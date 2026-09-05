import json
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Enum as SQLEnum,
    Index,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ProcessingStatus(str, Enum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# Association table for Article <-> Tag
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(512), nullable=False, index=True)
    url = Column(String(1024), nullable=False, unique=True, index=True)
    canonical_url = Column(String(1024), nullable=False, index=True)
    source_name = Column(String(128), nullable=False, index=True)
    source_url = Column(String(1024), nullable=True)
    author = Column(String(256), nullable=True)

    published_at = Column(DateTime, nullable=False, index=True)
    discovered_at = Column(DateTime, default=utc_now, nullable=False)

    image_url = Column(String(1024), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(64), nullable=False, default="AI News", index=True)

    # Stored as JSON string or comma-separated
    tags = Column(Text, nullable=True, default="[]")

    # Gemini Summarization Fields
    summary = Column(Text, nullable=True)
    key_takeaways = Column(Text, nullable=True, default="[]")  # JSON list
    why_it_matters = Column(Text, nullable=True)
    importance_score = Column(Integer, default=5)
    relevance_score = Column(Float, default=1.0)
    trending_score = Column(Float, default=0.0, index=True)

    content_hash = Column(String(64), nullable=False, index=True)
    processing_status = Column(
        SQLEnum(ProcessingStatus),
        default=ProcessingStatus.NEW,
        nullable=False,
        index=True,
    )
    failure_reason = Column(String(512), nullable=True)
    gemini_processed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Helper accessors for list properties stored as JSON
    @property
    def tags_list(self) -> list[str]:
        if not self.tags:
            return []
        try:
            val = json.loads(self.tags)
            if isinstance(val, list):
                return val
            return [t.strip() for t in str(self.tags).split(",") if t.strip()]
        except Exception:
            return [t.strip() for t in str(self.tags).split(",") if t.strip()]

    @tags_list.setter
    def tags_list(self, val: list[str]):
        self.tags = json.dumps(val or [])

    @property
    def takeaways_list(self) -> list[str]:
        if not self.key_takeaways:
            return []
        try:
            val = json.loads(self.key_takeaways)
            return val if isinstance(val, list) else []
        except Exception:
            return [self.key_takeaways]

    @takeaways_list.setter
    def takeaways_list(self, val: list[str]):
        self.key_takeaways = json.dumps(val or [])


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False, index=True)
    description = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=utc_now)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)


# Explicit composite / performance indices
Index("idx_articles_status_published", Article.processing_status, Article.published_at.desc())
Index("idx_articles_category_published", Article.category, Article.published_at.desc())
Index("idx_articles_trending", Article.trending_score.desc(), Article.published_at.desc())
