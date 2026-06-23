from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Appointment, DoctorSchedule
from app.schemas import AppointmentCreate, AppointmentUpdate

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_appointment(
    request: AppointmentCreate,
    db: Session = Depends(get_db),
):
    if request.schedule_id:
        schedule = (
            db.query(DoctorSchedule)
            .filter(DoctorSchedule.id == request.schedule_id)
            .first()
        )

        if not schedule:
            return {"error": "Schedule not found"}

        if schedule.status != "available":
            return {"error": "Schedule is not available"}

        schedule.status = "booked"

    appointment = Appointment(
        clinic_id=request.clinic_id,
        patient_id=request.patient_id,
        doctor_id=request.doctor_id,
        service_id=request.service_id,
        schedule_id=request.schedule_id,
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
def get_appointments(
    clinic_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Appointment)

    if clinic_id:
        query = query.filter(Appointment.clinic_id == clinic_id)

    return query.all()


@router.get("/{appointment_id}")
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        return {"error": "Appointment not found"}

    return appointment


@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    request: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        return {"error": "Appointment not found"}

    appointment.patient_name = request.patient_name
    appointment.phone = request.phone
    appointment.complaint = request.complaint
    appointment.preferred_time = request.preferred_time
    appointment.status = request.status

    db.commit()
    db.refresh(appointment)

    return appointment


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        return {"error": "Appointment not found"}

    if appointment.schedule_id:
        schedule = (
            db.query(DoctorSchedule)
            .filter(DoctorSchedule.id == appointment.schedule_id)
            .first()
        )

        if schedule:
            schedule.status = "available"

    db.delete(appointment)
    db.commit()

    return {
        "status": "deleted",
        "appointment_id": appointment_id,
    }