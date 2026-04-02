from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from worker.tasks import generate_chapter_task

router = APIRouter(prefix="/novels/{novel_id}/jobs", tags=["jobs"])


@router.post("", status_code=201, response_model=schemas.JobResponse)
def create_job(novel_id: str, payload: schemas.JobCreate, db: Session = Depends(get_db)):
    # Verify novel exists
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    # Create job record
    job = models.GenerationJob(
        novel_id=UUID(novel_id),
        job_type=payload.job_type,
        start_chapter=payload.start_chapter,
        end_chapter=payload.end_chapter,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Queue tasks for each chapter
    for chapter_num in range(payload.start_chapter, payload.end_chapter + 1):
        generate_chapter_task.delay(novel_id, chapter_num)

    return job


@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job(novel_id: str, job_id: str, db: Session = Depends(get_db)):
    job = db.query(models.GenerationJob).filter(
        models.GenerationJob.novel_id == UUID(novel_id),
        models.GenerationJob.id == UUID(job_id)
    ).first()
    return job
