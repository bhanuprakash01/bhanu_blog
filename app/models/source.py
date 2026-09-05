from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False, index=True)
    url = Column(String(1024), unique=True, nullable=False)
    category = Column(String(64), nullable=False, default="AI News")
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    priority = Column(Integer, default=5, nullable=False)  # 1 to 10

    last_fetched_at = Column(DateTime, nullable=True)
    last_status = Column(String(32), default="OK")  # OK, ERROR, TIMEOUT
    last_error = Column(String(512), nullable=True)
    consecutive_failures = Column(Integer, default=0)
    total_articles_fetched = Column(Integer, default=0)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
