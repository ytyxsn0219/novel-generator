from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/novels/{novel_id}/chapters", tags=["chapters"])

@router.get("", response_model=list[schemas.ChapterResponse])
def list_chapters(novel_id: str, db: Session = Depends(get_db)):
    return db.query(models.Chapter).filter(models.Chapter.novel_id == UUID(novel_id)).order_by(models.Chapter.number).all()
