from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.article import ArticleResponse


class ArticleListResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SourceResponse(BaseModel):
    id: int
    name: str
    url: str
    category: str
    enabled: bool
    priority: int
    last_fetched_at: Optional[datetime] = None
    last_status: str
    last_error: Optional[str] = None
    total_articles_fetched: int


class SourceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    url: str = Field(..., min_length=5, max_length=1024)
    category: str = Field(default="AI News")
    enabled: bool = True
    priority: int = Field(default=5, ge=1, le=10)


class SourceUpdateRequest(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=10)


class AdminStatsResponse(BaseModel):
    total_articles: int
    articles_today: int
    articles_processed_today: int
    failed_articles: int
    total_sources: int
    enabled_sources: int
    last_refresh: Optional[datetime] = None
    next_refresh: Optional[datetime] = None
    gemini_processed_count: int
    latest_errors: list[dict] = Field(default_factory=list)


class HealthCheckResponse(BaseModel):
    status: str
    database: str
    scheduler: str
    articles_count: int
