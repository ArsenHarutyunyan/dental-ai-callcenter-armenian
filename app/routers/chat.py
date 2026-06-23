import re

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.agent import build_knowledge_context, process_message
from app.database import SessionLocal
from app.models import (
    Appointment,
    ChatMessage,
    DoctorSchedule,
    KnowledgeBase,
    Patient,
)

router = APIRouter(prefix="/chat", tags=["Chat"])

chat_sessions = {}


class ChatRequest(BaseModel):
    clinic_id: int
    session_id: str
    message: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def extract_phone_from_text(text: str):
    match = re.search(r"\+374\d{8}", text)
    return match.group() if match else None


def build_schedule_context(schedules):
    if not schedules:
        return "No available schedules"

    parts = []

    for schedule in schedules:
        parts.append(
            f"""
Schedule ID: {schedule.id}
Doctor ID: {schedule.doctor_id}
Date: {schedule.date}
Start: {schedule.start_time}
End: {schedule.end_time}
Status: {schedule.status}
"""
        )

    return "\n".join(parts)


def build_patient_context(patient, appointments):
    if not patient:
        return "No known patient"

    parts = [
        f"Patient ID: {patient.id}",
        f"Full name: {patient.full_name}",
        f"Phone: {patient.phone}",
        "Previous appointments:",
    ]

    if not appointments:
        parts.append("No previous appointments")
    else:
        for appointment in appointments:
            parts.append(
                f"""
Appointment ID: {appointment.id}
Complaint: {appointment.complaint}
Preferred time: {appointment.preferred_time}
Status: {appointment.status}
"""
            )

    return "\n".join(parts)


@router.get("/history/{session_id}")
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id)
        .all()
    )

    return messages


@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    db.add(
        ChatMessage(
            session_id=request.session_id,
            clinic_id=request.clinic_id,
            role="user",
            message=request.message,
        )
    )
    db.commit()

    session_data = chat_sessions.get(
        request.session_id,
        {
            "messages": [],
            "selected_schedule_id": None,
        },
    )

    session_data["messages"].append(request.message)
    combined_message = "\n".join(session_data["messages"])

    knowledge_items = (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.clinic_id == request.clinic_id)
        .all()
    )

    knowledge_context = build_knowledge_context(knowledge_items)

    available_schedules = (
        db.query(DoctorSchedule)
        .filter(DoctorSchedule.status == "available")
        .all()
    )

    schedule_context = build_schedule_context(available_schedules)

    phone_from_text = extract_phone_from_text(combined_message)

    existing_patient = None
    previous_appointments = []

    if phone_from_text:
        existing_patient = (
            db.query(Patient)
            .filter(Patient.phone == phone_from_text)
            .first()
        )

        if existing_patient:
            previous_appointments = (
                db.query(Appointment)
                .filter(Appointment.patient_id == existing_patient.id)
                .order_by(Appointment.id.desc())
                .limit(5)
                .all()
            )

    patient_context = build_patient_context(
        existing_patient,
        previous_appointments,
    )

    result = process_message(
        combined_message,
        knowledge_context,
        schedule_context,
        patient_context,
    )

    if result["type"] == "faq":
        bot_answer = result["answer"]

        db.add(
            ChatMessage(
                session_id=request.session_id,
                clinic_id=request.clinic_id,
                role="assistant",
                message=bot_answer,
            )
        )
        db.commit()

        chat_sessions[request.session_id] = session_data

        return {
            "status": "faq_answered",
            "answer": bot_answer,
        }

    if result["type"] == "schedule_query":
        bot_answer = result["answer"]

        session_data["selected_schedule_id"] = result.get("schedule_id")
        chat_sessions[request.session_id] = session_data

        db.add(
            ChatMessage(
                session_id=request.session_id,
                clinic_id=request.clinic_id,
                role="assistant",
                message=bot_answer,
            )
        )
        db.commit()

        return {
            "status": "schedule_answered",
            "answer": bot_answer,
            "schedule_id": result.get("schedule_id"),
        }

    data = result["data"]

    if existing_patient and not data.get("patient_name"):
        data["patient_name"] = existing_patient.full_name

    if existing_patient and not data.get("phone"):
        data["phone"] = existing_patient.phone

    missing = []

    if not data.get("patient_name"):
        missing.append("name")

    if not data.get("phone"):
        missing.append("phone")

    if not data.get("preferred_time"):
        missing.append("time")

    if missing:
        questions = []

        if "name" in missing:
            questions.append("Ձեր անունը")

        if "phone" in missing:
            questions.append("հեռախոսահամարը")

        if "time" in missing:
            questions.append("Ձեզ հարմար օրը և ժամը")

        bot_answer = "Խնդրում եմ նշեք " + ", ".join(questions) + "։"

        db.add(
            ChatMessage(
                session_id=request.session_id,
                clinic_id=request.clinic_id,
                role="assistant",
                message=bot_answer,
            )
        )
        db.commit()

        chat_sessions[request.session_id] = session_data

        return {
            "status": "missing_data",
            "missing": missing,
            "data": data,
            "answer": bot_answer,
        }

    schedule_id = data.get("schedule_id") or session_data.get("selected_schedule_id")

    if schedule_id:
        schedule = (
            db.query(DoctorSchedule)
            .filter(DoctorSchedule.id == schedule_id)
            .first()
        )

        if not schedule:
            return {"error": "Schedule not found"}

        if schedule.status != "available":
            return {"error": "Schedule already booked"}

        schedule.status = "booked"

    patient = (
        db.query(Patient)
        .filter(Patient.phone == data["phone"])
        .first()
    )

    if not patient:
        patient = Patient(
            full_name=data["patient_name"],
            phone=data["phone"],
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)

    appointment = Appointment(
        clinic_id=request.clinic_id,
        patient_id=patient.id,
        schedule_id=schedule_id,
        patient_name=data["patient_name"],
        phone=data["phone"],
        complaint=data.get("complaint") or "Չնշված գանգատ",
        preferred_time=data["preferred_time"],
        status="new",
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    bot_answer = (
        "Ձեր հայտը հաջողությամբ գրանցվել է։ "
        "Կլինիկայի ադմինիստրատորը կկապվի Ձեզ հետ։"
    )

    db.add(
        ChatMessage(
            session_id=request.session_id,
            clinic_id=request.clinic_id,
            role="assistant",
            message=bot_answer,
        )
    )
    db.commit()

    chat_sessions.pop(request.session_id, None)

    return {
        "status": "appointment_created",
        "appointment_id": appointment.id,
        "patient_id": patient.id,
        "schedule_id": schedule_id,
        "data": data,
        "answer": bot_answer,
    }