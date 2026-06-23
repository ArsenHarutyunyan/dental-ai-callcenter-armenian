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
        clinic_id=request.clinic_id,
        patient_id=request.patient_id,
        doctor_id=request.doctor_id,
        service_id=request.service_id,
        patient_name=request.patient_name,
        phone=request.phone,
        complaint=request.complaint,
        preferred_time=request.preferred_time,
        status=request.status,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


@router.get("/")
def get_appointments(db: Session = Depends(get_db)):
    return db.query(Appointment).all()


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