from uuid import UUID
from app.models import Novel, Chapter, GenerationJob, Feedback

def test_novel_instance_creation():
    novel = Novel(title="Test Novel", theme="A hero's journey")
    assert novel.title == "Test Novel"
    assert isinstance(novel.id, UUID)
