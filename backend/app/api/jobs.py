from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/novels/{novel_id}/jobs", tags=["jobs"])

@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job(novel_id: str, job_id: str, db: Session = Depends(get_db)):
    job = db.query(models.GenerationJob).filter(
        models.GenerationJob.novel_id == UUID(novel_id),
        models.GenerationJob.id == UUID(job_id)
    ).first()
    return job
