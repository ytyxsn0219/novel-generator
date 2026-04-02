from sqlalchemy import text
from app.database import engine


def test_engine_connects():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
