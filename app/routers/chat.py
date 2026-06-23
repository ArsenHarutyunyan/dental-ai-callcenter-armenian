from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.agent import process_message
from app.database import SessionLocal
from app.models import Appointment, ChatMessage

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


@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    session_messages = chat_sessions.get(request.session_id, [])
    session_messages.append(request.message)
    db.add(
    ChatMessage(
        session_id=request.session_id,
        clinic_id=request.clinic_id,
        role="user",
        message=request.message,
        )
    )
    db.commit()
    chat_sessions[request.session_id] = session_messages

    combined_message = "\n".join(session_messages)

    result = process_message(combined_message)

    if not result["ready"]:
        missing = result["missing"]

        questions = []

        if "name" in missing:
            questions.append("Ձեր անունը")

        if "phone" in missing:
            questions.append("հեռախոսահամարը")

        if "time" in missing:
            questions.append("Ձեզ հարմար օրը և ժամը")

        return {
            "status": "missing_data",
            "missing": missing,
            "data": result["data"],
            "answer": "Խնդրում եմ նշեք " + ", ".join(questions) + "։",
        }

    data = result["data"]

    appointment = Appointment(
        clinic_id=request.clinic_id,
        patient_name=data["patient_name"],
        phone=data["phone"],
        complaint=data["complaint"],
        preferred_time=data["preferred_time"],
        status="new",
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    chat_sessions.pop(request.session_id, None)
    bot_answer = (
    "Խնդրում եմ նշեք "
    + ", ".join(questions)
    + "։"
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
    

    return {
        "status": "appointment_created",
        "appointment_id": appointment.id,
        "data": data,
        "answer": bot_answer}