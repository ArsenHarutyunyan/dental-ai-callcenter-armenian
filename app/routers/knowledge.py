from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import KnowledgeBase
from app.schemas import KnowledgeBaseCreate

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Base"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_knowledge(
    request: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
):
    item = KnowledgeBase(
        clinic_id=request.clinic_id,
        category=request.category,
        title=request.title,
        content=request.content,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get("/")
def get_knowledge(
    clinic_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.clinic_id == clinic_id
        )
        .all()
    )