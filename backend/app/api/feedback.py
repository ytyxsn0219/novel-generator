from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/novels/{novel_id}/feedbacks", tags=["feedbacks"])

@router.post("", status_code=201, response_model=schemas.FeedbackResponse)
def create_feedback(novel_id: str, payload: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    fb = models.Feedback(
        novel_id=UUID(novel_id),
        chapter_id=payload.chapter_id,
        content=payload.content
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
