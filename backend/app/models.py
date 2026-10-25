from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Integer, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from .database import Base
from .config import settings

def now(): return datetime.now(timezone.utc)
def uid(): return str(uuid4())

class Category(Base):
    __tablename__='service_categories'
    slug: Mapped[str] = mapped_column(String(80), primary_key=True)
    name_en: Mapped[str] = mapped_column(String(160))
    name_bn: Mapped[str] = mapped_column(String(160))
    icon: Mapped[str] = mapped_column(String(40), default='folder')

class Service(Base):
    __tablename__='services'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name_en: Mapped[str] = mapped_column(String(200))
    name_bn: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(ForeignKey('service_categories.slug'))
    description_en: Mapped[str] = mapped_column(Text, default='')
    description_bn: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(20), default='draft', index=True)
    official_url: Mapped[str] = mapped_column(Text, default='')
    # All structured claims belong to source versions, never unreviewed frontend copy.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Source(Base):
    __tablename__='sources'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    service_id: Mapped[str] = mapped_column(ForeignKey('services.id'), index=True)
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(300))
    agency: Mapped[str] = mapped_column(String(200), default='')
    current_version: Mapped[str | None] = mapped_column(String(36), nullable=True)

class SourceVersion(Base):
    __tablename__='source_versions'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    source_id: Mapped[str] = mapped_column(ForeignKey('sources.id'), index=True)
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default='pending', index=True)
    claims: Mapped[dict] = mapped_column(JSON, default=dict)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class Chunk(Base):
    __tablename__='knowledge_chunks'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    version_id: Mapped[str] = mapped_column(ForeignKey('source_versions.id'), index=True)
    text: Mapped[str] = mapped_column(Text)
    ordinal: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[list | None] = mapped_column(Vector(settings.embedding_dimensions).with_variant(JSON,'sqlite'), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(150), nullable=True)

class Admin(Base):
    __tablename__='admin_users'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    username: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)

class Session(Base):
    __tablename__='admin_sessions'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    admin_id: Mapped[str] = mapped_column(ForeignKey('admin_users.id'))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Audit(Base):
    __tablename__='audit_logs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    admin_id: Mapped[str] = mapped_column(ForeignKey('admin_users.id'))
    action: Mapped[str] = mapped_column(String(100))
    target: Mapped[str] = mapped_column(String(100))
    note: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Feedback(Base):
    __tablename__='feedback'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    message: Mapped[str] = mapped_column(Text)
    service_slug: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
