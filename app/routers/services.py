from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Service
from app.schemas import ServiceCreate, ServiceUpdate

router = APIRouter(prefix="/services", tags=["Services"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_service(request: ServiceCreate, db: Session = Depends(get_db)):
    service = Service(
        clinic_id=request.clinic_id,
        name=request.name,
        description=request.description,
        price=request.price,
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service


@router.get("/")
def get_services(db: Session = Depends(get_db)):
    return db.query(Service).all()


@router.get("/{service_id}")
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        return {"error": "Service not found"}

    return service

@router.put("/{service_id}")
def update_service(
    service_id: int,
    request: ServiceUpdate,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        return {"error": "Service not found"}

    service.clinic_id = request.clinic_id
    service.name = request.name
    service.description = request.description
    service.price = request.price

    db.commit()
    db.refresh(service)

    return service


@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        return {"error": "Service not found"}

    db.delete(service)
    db.commit()

    return {
        "status": "deleted",
        "service_id": service_id
    }