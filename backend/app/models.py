import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Novel(Base):
    __tablename__ = "novels"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = uuid.uuid4()
        super().__init__(**kwargs)
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


class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, nullable=False, unique=True)
    value = Column(Text, nullable=False)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
