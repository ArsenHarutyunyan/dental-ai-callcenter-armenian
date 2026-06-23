from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Patient
from app.schemas import PatientCreate

router = APIRouter(prefix="/patients", tags=["Patients"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_patient(request: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(
        full_name=request.full_name,
        phone=request.phone,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


@router.get("/")
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()


@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        return {"error": "Patient not found"}

    return patient