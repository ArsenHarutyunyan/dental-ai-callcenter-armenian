from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Clinic
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
        "clinic_id": clinic_id
    }