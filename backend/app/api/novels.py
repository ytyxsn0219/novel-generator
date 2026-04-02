from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.config import get_llm_router
from app.services.settings_generator import generate_settings

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
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel


@router.post("/{novel_id}/settings", status_code=200, response_model=schemas.NovelResponse)
def generate_novel_settings(novel_id: str, db: Session = Depends(get_db)):
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    # Generate settings using LLM
    router = get_llm_router()
    config = router.get_config("settings")
    from app.llm.openai_client import OpenAICompatibleClient
    client = OpenAICompatibleClient()

    settings = generate_settings(client, novel.theme, config)
    novel.settings = settings
    db.commit()
    db.refresh(novel)
    return novel


@router.post("/{novel_id}/settings/confirm", status_code=200, response_model=schemas.NovelResponse)
def confirm_settings(novel_id: str, payload: schemas.SettingsConfirm, db: Session = Depends(get_db)):
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    novel.settings = payload.settings
    novel.status = "serializing"
    db.commit()
    db.refresh(novel)
    return novel
