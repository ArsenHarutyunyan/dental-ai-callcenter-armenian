from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Doctor
from app.schemas import DoctorCreate

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_doctor(request: DoctorCreate, db: Session = Depends(get_db)):
    doctor = Doctor(
        clinic_id=request.clinic_id,
        full_name=request.full_name,
        specialization=request.specialization,
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


@router.get("/")
def get_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()


@router.get("/{doctor_id}")
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:
        return {"error": "Doctor not found"}

    return doctor