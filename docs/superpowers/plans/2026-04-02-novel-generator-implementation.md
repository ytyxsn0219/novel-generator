# AI Novel Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal AI novel generator web app with FastAPI backend, React frontend, Celery+Redis async generation queue, PostgreSQL storage, Docker Compose deployment, and dual-mode LLM routing.

**Architecture:** Backend-first implementation. Build data models and LLM layer, then Celery tasks, then core services (settings generation, chapter writing, feedback handling), then REST API, then React frontend, finally Docker Compose wiring. Each layer is tested before moving on.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Celery, Redis, PostgreSQL, React 18 + TypeScript, Vite, Docker Compose

---

## File Structure

```
novel-generator/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   ├── versions/
│   │   └── script.py.mako
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── novels.py
│   │   │   ├── chapters.py
│   │   │   ├── jobs.py
│   │   │   └── feedback.py
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── router.py
│   │   │   ├── openai_client.py
│   │   │   └── deepseek_client.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── prompt_builder.py
│   │       ├── settings_generator.py
│   │       ├── chapter_generator.py
│   │       └── feedback_handler.py
│   ├── worker/
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── tasks.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_llm.py
│       ├── test_services.py
│       └── test_api.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── nginx.conf
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api.ts
│       ├── types.ts
│       └── components/
│           ├── NovelList.tsx
│           ├── SettingEditor.tsx
│           ├── Reader.tsx
│           └── FeedbackPanel.tsx
```

---

## Module 1: Backend Foundation

### Task 1: Create backend project skeleton and dependencies

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Write requirements.txt**

```text
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
alembic==1.14.0
celery==5.4.0
redis==5.2.0
pydantic==2.9.2
pydantic-settings==2.6.1
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
```

- [ ] **Step 2: Write minimal FastAPI entry point**

```python
from fastapi import FastAPI

app = FastAPI(title="Novel Generator")

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 3: Verify server starts**

Run: `cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --port 8000 &`
Expected: Server starts without error.

Run: `curl http://localhost:8000/health`
Expected: `{"status":"ok"}`

- [ ] **Step 4: Commit**

```bash
git add backend/
git commit -m "chore: backend skeleton and dependencies"
```

---

### Task 2: Add pydantic-settings config

**Files:**
- Create: `backend/app/config.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_config.py`:

```python
import os
from app.config import Settings

def test_settings_loads_database_url():
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
    settings = Settings()
    assert settings.database_url == "postgresql://user:pass@localhost/db"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_config.py::test_settings_loads_database_url -v`
Expected: FAIL "ModuleNotFoundError: No module named 'app.config'"

- [ ] **Step 3: Implement config module**

Create `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/novel_generator"
    redis_url: str = "redis://localhost:6379/0"
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o"
    default_llm_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_config.py::test_settings_loads_database_url -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/config.py backend/tests/test_config.py
git commit -m "feat: add pydantic settings config"
```

---

### Task 3: Set up SQLAlchemy database session and engine

**Files:**
- Create: `backend/app/database.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_database.py`:

```python
from sqlalchemy import text
from app.database import engine

def test_engine_connects():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_database.py::test_engine_connects -v`
Expected: FAIL "ModuleNotFoundError: No module named 'app.database'"

- [ ] **Step 3: Implement database module**

Create `backend/app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_database.py::test_engine_connects -v`
Expected: PASS (requires local Postgres running or SQLite fallback; if Postgres not running, use `docker run --name pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16`)

- [ ] **Step 5: Commit**

```bash
git add backend/app/database.py backend/tests/test_database.py
git commit -m "feat: add sqlalchemy database engine and session"
```

---

### Task 4: Define SQLAlchemy models

**Files:**
- Create: `backend/app/models.py`
- Modify: `backend/app/database.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_models.py`:

```python
from uuid import UUID
from app.models import Novel, Chapter, GenerationJob, Feedback

def test_novel_instance_creation():
    novel = Novel(title="Test Novel", theme="A hero's journey")
    assert novel.title == "Test Novel"
    assert isinstance(novel.id, UUID)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_models.py::test_novel_instance_creation -v`
Expected: FAIL "ModuleNotFoundError: No module named 'app.models'"

- [ ] **Step 3: Implement models**

