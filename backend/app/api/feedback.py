from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from worker.tasks import process_feedback_task

router = APIRouter(prefix="/novels/{novel_id}/feedbacks", tags=["feedbacks"])


@router.post("", status_code=201, response_model=schemas.FeedbackResponse)
def create_feedback(novel_id: str, payload: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    # Verify novel exists
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    fb = models.Feedback(
        novel_id=UUID(novel_id),
        chapter_id=payload.chapter_id,
        content=payload.content
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    # Trigger async task to process feedback
    process_feedback_task.delay(str(fb.id))

    return fb
