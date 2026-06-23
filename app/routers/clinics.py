from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    Appointment,
    Clinic,
    Doctor,
    DoctorSchedule,
    Patient,
    Service,
)
from app.schemas import ClinicCreate, ClinicUpdate

router = APIRouter(prefix="/clinics", tags=["Clinics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_clinic(request: ClinicCreate, db: Session = Depends(get_db)):
    clinic = Clinic(
        name=request.name,
        address=request.address,
        phone=request.phone,
    )

    db.add(clinic)
    db.commit()
    db.refresh(clinic)

    return clinic


@router.get("/")
def get_clinics(db: Session = Depends(get_db)):
    return db.query(Clinic).all()


@router.get("/{clinic_id}/dashboard")
def get_clinic_dashboard(
    clinic_id: int,
    db: Session = Depends(get_db),
):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()

    if not clinic:
        return {"error": "Clinic not found"}

    doctors = db.query(Doctor).filter(Doctor.clinic_id == clinic_id).all()
    services = db.query(Service).filter(Service.clinic_id == clinic_id).all()
    appointments = (
        db.query(Appointment)
        .filter(Appointment.clinic_id == clinic_id)
        .order_by(Appointment.id.desc())
        .all()
    )

    doctor_ids = [doctor.id for doctor in doctors]

    schedules = []

    if doctor_ids:
        schedules = (
            db.query(DoctorSchedule)
            .filter(DoctorSchedule.doctor_id.in_(doctor_ids))
            .all()
        )

    patient_ids = {
        appointment.patient_id
        for appointment in appointments
        if appointment.patient_id
    }

    patients = []

    if patient_ids:
        patients = (
            db.query(Patient)
            .filter(Patient.id.in_(patient_ids))
            .all()
        )

    return {
        "clinic": clinic,
        "stats": {
            "doctors_count": len(doctors),
            "services_count": len(services),
            "patients_count": len(patients),
            "appointments_count": len(appointments),
            "schedules_count": len(schedules),
        },
        "doctors": doctors,
        "services": services,
        "patients": patients,
        "appointments": appointments,
        "schedules": schedules,
    }


@router.get("/{clinic_id}")
def get_clinic(clinic_id: int, db: Session = Depends(get_db)):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()

    if not clinic:
        return {"error": "Clinic not found"}

    return clinic


@router.put("/{clinic_id}")
def update_clinic(
    clinic_id: int,
    request: ClinicUpdate,
    db: Session = Depends(get_db),
):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()

    if not clinic:
        return {"error": "Clinic not found"}

    clinic.name = request.name
    clinic.address = request.address
    clinic.phone = request.phone

    db.commit()
    db.refresh(clinic)

    return clinic


@router.delete("/{clinic_id}")
def delete_clinic(
    clinic_id: int,
    db: Session = Depends(get_db),
):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()

    if not clinic:
        return {"error": "Clinic not found"}

    db.delete(clinic)
    db.commit()

    return {
        "status": "deleted",
        "clinic_id": clinic_id,
    }