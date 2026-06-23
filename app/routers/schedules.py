from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DoctorSchedule
from app.schemas import (DoctorScheduleCreate,DoctorScheduleUpdate,)

router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_schedule(
    request: DoctorScheduleCreate,
    db: Session = Depends(get_db),
):
    schedule = DoctorSchedule(
        doctor_id=request.doctor_id,
        date=request.date,
        start_time=request.start_time,
        end_time=request.end_time,
    )

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


@router.get("/")
def get_schedules(
    db: Session = Depends(get_db),
):
    return db.query(
        DoctorSchedule
    ).all()
    
@router.put("/{schedule_id}")
def update_schedule(
    schedule_id: int,
    request: DoctorScheduleUpdate,
    db: Session = Depends(get_db),
):
    schedule = (
        db.query(DoctorSchedule)
        .filter(
            DoctorSchedule.id == schedule_id
        )
        .first()
    )

    if not schedule:
        return {
            "error": "Schedule not found"
        }

    schedule.status = request.status

    db.commit()
    db.refresh(schedule)

    return schedule

@router.get("/available")
def get_available_slots(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(DoctorSchedule)
        .filter(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.status == "available"
        )
        .all()
    )