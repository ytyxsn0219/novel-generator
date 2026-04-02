from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/novels", tags=["novels"])


@router.post("", status_code=201, response_model=schemas.NovelResponse)
def create_novel(payload: schemas.NovelCreate, db: Session = Depends(get_db)):
    novel = models.Novel(title=payload.title, theme=payload.theme)
    db.add(novel)
    db.commit()
    db.refresh(novel)
    return novel


@router.get("/{novel_id}", response_model=schemas.NovelResponse)
def get_novel(novel_id: str, db: Session = Depends(get_db)):
    from uuid import UUID
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel
