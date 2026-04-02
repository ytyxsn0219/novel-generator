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
