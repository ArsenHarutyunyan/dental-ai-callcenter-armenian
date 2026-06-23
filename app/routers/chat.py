from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.agent import process_message
from app.database import SessionLocal
from app.models import Appointment

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    clinic_id: int
    message: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    result = process_message(request.message)

    if not result["ready"]:
        return {
            "status": "missing_data",
            "missing": result["missing"],
            "data": result["data"],
            "answer": "Խնդրում եմ նշեք Ձեր անունը, հեռախոսահամարը և հարմար ժամը։"
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

    return {
        "status": "appointment_created",
        "appointment_id": appointment.id,
        "data": data,
        "answer": "Ձեր հայտը հաջողությամբ գրանցվել է։ Կլինիկայի ադմինիստրատորը կկապվի Ձեզ հետ։"
    }