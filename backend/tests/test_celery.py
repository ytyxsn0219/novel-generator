from worker.celery_app import celery_app

def test_celery_app_name():
    assert celery_app.main == "novel_generator"
