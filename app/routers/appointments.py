from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Appointment
from app.schemas import AppointmentCreate

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_appointment(request: AppointmentCreate, db: Session = Depends(get_db)):
    appointment = Appointment(
        patient_name=request.patient_name,
        phone=request.phone,
        complaint=request.complaint,
        preferred_time=request.preferred_time,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {
        "id": appointment.id,
        "patient_name": appointment.patient_name,
        "phone": appointment.phone,
        "complaint": appointment.complaint,
        "preferred_time": appointment.preferred_time,
        "status": "created",
    }


@router.get("/")
def get_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).all()
    return appointments


@router.get("/{appointment_id}")
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        return {"error": "Appointment not found"}

    return appointment