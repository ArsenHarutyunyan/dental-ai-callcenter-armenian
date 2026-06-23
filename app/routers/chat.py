from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.agent import build_knowledge_context, process_message
from app.database import SessionLocal
from app.models import Appointment, ChatMessage, KnowledgeBase, DoctorSchedule

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

    session_messages = chat_sessions.get(request.session_id, [])
    session_messages.append(request.message)
    chat_sessions[request.session_id] = session_messages

    combined_message = "\n".join(session_messages)

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

    result = process_message(
        combined_message,
        knowledge_context,
        schedule_context,
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

        return {
            "status": "faq_answered",
            "answer": bot_answer,
        }

    if result["type"] == "schedule_query":
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

        return {
            "status": "schedule_answered",
            "answer": bot_answer,
            "schedule_id": result.get("schedule_id")
        }

    if not result["ready"]:
        missing = result["missing"]

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

        return {
            "status": "missing_data",
            "missing": missing,
            "data": result["data"],
            "answer": bot_answer,
        }

    data = result["data"]
    schedule_id = data.get("schedule_id")
    appointment = Appointment(
        schedule_id=schedule_id,
        clinic_id=request.clinic_id,
        patient_name=data["patient_name"],
        phone=data["phone"],
        complaint=data["complaint"],
        preferred_time=data["preferred_time"],
        status="new",
    )
    if schedule_id:
        schedule = (
            db.query(DoctorSchedule).filter(
            DoctorSchedule.id == schedule_id
            ).first()
        )

    if schedule:
        schedule.status = "booked"

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
        "data": data,
        "answer": bot_answer,
    }