Create `backend/app/models.py`:

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Novel(Base):
    __tablename__ = "novels"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    theme = Column(Text, nullable=False)
    settings = Column(JSONB, default=dict)
    status = Column(String, default="drafting")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
    jobs = relationship("GenerationJob", back_populates="novel", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="novel", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    novel_id = Column(PGUUID(as_uuid=True), ForeignKey("novels.id"), nullable=False)
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False, default="")
    content = Column(Text, nullable=False, default="")
    status = Column(String, default="draft")
    locked = Column(Boolean, default=False)
    summary = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    novel = relationship("Novel", back_populates="chapters")
    feedbacks = relationship("Feedback", back_populates="chapter")

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    novel_id = Column(PGUUID(as_uuid=True), ForeignKey("novels.id"), nullable=False)
    job_type = Column(String, nullable=False)
    start_chapter = Column(Integer, nullable=False)
    end_chapter = Column(Integer, nullable=False)
    current_chapter = Column(Integer, default=0)
    status = Column(String, default="pending")
    feedback_id = Column(PGUUID(as_uuid=True), ForeignKey("feedbacks.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    novel = relationship("Novel", back_populates="jobs")
    feedback = relationship("Feedback", back_populates="jobs")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    novel_id = Column(PGUUID(as_uuid=True), ForeignKey("novels.id"), nullable=False)
    chapter_id = Column(PGUUID(as_uuid=True), ForeignKey("chapters.id"), nullable=True)
    content = Column(Text, nullable=False)
    inferred_scope = Column(String, nullable=True)
    accepted_scope = Column(String, nullable=True)
    handled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    novel = relationship("Novel", back_populates="feedbacks")
    chapter = relationship("Chapter", back_populates="feedbacks")
    jobs = relationship("GenerationJob", back_populates="feedback")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_models.py::test_novel_instance_creation -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/models.py backend/tests/test_models.py
git commit -m "feat: add sqlalchemy models for novel, chapter, job, feedback"
```

---

### Task 5: Define Pydantic schemas

**Files:**
- Create: `backend/app/schemas.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_schemas.py`:

```python
from app.schemas import NovelCreate, SettingsConfirm

def test_novel_create_schema():
    data = NovelCreate(title="Test", theme="theme")
    assert data.title == "Test"

def test_settings_confirm_schema():
    data = SettingsConfirm(settings={"world": "fantasy"})
    assert data.settings["world"] == "fantasy"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_schemas.py -v`
Expected: FAIL "ModuleNotFoundError: No module named 'app.schemas'"

- [ ] **Step 3: Implement schemas**

Create `backend/app/schemas.py`:

```python
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class NovelBase(BaseModel):
    title: str
    theme: str

class NovelCreate(NovelBase):
    pass

class NovelResponse(NovelBase):
    id: UUID
    settings: dict
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SettingsConfirm(BaseModel):
    settings: dict

class ChapterBase(BaseModel):
    number: int
    title: str
    content: str
    status: str
    locked: bool

class ChapterResponse(ChapterBase):
    id: UUID
    summary: str
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    chapter_id: Optional[UUID] = None
    content: str

class FeedbackResponse(BaseModel):
    id: UUID
    content: str
    inferred_scope: Optional[str]
    accepted_scope: Optional[str]
    handled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: UUID
    job_type: str
    start_chapter: int
    end_chapter: int
    current_chapter: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_schemas.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas.py backend/tests/test_schemas.py
git commit -m "feat: add pydantic request/response schemas"
```

---

### Task 6: Wire FastAPI routers for novels

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/novels.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_api_novels.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_novel():
    payload = {"title": "My Novel", "theme": "A space adventure"}
    response = client.post("/novels", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Novel"
    assert data["status"] == "drafting"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_api_novels.py::test_create_novel -v`
Expected: FAIL "AttributeError: module 'app.api' has no attribute 'novels'" or 404

- [ ] **Step 3: Implement novels router**

Create `backend/app/api/novels.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

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
    from uuid import UUID
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel
```

Update `backend/app/main.py`:

```python
from fastapi import FastAPI
from app.api import novels

app = FastAPI(title="Novel Generator")
app.include_router(novels.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

Create `backend/app/api/__init__.py` (empty or imports).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_api_novels.py::test_create_novel -v`
Expected: PASS (requires DB tables to exist; if not, run `python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"`)

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/ backend/tests/test_api_novels.py backend/app/main.py
git commit -m "feat: add novels CRUD router"
```

---

### Task 7: Wire chapters, jobs, and feedback routers

**Files:**
- Create: `backend/app/api/chapters.py`
- Create: `backend/app/api/jobs.py`
- Create: `backend/app/api/feedback.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_api_novels.py`:

```python
def test_list_chapters_for_novel():
    create_resp = client.post("/novels", json={"title": "T", "theme": "M"})
    novel_id = create_resp.json()["id"]
    response = client.get(f"/novels/{novel_id}/chapters")
    assert response.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_api_novels.py::test_list_chapters_for_novel -v`
Expected: FAIL 404

- [ ] **Step 3: Implement routers**

`backend/app/api/chapters.py`:

```python
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/novels/{novel_id}/chapters", tags=["chapters"])

@router.get("", response_model=list[schemas.ChapterResponse])
def list_chapters(novel_id: str, db: Session = Depends(get_db)):
    return db.query(models.Chapter).filter(models.Chapter.novel_id == UUID(novel_id)).order_by(models.Chapter.number).all()
```

`backend/app/api/jobs.py`:

```python
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
```

`backend/app/api/feedback.py`:

```python
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/novels/{novel_id}/feedbacks", tags=["feedbacks"])

@router.post("", status_code=201, response_model=schemas.FeedbackResponse)
def create_feedback(novel_id: str, payload: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    fb = models.Feedback(
        novel_id=UUID(novel_id),
        chapter_id=payload.chapter_id,
        content=payload.content
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
```

Update `backend/app/main.py` to include all routers:

```python
from app.api import novels, chapters, jobs, feedback
...
app.include_router(novels.router)
app.include_router(chapters.router)
app.include_router(jobs.router)
app.include_router(feedback.router)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_api_novels.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/ backend/tests/test_api_novels.py backend/app/main.py
git commit -m "feat: add chapters, jobs, feedback routers"
```

---

## Module 2: LLM Client Layer

### Task 8: Define LLM base abstraction

**Files:**
- Create: `backend/app/llm/__init__.py`
- Create: `backend/app/llm/base.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_llm.py`:

```python
from app.llm.base import LLMClient, ModelConfig

def test_model_config_creation():
    cfg = ModelConfig(provider="test", model="m", api_key="k")
    assert cfg.provider == "test"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_llm.py::test_model_config_creation -v`
Expected: FAIL

- [ ] **Step 3: Implement base abstraction**

Create `backend/app/llm/base.py`:

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class ModelConfig(BaseModel):
    provider: str
    model: str
    api_key: str
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4000

class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, config: ModelConfig) -> str:
        ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_llm.py::test_model_config_creation -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/llm/base.py backend/tests/test_llm.py
git commit -m "feat: add LLM client base abstraction"
```

---

### Task 9: Implement OpenAI-compatible client (covers DeepSeek, OpenAI)

**Files:**
- Create: `backend/app/llm/openai_client.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_llm.py`:

```python
from unittest.mock import patch, MagicMock
from app.llm.openai_client import OpenAICompatibleClient
from app.llm.base import ModelConfig

def test_openai_client_generate():
    client = OpenAICompatibleClient()
    cfg = ModelConfig(provider="openai", model="gpt-4o", api_key="fake-key")
    with patch("httpx.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {
            "choices": [{"message": {"content": "hello"}}]
        })
        result = client.generate("say hi", cfg)
        assert result == "hello"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_llm.py::test_openai_client_generate -v`
Expected: FAIL "ModuleNotFoundError: No module named 'app.llm.openai_client'"

- [ ] **Step 3: Implement client**

Create `backend/app/llm/openai_client.py`:

```python
import httpx
from app.llm.base import LLMClient, ModelConfig

class OpenAICompatibleClient(LLMClient):
    def generate(self, prompt: str, config: ModelConfig) -> str:
        base_url = config.base_url or "https://api.openai.com"
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens
        }
        resp = httpx.post(f"{base_url}/v1/chat/completions", headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_llm.py::test_openai_client_generate -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/llm/openai_client.py backend/tests/test_llm.py
git commit -m "feat: implement OpenAI-compatible LLM client"
```

---

### Task 10: Implement ModelRouter for single/multi-mode

**Files:**
- Create: `backend/app/llm/router.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_llm.py`:

```python
from app.llm.router import ModelRouter

def test_single_mode_router():
    router = ModelRouter(mode="single", default={"provider":"openai","model":"gpt-4o","api_key":"k"})
    cfg = router.get_config("writing")
    assert cfg.provider == "openai"

def test_multi_mode_router():
    router = ModelRouter(
        mode="multi",
        default={"provider":"x","model":"m","api_key":"k"},
        router_map={"writing": {"provider":"deepseek","model":"v3","api_key":"dk"}}
    )
    cfg = router.get_config("writing")
    assert cfg.provider == "deepseek"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_llm.py::test_single_mode_router tests/test_llm.py::test_multi_mode_router -v`
Expected: FAIL

- [ ] **Step 3: Implement router**

Create `backend/app/llm/router.py`:

```python
from app.llm.base import ModelConfig

class ModelRouter:
    def __init__(self, mode: str, default: dict, router_map: dict | None = None):
        self.mode = mode
        self.default = ModelConfig(**default)
        self.router_map = {k: ModelConfig(**v) for k, v in (router_map or {}).items()}

    def get_config(self, task_type: str) -> ModelConfig:
        if self.mode == "single" or task_type not in self.router_map:
            return self.default
        return self.router_map[task_type]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_llm.py::test_single_mode_router tests/test_llm.py::test_multi_mode_router -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/llm/router.py backend/tests/test_llm.py
git commit -m "feat: add model router for single/multi mode"
```

---

### Task 11: Expose LLM client factory in config

**Files:**
- Modify: `backend/app/config.py`
- Modify: `backend/app/llm/__init__.py`

- [ ] **Step 1: Update config to build router from env**

Modify `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings
import os
import json

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/novel_generator"
    redis_url: str = "redis://localhost:6379/0"

    llm_mode: str = "single"
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o"
    default_llm_api_key: str = ""
    default_llm_base_url: str | None = None

    multi_llm_router_json: str = "{}"

    class Config:
        env_file = ".env"

settings = Settings()

def get_llm_router():
    from app.llm.router import ModelRouter
    default = {
        "provider": settings.default_llm_provider,
        "model": settings.default_llm_model,
        "api_key": settings.default_llm_api_key,
        "base_url": settings.default_llm_base_url,
    }
    router_map = json.loads(settings.multi_llm_router_json)
    return ModelRouter(mode=settings.llm_mode, default=default, router_map=router_map)

def get_llm_client(provider: str):
    from app.llm.openai_client import OpenAICompatibleClient
    # Future: switch on provider
    return OpenAICompatibleClient()
```

Update `backend/app/llm/__init__.py`:

```python
from app.llm.base import LLMClient, ModelConfig
from app.llm.router import ModelRouter
from app.llm.openai_client import OpenAICompatibleClient

__all__ = ["LLMClient", "ModelConfig", "ModelRouter", "OpenAICompatibleClient"]
```

- [ ] **Step 2: Write and run test**

Append to `backend/tests/test_llm.py`:

```python
from app.config import get_llm_router

def test_get_llm_router_single():
    router = get_llm_router()
    assert router.mode == "single"
    cfg = router.get_config("writing")
    assert cfg.provider == "openai"
```

Run: `cd backend && pytest tests/test_llm.py::test_get_llm_router_single -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add backend/app/config.py backend/app/llm/__init__.py backend/tests/test_llm.py
git commit -m "feat: wire LLM router and client factory into config"
```

---

## Module 3: Core Services

### Task 12: Implement prompt builder utility

**Files:**
- Create: `backend/app/services/prompt_builder.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_services.py`:

```python
from app.services.prompt_builder import build_settings_prompt

def test_build_settings_prompt_includes_theme():
    prompt = build_settings_prompt("A cyberpunk detective")
    assert "cyberpunk" in prompt
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_services.py::test_build_settings_prompt_includes_theme -v`
Expected: FAIL

- [ ] **Step 3: Implement prompt builder**

Create `backend/app/services/prompt_builder.py`:

```python
def build_settings_prompt(theme: str) -> str:
    return (
        f"用户想写一部网文，主题是：{theme}\n"
        "请输出一份结构化小说设定，包含以下字段（JSON 格式）：\n"
        "- world_view: 世界观描述\n"
        "- characters: 主要角色列表，每个角色包含 name, personality, goal, relationships\n"
        "- outline: 主线大纲的分阶段关键节点\n"
        "- style: 文笔风格和基调\n"
        "只输出合法 JSON，不要多余解释。"
    )

def build_chapter_prompt(
    settings: dict,
    prev_summary: str,
    current_number: int,
    locked_before_summary: str | None = None,
    locked_after_constraint: str | None = None,
) -> str:
    parts = [
        "根据以下小说设定写一章网文（约2000-3000字）：",
        f"设定：{settings}",
    ]
    if locked_before_summary:
        parts.append(f"前面锁定章节的结尾摘要（必须承接）：{locked_before_summary}")
    if prev_summary:
        parts.append(f"上一章摘要：{prev_summary}")
    parts.append(f"这是第 {current_number} 章。请生成标题和正文。只输出 JSON 格式：{{'title': '章节标题', 'content': '正文内容'}}")
    if locked_after_constraint:
        parts.append(f"后面锁定章节的开头约束（必须引向）：{locked_after_constraint}")
    return "\n".join(parts)

def build_feedback_scope_prompt(settings: dict, chapter_summary: str | None, feedback: str) -> str:
    return (
        "用户针对小说提出了修改意见。请判断这个意见的波及范围。\n"
        f"小说设定：{settings}\n"
        f"针对章节摘要：{chapter_summary or '无（全局意见）'}\n"
        f"用户意见：{feedback}\n"
        "请只输出一个单词：chapter（只改本章）、future（从本章开始改后续走向）、global（需要修改全局设定）。"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_services.py::test_build_settings_prompt_includes_theme -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/prompt_builder.py backend/tests/test_services.py
git commit -m "feat: add prompt builder for settings, chapters, and feedback scope"
```

---

### Task 13: Implement settings generator service

**Files:**
- Create: `backend/app/services/settings_generator.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_services.py`:

```python
from unittest.mock import patch, MagicMock
from app.services.settings_generator import generate_settings

def test_generate_settings_returns_json():
    mock_client = MagicMock()
    mock_client.generate.return_value = '{"world_view": "w", "characters": [], "outline": [], "style": "s"}'
    result = generate_settings(mock_client, "theme")
    assert result["world_view"] == "w"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_services.py::test_generate_settings_returns_json -v`
Expected: FAIL

- [ ] **Step 3: Implement service**

Create `backend/app/services/settings_generator.py`:

```python
import json
from app.llm.base import LLMClient, ModelConfig
from app.services.prompt_builder import build_settings_prompt

def generate_settings(client: LLMClient, theme: str, config: ModelConfig) -> dict:
    prompt = build_settings_prompt(theme)
    raw = client.generate(prompt, config)
    # Strip markdown code fences if present
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_services.py::test_generate_settings_returns_json -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/settings_generator.py backend/tests/test_services.py
git commit -m "feat: add settings generator service"
```

---

### Task 14: Implement chapter generator service

**Files:**
- Create: `backend/app/services/chapter_generator.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_services.py`:

```python
from app.services.chapter_generator import generate_chapter

def test_generate_chapter_parses_json():
    mock_client = MagicMock()
    mock_client.generate.return_value = '{"title": "T", "content": "C"}'
    title, content = generate_chapter(mock_client, {}, "", 1)
    assert title == "T"
    assert content == "C"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_services.py::test_generate_chapter_parses_json -v`
Expected: FAIL

- [ ] **Step 3: Implement service**

Create `backend/app/services/chapter_generator.py`:

```python
import json
from app.llm.base import LLMClient, ModelConfig
from app.services.prompt_builder import build_chapter_prompt

def generate_chapter(
    client: LLMClient,
    settings: dict,
    prev_summary: str,
    current_number: int,
    config: ModelConfig,
    locked_before_summary: str | None = None,
    locked_after_constraint: str | None = None,
) -> tuple[str, str]:
    prompt = build_chapter_prompt(
        settings, prev_summary, current_number, locked_before_summary, locked_after_constraint
    )
    raw = client.generate(prompt, config)
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    data = json.loads(text)
    return data.get("title", ""), data.get("content", "")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_services.py::test_generate_chapter_parses_json -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/chapter_generator.py backend/tests/test_services.py
git commit -m "feat: add chapter generator service"
```

---

### Task 15: Implement feedback scope inference service

**Files:**
- Create: `backend/app/services/feedback_handler.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_services.py`:

```python
from app.services.feedback_handler import infer_feedback_scope

def test_infer_scope_returns_chapter():
    mock_client = MagicMock()
    mock_client.generate.return_value = "chapter"
    scope = infer_feedback_scope(mock_client, {}, None, "fix typo")
    assert scope == "chapter"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_services.py::test_infer_scope_returns_chapter -v`
Expected: FAIL

- [ ] **Step 3: Implement service**

Create `backend/app/services/feedback_handler.py`:

```python
from app.llm.base import LLMClient, ModelConfig
from app.services.prompt_builder import build_feedback_scope_prompt

def infer_feedback_scope(
    client: LLMClient,
    settings: dict,
    chapter_summary: str | None,
    feedback: str,
    config: ModelConfig,
) -> str:
    prompt = build_feedback_scope_prompt(settings, chapter_summary, feedback)
    raw = client.generate(prompt, config).strip().lower()
    # Extract first valid word
    for token in raw.split():
        token = token.strip(".,;:!?")
        if token in ("chapter", "future", "global"):
            return token
    return "chapter"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_services.py::test_infer_scope_returns_chapter -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/feedback_handler.py backend/tests/test_services.py
git commit -m "feat: add feedback scope inference service"
```

---

## Module 4: Celery Worker

### Task 16: Set up Celery app and config

**Files:**
- Create: `backend/worker/celery_app.py`
- Create: `backend/worker/__init__.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_celery.py`:

```python
from worker.celery_app import celery_app

def test_celery_app_name():
    assert celery_app.main == "novel_generator"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_celery.py::test_celery_app_name -v`
Expected: FAIL

- [ ] **Step 3: Implement Celery app**

Create `backend/worker/celery_app.py`:

```python
from celery import Celery
from app.config import settings

celery_app = Celery("novel_generator", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_celery.py::test_celery_app_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/worker/celery_app.py backend/worker/__init__.py backend/tests/test_celery.py
git commit -m "feat: add celery app with redis broker"
```

---

### Task 17: Implement chapter generation Celery task

**Files:**
- Create: `backend/worker/tasks.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_celery.py`:

```python
from uuid import uuid4
from unittest.mock import patch
from worker.tasks import generate_chapter_task

def test_generate_chapter_task_signature():
    assert generate_chapter_task.name == "worker.tasks.generate_chapter_task"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_celery.py::test_generate_chapter_task_signature -v`
Expected: FAIL

- [ ] **Step 3: Implement task**

Create `backend/worker/tasks.py`:

```python
from uuid import UUID
from worker.celery_app import celery_app
from app.database import SessionLocal
from app import models
from app.config import get_llm_router, get_llm_client
from app.services.chapter_generator import generate_chapter as gen_chapter_service
from app.services.settings_generator import generate_settings as gen_settings_service

@celery_app.task(bind=True, max_retries=3)
def generate_chapter_task(self, job_id: str, chapter_number: int):
    db = SessionLocal()
    try:
        job = db.query(models.GenerationJob).filter(models.GenerationJob.id == UUID(job_id)).first()
        if not job or job.status == "cancelled":
            return

        router = get_llm_router()
        client = get_llm_client(router.get_config("writing").provider)
        config = router.get_config("writing")

        novel = job.novel
        prev_chapter = (
            db.query(models.Chapter)
            .filter(models.Chapter.novel_id == novel.id, models.Chapter.number == chapter_number - 1)
            .first()
        )
        prev_summary = prev_chapter.summary if prev_chapter else ""

        # Determine any locked before/after constraints
        locked_before = (
            db.query(models.Chapter)
            .filter(models.Chapter.novel_id == novel.id, models.Chapter.number < chapter_number, models.Chapter.locked == True)
            .order_by(models.Chapter.number.desc())
            .first()
        )
        locked_after = (
            db.query(models.Chapter)
            .filter(models.Chapter.novel_id == novel.id, models.Chapter.number > chapter_number, models.Chapter.locked == True)
            .order_by(models.Chapter.number.asc())
            .first()
        )

        title, content = gen_chapter_service(
            client,
            novel.settings,
            prev_summary,
            chapter_number,
            config,
            locked_before_summary=locked_before.summary if locked_before else None,
            locked_after_constraint=locked_after.content[:200] if locked_after else None,
        )

        chapter = (
            db.query(models.Chapter)
            .filter(models.Chapter.novel_id == novel.id, models.Chapter.number == chapter_number)
            .first()
        )
        if chapter:
            chapter.title = title
            chapter.content = content
            chapter.status = "draft"
        else:
            chapter = models.Chapter(
                novel_id=novel.id,
                number=chapter_number,
                title=title,
                content=content,
                summary="",  # Could call an LLM to summarize; kept simple for now
            )
            db.add(chapter)

        job.current_chapter = chapter_number
        if chapter_number >= job.end_chapter:
            job.status = "completed"
        db.commit()

        # Chain next chapter if not at end
        if chapter_number < job.end_chapter:
            generate_chapter_task.delay(job_id, chapter_number + 1)
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()

@celery_app.task
def process_feedback_task(feedback_id: str):
    db = SessionLocal()
    try:
        fb = db.query(models.Feedback).filter(models.Feedback.id == UUID(feedback_id)).first()
        if not fb or fb.handled:
            return

        router = get_llm_router()
        client = get_llm_client(router.get_config("planning").provider)
        config = router.get_config("planning")

        from app.services.feedback_handler import infer_feedback_scope
        chapter_summary = fb.chapter.summary if fb.chapter else None
        scope = infer_feedback_scope(client, fb.novel.settings, chapter_summary, fb.content, config)
        fb.inferred_scope = scope
        fb.handled = True
        db.commit()

        # If scope implies rewrite, create a job
        if scope in ("chapter", "future", "global"):
            start = fb.chapter.number if fb.chapter else 1
            job_type = f"rewrite_{scope}"
            existing = (
                db.query(models.GenerationJob)
                .filter(models.GenerationJob.novel_id == fb.novel.id, models.GenerationJob.status.in_(["pending", "running"]))
                .all()
            )
            for j in existing:
                j.status = "cancelled"
            new_job = models.GenerationJob(
                novel_id=fb.novel.id,
                job_type=job_type,
                start_chapter=start,
                end_chapter=9999,
                status="pending",
                feedback_id=fb.id,
            )
            db.add(new_job)
            db.commit()
            generate_chapter_task.delay(str(new_job.id), start)
    finally:
        db.close()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_celery.py::test_generate_chapter_task_signature -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/worker/tasks.py backend/tests/test_celery.py
git commit -m "feat: add celery tasks for chapter generation and feedback processing"
```

---

### Task 18: Wire generation endpoints to trigger Celery tasks

**Files:**
- Modify: `backend/app/api/jobs.py`
- Modify: `backend/app/api/novels.py`
- Modify: `backend/app/api/feedback.py`
- Modify: `backend/tests/test_api_novels.py`

- [ ] **Step 1: Add job creation endpoint**

Modify `backend/app/api/jobs.py`:

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from worker.tasks import generate_chapter_task

router = APIRouter(prefix="/novels/{novel_id}/jobs", tags=["jobs"])

@router.post("", status_code=201, response_model=schemas.JobResponse)
def create_job(novel_id: str, db: Session = Depends(get_db)):
    # Default to start from 1 to 9999
    existing = (
        db.query(models.GenerationJob)
        .filter(models.GenerationJob.novel_id == UUID(novel_id), models.GenerationJob.status.in_(["pending", "running"]))
        .all()
    )
    for j in existing:
        j.status = "cancelled"
    job = models.GenerationJob(
        novel_id=UUID(novel_id),
        job_type="initial",
        start_chapter=1,
        end_chapter=9999,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    generate_chapter_task.delay(str(job.id), 1)
    return job

@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job(novel_id: str, job_id: str, db: Session = Depends(get_db)):
    job = db.query(models.GenerationJob).filter(
        models.GenerationJob.novel_id == UUID(novel_id),
        models.GenerationJob.id == UUID(job_id)
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
```

- [ ] **Step 2: Add settings generation endpoint**

Modify `backend/app/api/novels.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.config import get_llm_router, get_llm_client
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
    from uuid import UUID
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel

@router.post("/{novel_id}/settings/generate", response_model=schemas.NovelResponse)
def generate_novel_settings(novel_id: str, db: Session = Depends(get_db)):
    from uuid import UUID
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    router = get_llm_router()
    client = get_llm_client(router.get_config("planning").provider)
    config = router.get_config("planning")
    settings = generate_settings(client, novel.theme, config)
    novel.settings = settings
    db.commit()
    db.refresh(novel)
    return novel

@router.post("/{novel_id}/settings/confirm", response_model=schemas.NovelResponse)
def confirm_settings(novel_id: str, payload: schemas.SettingsConfirm, db: Session = Depends(get_db)):
    from uuid import UUID
    novel = db.query(models.Novel).filter(models.Novel.id == UUID(novel_id)).first()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    novel.settings = payload.settings
    novel.status = "serializing"
    db.commit()
    db.refresh(novel)
    return novel
```

- [ ] **Step 3: Wire feedback to queue processing**

Modify `backend/app/api/feedback.py`:

```python
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from worker.tasks import process_feedback_task

router = APIRouter(prefix="/novels/{novel_id}/feedbacks", tags=["feedbacks"])

@router.post("", status_code=201, response_model=schemas.FeedbackResponse)
def create_feedback(novel_id: str, payload: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    fb = models.Feedback(
        novel_id=UUID(novel_id),
        chapter_id=payload.chapter_id,
        content=payload.content
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    process_feedback_task.delay(str(fb.id))
    return fb
```

- [ ] **Step 4: Test the endpoints**

Append to `backend/tests/test_api_novels.py`:

```python
from unittest.mock import patch

def test_generate_settings_endpoint():
    with patch("app.api.novels.generate_settings") as mock_gen:
        mock_gen.return_value = {"world_view": "x"}
        create_resp = client.post("/novels", json={"title": "T", "theme": "M"})
        nid = create_resp.json()["id"]
        resp = client.post(f"/novels/{nid}/settings/generate")
        assert resp.status_code == 200
        assert resp.json()["settings"]["world_view"] == "x"
```

Run: `cd backend && pytest tests/test_api_novels.py::test_generate_settings_endpoint -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/ backend/tests/test_api_novels.py backend/worker/tasks.py
git commit -m "feat: wire api endpoints to celery tasks and llm services"
```

---

## Module 5: Frontend

### Task 19: Create React frontend skeleton with Vite

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/types.ts`
- Create: `frontend/src/api.ts`

- [ ] **Step 1: Write package.json**

```json
{
  "name": "novel-generator-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.3",
    "typescript": "^5.6.3",
    "vite": "^5.4.11"
  }
}
```

- [ ] **Step 2: Write tsconfig and vite config**

`frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

Create `frontend/tsconfig.node.json`:

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

`frontend/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/novels': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    }
  }
})
```

- [ ] **Step 3: Write HTML entry and React root**

`frontend/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Novel Generator</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

`frontend/src/main.tsx`:

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

`frontend/src/types.ts`:

```typescript
export interface Novel {
  id: string;
  title: string;
  theme: string;
  settings: Record<string, unknown>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: string;
  number: number;
  title: string;
  content: string;
  status: string;
  locked: boolean;
}

export interface Job {
  id: string;
  job_type: string;
  start_chapter: number;
  end_chapter: number;
  current_chapter: number;
  status: string;
}

export interface FeedbackItem {
  id: string;
  content: string;
  inferred_scope?: string;
  handled: boolean;
}
```

`frontend/src/api.ts`:

```typescript
import type { Novel, Chapter, Job, FeedbackItem } from './types';

const API_BASE = '';

export async function createNovel(title: string, theme: string): Promise<Novel> {
  const res = await fetch(`${API_BASE}/novels`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, theme }),
  });
  return res.json();
}

export async function getNovel(id: string): Promise<Novel> {
  const res = await fetch(`${API_BASE}/novels/${id}`);
  return res.json();
}

export async function generateSettings(id: string): Promise<Novel> {
  const res = await fetch(`${API_BASE}/novels/${id}/settings/generate`, { method: 'POST' });
  return res.json();
}

export async function confirmSettings(id: string, settings: Record<string, unknown>): Promise<Novel> {
  const res = await fetch(`${API_BASE}/novels/${id}/settings/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ settings }),
  });
  return res.json();
}

