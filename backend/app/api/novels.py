from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.config import get_db_llm_config
from app.services.settings_generator import generate_settings
from app.llm.base import ModelConfig
from app.llm.openai_client import OpenAICompatibleClient

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

    # Get config from database
    db_config = get_db_llm_config(db)

    # Create ModelConfig
    config = ModelConfig(
        provider=db_config["provider"],
        model=db_config["model"],
        api_key=db_config["api_key"],
        base_url=db_config["base_url"],
        temperature=db_config["temperature"],
        max_tokens=db_config["max_tokens"]
    )

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
