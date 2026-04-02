from worker.celery_app import celery_app
from worker.tasks import generate_chapter_task

def test_celery_app_name():
    assert celery_app.main == "novel_generator"

def test_generate_chapter_task_signature():
    assert generate_chapter_task.name == "worker.tasks.generate_chapter_task"
