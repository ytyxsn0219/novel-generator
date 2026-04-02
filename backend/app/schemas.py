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


class JobCreate(BaseModel):
    job_type: str
    start_chapter: int
    end_chapter: int


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


class SystemConfigItem(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemConfigUpdate(BaseModel):
    value: str


class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000


class LLMConfigResponse(BaseModel):
    provider: str
    model: str
    base_url: Optional[str]
    temperature: float
    max_tokens: int
    # api_key 不返回，保护密钥
