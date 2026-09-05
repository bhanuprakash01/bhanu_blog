from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_name = Column(String(128), nullable=True, index=True)
    level = Column(String(16), default="INFO", nullable=False)  # INFO, WARNING, ERROR
    message = Column(String(256), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(64), primary_key=True, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