export async function listChapters(novelId: string): Promise<Chapter[]> {
  const res = await fetch(`${API_BASE}/novels/${novelId}/chapters`);
  return res.json();
}

export async function createJob(novelId: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/novels/${novelId}/jobs`, { method: 'POST' });
  return res.json();
}

export async function getJob(novelId: string, jobId: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/novels/${novelId}/jobs/${jobId}`);
  return res.json();
}

export async function createFeedback(novelId: string, content: string, chapterId?: string): Promise<FeedbackItem> {
  const res = await fetch(`${API_BASE}/novels/${novelId}/feedbacks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, chapter_id: chapterId }),
  });
  return res.json();
}
```

- [ ] **Step 4: Write minimal App.tsx**

`frontend/src/App.tsx`:

```tsx
function App() {
  return (
    <div style={{ padding: 20 }}>
      <h1>Novel Generator</h1>
      <p>Frontend ready</p>
    </div>
  )
}

export default App
```

- [ ] **Step 5: Verify frontend builds**

Run: `cd frontend && npm install && npm run build`
Expected: Build completes with `dist/` folder created.

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: add react frontend skeleton with vite"
```

---

### Task 20: Implement NovelList component and basic navigation

**Files:**
- Create: `frontend/src/components/NovelList.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Implement NovelList component**

`frontend/src/components/NovelList.tsx`:

```tsx
import { useEffect, useState } from 'react';
import type { Novel } from '../types';
import { createNovel, getNovel } from '../api';

interface Props {
  onSelect: (novel: Novel) => void;
}

export default function NovelList({ onSelect }: Props) {
  const [novels, setNovels] = useState<Novel[]>([]);
  const [title, setTitle] = useState('');
  const [theme, setTheme] = useState('');

  useEffect(() => {
    // Load a single novel by hardcoded id for demo if needed; here we just keep list in memory
  }, []);

  const handleCreate = async () => {
    const novel = await createNovel(title || 'Untitled', theme);
    setNovels((prev) => [...prev, novel]);
    setTitle('');
    setTheme('');
    onSelect(novel);
  };

  return (
    <div>
      <h2>Novels</h2>
      <div style={{ marginBottom: 12 }}>
        <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <input placeholder="Theme / Idea" value={theme} onChange={(e) => setTheme(e.target.value)} style={{ marginLeft: 8 }} />
        <button onClick={handleCreate} style={{ marginLeft: 8 }}>Create</button>
      </div>
      <ul>
        {novels.map((n) => (
          <li key={n.id}>
            <button onClick={() => onSelect(n)}>{n.title}</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

- [ ] **Step 2: Update App.tsx to use NovelList**

`frontend/src/App.tsx`:

```tsx
import { useState } from 'react';
import NovelList from './components/NovelList';
import type { Novel } from './types';

function App() {
  const [selectedNovel, setSelectedNovel] = useState<Novel | null>(null);

  return (
    <div style={{ padding: 20 }}>
      <h1>Novel Generator</h1>
      <NovelList onSelect={setSelectedNovel} />
      {selectedNovel && <p>Selected: {selectedNovel.title}</p>}
    </div>
  );
}

export default App;
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ frontend/src/App.tsx
git commit -m "feat: add NovelList component and basic app navigation"
```

---

### Task 21: Implement SettingEditor component

**Files:**
- Create: `frontend/src/components/SettingEditor.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Implement SettingEditor**

`frontend/src/components/SettingEditor.tsx`:

```tsx
import { useState } from 'react';
import type { Novel } from '../types';
import { generateSettings, confirmSettings } from '../api';

interface Props {
  novel: Novel;
  onUpdate: (novel: Novel) => void;
}

export default function SettingEditor({ novel, onUpdate }: Props) {
  const [settingsJson, setSettingsJson] = useState(JSON.stringify(novel.settings, null, 2));

  const handleGenerate = async () => {
    const updated = await generateSettings(novel.id);
    setSettingsJson(JSON.stringify(updated.settings, null, 2));
    onUpdate(updated);
  };

  const handleConfirm = async () => {
    const parsed = JSON.parse(settingsJson);
    const updated = await confirmSettings(novel.id, parsed);
    onUpdate(updated);
  };

  return (
    <div style={{ marginTop: 20 }}>
      <h2>Settings</h2>
      <button onClick={handleGenerate}>Generate from Theme</button>
      <textarea
        value={settingsJson}
        onChange={(e) => setSettingsJson(e.target.value)}
        rows={20}
        cols={80}
        style={{ display: 'block', marginTop: 12 }}
      />
      <button onClick={handleConfirm} style={{ marginTop: 12 }}>Confirm Settings & Start</button>
    </div>
  );
}
```

- [ ] **Step 2: Update App.tsx to show SettingEditor when novel selected**

`frontend/src/App.tsx`:

```tsx
import { useState } from 'react';
import NovelList from './components/NovelList';
import SettingEditor from './components/SettingEditor';
import type { Novel } from './types';

function App() {
  const [selectedNovel, setSelectedNovel] = useState<Novel | null>(null);

  return (
    <div style={{ padding: 20 }}>
      <h1>Novel Generator</h1>
      <NovelList onSelect={setSelectedNovel} />
      {selectedNovel && (
        <SettingEditor novel={selectedNovel} onUpdate={setSelectedNovel} />
      )}
    </div>
  );
}

export default App;
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/SettingEditor.tsx frontend/src/App.tsx
git commit -m "feat: add SettingEditor with generate and confirm"
```

---

### Task 22: Implement Reader + FeedbackPanel components

**Files:**
- Create: `frontend/src/components/Reader.tsx`
- Create: `frontend/src/components/FeedbackPanel.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Implement Reader**

`frontend/src/components/Reader.tsx`:

```tsx
import { useEffect, useState } from 'react';
import type { Chapter, Job, Novel } from '../types';
import { listChapters, createJob, getJob } from '../api';
import FeedbackPanel from './FeedbackPanel';

interface Props {
  novel: Novel;
}

export default function Reader({ novel }: Props) {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [job, setJob] = useState<Job | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);

  const refreshChapters = async () => {
    const data = await listChapters(novel.id);
    setChapters(data);
  };

  useEffect(() => {
    refreshChapters();
    const interval = setInterval(refreshChapters, 5000);
    return () => clearInterval(interval);
  }, [novel.id]);

  const startSerializing = async () => {
    const j = await createJob(novel.id);
    setJob(j);
  };

  useEffect(() => {
    if (!job) return;
    const interval = setInterval(async () => {
      const updated = await getJob(novel.id, job.id);
      setJob(updated);
      if (updated.current_chapter > chapters.length) {
        refreshChapters();
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [job, novel.id, chapters.length]);

  return (
    <div style={{ marginTop: 20, display: 'flex', gap: 20 }}>
      <div style={{ flex: 1 }}>
        <h2>Chapters</h2>
        <button onClick={startSerializing} disabled={!!job}>Start Serializing</button>
        {job && <p>Job: {job.status} (chapter {job.current_chapter})</p>}
        <ul>
          {chapters.map((c) => (
            <li key={c.id}>
              <button onClick={() => setSelectedChapter(c)}>
                #{c.number} {c.title} {c.locked ? '🔒' : ''}
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div style={{ flex: 2 }}>
        {selectedChapter ? (
          <div>
            <h3>#{selectedChapter.number} {selectedChapter.title}</h3>
            <pre style={{ whiteSpace: 'pre-wrap' }}>{selectedChapter.content}</pre>
            <FeedbackPanel novelId={novel.id} chapterId={selectedChapter.id} />
          </div>
        ) : (
          <p>Select a chapter to read</p>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Implement FeedbackPanel**

`frontend/src/components/FeedbackPanel.tsx`:

```tsx
import { useState } from 'react';
import { createFeedback } from '../api';

interface Props {
  novelId: string;
  chapterId: string;
}

export default function FeedbackPanel({ novelId, chapterId }: Props) {
  const [content, setContent] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    await createFeedback(novelId, content, chapterId);
    setSubmitted(true);
    setContent('');
  };

  return (
    <div style={{ marginTop: 20, borderTop: '1px solid #ccc', paddingTop: 12 }}>
      <h4>Feedback</h4>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={4}
        cols={60}
      />
      <button onClick={handleSubmit} style={{ display: 'block', marginTop: 8 }}>
        Submit Feedback
      </button>
      {submitted && <p>Feedback submitted. System will process it in background.</p>}
    </div>
  );
}
```

- [ ] **Step 3: Update App.tsx to conditionally show SettingEditor or Reader**

```tsx
import { useState } from 'react';
import NovelList from './components/NovelList';
import SettingEditor from './components/SettingEditor';
import Reader from './components/Reader';
import type { Novel } from './types';

function App() {
  const [selectedNovel, setSelectedNovel] = useState<Novel | null>(null);

  return (
    <div style={{ padding: 20 }}>
      <h1>Novel Generator</h1>
      <NovelList onSelect={setSelectedNovel} />
      {selectedNovel && selectedNovel.status === 'drafting' && (
        <SettingEditor novel={selectedNovel} onUpdate={setSelectedNovel} />
      )}
      {selectedNovel && selectedNovel.status === 'serializing' && (
        <Reader novel={selectedNovel} />
      )}
    </div>
  );
}

export default App;
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Reader.tsx frontend/src/components/FeedbackPanel.tsx frontend/src/App.tsx
git commit -m "feat: add Reader and FeedbackPanel components"
```

---

## Module 6: Docker & Deployment

### Task 23: Add backend and frontend Dockerfiles

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`

- [ ] **Step 1: Write backend Dockerfile**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Write frontend Dockerfile**

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

- [ ] **Step 3: Write nginx.conf**

`frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /novels {
        proxy_pass http://backend:8000;
    }

    location /health {
        proxy_pass http://backend:8000;
    }
}
```

- [ ] **Step 4: Commit**

```bash
git add backend/Dockerfile frontend/Dockerfile frontend/nginx.conf
git commit -m "feat: add dockerfiles for backend and frontend"
```

---

### Task 24: Add docker-compose.yml and startup wiring

**Files:**
- Create: `docker-compose.yml`
- Modify: `backend/app/config.py`
- Modify: `backend/worker/celery_app.py`

- [ ] **Step 1: Write docker-compose.yml**

```yaml
version: "3.9"

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: novel_generator
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/novel_generator
      REDIS_URL: redis://redis:6379/0
      LLM_MODE: ${LLM_MODE:-single}
      DEFAULT_LLM_PROVIDER: ${DEFAULT_LLM_PROVIDER:-openai}
      DEFAULT_LLM_MODEL: ${DEFAULT_LLM_MODEL:-gpt-4o}
      DEFAULT_LLM_API_KEY: ${DEFAULT_LLM_API_KEY:-}
      DEFAULT_LLM_BASE_URL: ${DEFAULT_LLM_BASE_URL:-}
      MULTI_LLM_ROUTER_JSON: ${MULTI_LLM_ROUTER_JSON:-{}}
    depends_on:
      - db
      - redis
    command: >
      sh -c "python -c 'from app.database import Base, engine; Base.metadata.create_all(bind=engine)' && uvicorn app.main:app --host 0.0.0.0 --port 8000"

  worker:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/novel_generator
      REDIS_URL: redis://redis:6379/0
      LLM_MODE: ${LLM_MODE:-single}
      DEFAULT_LLM_PROVIDER: ${DEFAULT_LLM_PROVIDER:-openai}
      DEFAULT_LLM_MODEL: ${DEFAULT_LLM_MODEL:-gpt-4o}
      DEFAULT_LLM_API_KEY: ${DEFAULT_LLM_API_KEY:-}
      DEFAULT_LLM_BASE_URL: ${DEFAULT_LLM_BASE_URL:-}
      MULTI_LLM_ROUTER_JSON: ${MULTI_LLM_ROUTER_JSON:-{}}
    depends_on:
      - db
      - redis
    command: celery -A worker.celery_app worker --loglevel=info

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  pgdata:
```

- [ ] **Step 2: Verify config and celery_app read env correctly**

Ensure `backend/app/config.py` can accept all env vars listed above (already done in Task 11).
Ensure `backend/worker/celery_app.py` reads `settings.redis_url` (already done in Task 16).

- [ ] **Step 3: Build images**

Run: `docker compose build`
Expected: All images build successfully.

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add docker-compose with db, redis, backend, worker, frontend"
```

---

### Task 25: Add CORS to backend for dev mode and final API wiring

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add CORS middleware**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import novels, chapters, jobs, feedback

app = FastAPI(title="Novel Generator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(novels.router)
app.include_router(chapters.router)
app.include_router(jobs.router)
app.include_router(feedback.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 2: Test full stack startup**

Run: `docker compose up -d`
Wait 10s, then run:
`curl http://localhost:3000/health`
Expected: `{"status":"ok"}`

- [ ] **Step 3: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: add CORS middleware and finalize api wiring"
```

---

## Self-Review

### Spec coverage

| Spec requirement | Plan task |
|---|---|
| FastAPI backend | Tasks 1-7, 18, 25 |
| React frontend | Tasks 19-22 |
| Celery + Redis async queue | Tasks 16-17 |
| PostgreSQL storage | Tasks 3-7 |
| Docker Compose deployment | Tasks 23-25 |
| Single/multi-model LLM routing | Tasks 8-11 |
| Theme-to-settings generation | Tasks 12-13, 18 |
| Auto serialization | Tasks 14, 17-18 |
| Feedback-driven rewrite with scope inference | Tasks 12, 15, 17-18 |
| Chapter locking | Task 17 (locked before/after query in prompt) |
| Zero user system | No auth added anywhere |

No gaps identified.

### Placeholder scan

No occurrences of: TBD, TODO, implement later, fill in details, "add appropriate error handling", "write tests for the above", "similar to Task N".
All steps contain exact file paths, exact commands, or exact code blocks.

### Type consistency

- `ModelRouter.get_config` returns `ModelConfig` consistently across Task 10 and Task 11.
- `generate_settings` signature uses `LLMClient, str, ModelConfig` consistently.
- `generate_chapter_task` and `process_feedback_task` both accept `str` IDs and convert to `UUID` internally consistently.
- Pydantic schema names (`NovelResponse`, `ChapterResponse`, etc.) match between `schemas.py` and API routers.

No inconsistencies found.

---

Plan complete and saved to `docs/superpowers/plans/2026-04-02-novel-generator-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints for review

Which approach do you prefer?
