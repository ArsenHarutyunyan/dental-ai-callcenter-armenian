from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.agent import build_knowledge_context, process_message
from app.database import SessionLocal
from app.models import Appointment, ChatMessage, KnowledgeBase

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
    # 1. Save user message to PostgreSQL
    db.add(
        ChatMessage(
            session_id=request.session_id,
            clinic_id=request.clinic_id,
            role="user",
            message=request.message,
        )
    )
    db.commit()

    # 2. Keep temporary in-memory session
    session_messages = chat_sessions.get(request.session_id, [])
    session_messages.append(request.message)
    chat_sessions[request.session_id] = session_messages

    combined_message = "\n".join(session_messages)

    # 3. Load clinic knowledge
    knowledge_items = (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.clinic_id == request.clinic_id)
        .all()
    )

    knowledge_context = build_knowledge_context(knowledge_items)

    # 4. Process message with AI agent
    result = process_message(
        combined_message,
        knowledge_context,
    )

    # 5. FAQ answer
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

    # 6. Appointment missing data
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

    # 7. Create appointment
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

    # 8. Clear session after successful appointment
    chat_sessions.pop(request.session_id, None)

    return {
        "status": "appointment_created",
        "appointment_id": appointment.id,
        "data": data,
        "answer": bot_answer,
    }