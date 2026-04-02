import os
from app.config import Settings


def test_settings_loads_database_url():
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
    settings = Settings()
    assert settings.database_url == "postgresql://user:pass@localhost/db"
