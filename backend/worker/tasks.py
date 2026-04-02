from uuid import UUID
from sqlalchemy.orm import Session
from worker.celery_app import celery_app
from app.database import SessionLocal
from app import models
from app.config import get_llm_router
from app.services.chapter_generator import generate_chapter
from app.services.feedback_handler import infer_feedback_scope


@celery_app.task(bind=True, max_retries=3)
def generate_chapter_task(self, novel_id: str, chapter_number: int):
    """Generate a single chapter for a novel."""
    db: Session = SessionLocal()
    try:
        novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
        if not novel:
            raise ValueError(f"Novel {novel_id} not found")

        # Get previous chapter summary
        prev_chapter = (
            db.query(models.Chapter)
            .filter(models.Chapter.novel_id == UUID(novel_id))
            .filter(models.Chapter.number == chapter_number - 1)
            .first()
        )
        prev_summary = prev_chapter.summary if prev_chapter else ""

        # Get locked chapters for constraints
        locked_before = (
            db.query(models.Chapter)
            .filter(models.Chapter.novel_id == UUID(novel_id))
            .filter(models.Chapter.number < chapter_number)
            .filter(models.Chapter.locked == True)
            .order_by(models.Chapter.number.desc())
            .first()
        )
        locked_after = (
            db.query(models.Chapter)
            .filter(models.Chapter.novel_id == UUID(novel_id))
            .filter(models.Chapter.number > chapter_number)
            .filter(models.Chapter.locked == True)
            .order_by(models.Chapter.number.asc())
            .first()
        )

        locked_before_summary = locked_before.summary if locked_before else None
        locked_after_constraint = f"Must lead into: {locked_after.summary[:200]}..." if locked_after else None

        # Generate chapter
        router = get_llm_router()
        config = router.get_config("chapter")
        from app.llm.openai_client import OpenAICompatibleClient
        client = OpenAICompatibleClient()

        title, content = generate_chapter(
            client,
            novel.settings,
            prev_summary,
            chapter_number,
            config,
            locked_before_summary,
            locked_after_constraint
        )

        # Save chapter
        chapter = models.Chapter(
            novel_id=UUID(novel_id),
            number=chapter_number,
            title=title,
            content=content,
            status="draft",
            summary=content[:500] if content else ""
        )
        db.add(chapter)
        db.commit()

        return {"chapter_id": str(chapter.id), "status": "completed"}
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def process_feedback_task(self, feedback_id: str):
    """Process feedback to infer its scope."""
    db: Session = SessionLocal()
    try:
        feedback = db.query(models.Feedback).filter(models.Feedback.id == UUID(feedback_id)).first()
        if not feedback:
            raise ValueError(f"Feedback {feedback_id} not found")

        # Get chapter summary if feedback is for a specific chapter
        chapter_summary = None
        if feedback.chapter_id:
            chapter = db.query(models.Chapter).filter(models.Chapter.id == feedback.chapter_id).first()
            if chapter:
                chapter_summary = chapter.summary

        # Get novel settings
        novel = db.query(models.Novel).filter(models.Novel.id == feedback.novel_id).first()
        if not novel:
            raise ValueError(f"Novel for feedback {feedback_id} not found")

        # Infer scope
        router = get_llm_router()
        config = router.get_config("feedback")
        from app.llm.openai_client import OpenAICompatibleClient
        client = OpenAICompatibleClient()

        scope = infer_feedback_scope(
            client,
            novel.settings,
            chapter_summary,
            feedback.content,
            config
        )

        feedback.inferred_scope = scope
        db.commit()

        return {"feedback_id": feedback_id, "inferred_scope": scope}
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
    finally:
        db.close()
