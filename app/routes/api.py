from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, desc
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.article import Article, ProcessingStatus
from app.models.source import Source
from app.models.processing_log import ProcessingLog
from app.schemas.api import (
    ArticleListResponse,
    AdminStatsResponse,
    HealthCheckResponse,
    SourceResponse,
)
from app.schemas.article import ArticleResponse
from app.services.scheduler import news_scheduler
from app.services.article_processor import ArticleProcessor

router = APIRouter(tags=["API"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint used by Docker healthchecks and monitoring."""
    db_status = "ok"
    articles_count = 0
    try:
        articles_count = db.query(Article).count()
    except Exception:
        db_status = "error"

    scheduler_status = "running" if news_scheduler.scheduler.running else "stopped"

    overall_status = "healthy" if db_status == "ok" else "unhealthy"
    return HealthCheckResponse(
        status=overall_status,
        database=db_status,
        scheduler=scheduler_status,
        articles_count=articles_count,
    )


@router.get("/api/articles", response_model=ArticleListResponse)
def get_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    category: Optional[str] = None,
    source: Optional[str] = None,
    days: Optional[int] = None,
    status_filter: str = Query("PROCESSED"),
    db: Session = Depends(get_db),
):
    """Returns paginated articles filtered by category, source, date range, and status."""
    query = db.query(Article)

    if status_filter != "ALL":
        query = query.filter(Article.processing_status == status_filter)

    if category and category != "All":
        query = query.filter(Article.category == category)

    if source:
        query = query.filter(Article.source_name == source)

    if days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(Article.published_at >= cutoff)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Article.published_at.desc()).offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return ArticleListResponse(
        items=[ArticleResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/api/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Fetches a single article by ID."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleResponse.model_validate(article)


@router.get("/api/latest", response_model=list[ArticleResponse])
def get_latest_articles(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Returns the most recent processed articles."""
    articles = (
        db.query(Article)
        .filter(Article.processing_status == ProcessingStatus.PROCESSED)
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )
    return [ArticleResponse.model_validate(a) for a in articles]


@router.get("/api/trending", response_model=list[ArticleResponse])
def get_trending_articles(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Returns articles sorted by trending algorithm score."""
    articles = (
        db.query(Article)
        .filter(Article.processing_status == ProcessingStatus.PROCESSED)
        .order_by(Article.trending_score.desc(), Article.published_at.desc())
        .limit(limit)
        .all()
    )
    return [ArticleResponse.model_validate(a) for a in articles]


@router.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """Returns canonical categories and the count of processed articles in each."""
    results = []
    for cat in settings.ALLOWED_CATEGORIES:
        count = (
            db.query(Article)
            .filter(Article.category == cat, Article.processing_status == ProcessingStatus.PROCESSED)
            .count()
        )
        results.append({"name": cat, "count": count})
    return results


@router.get("/api/sources", response_model=list[SourceResponse])
def get_sources(db: Session = Depends(get_db)):
    """Returns all configured RSS sources."""
    sources = db.query(Source).order_by(Source.priority.desc(), Source.name).all()
    return sources


@router.get("/api/search", response_model=ArticleListResponse)
def search_articles(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    category: Optional[str] = None,
    source: Optional[str] = None,
    days: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Full search across title, summary, description, tags, category, and source."""
    term = f"%{q.strip()}%"
    query = db.query(Article).filter(
        Article.processing_status == ProcessingStatus.PROCESSED,
        or_(
            Article.title.ilike(term),
            Article.summary.ilike(term),
            Article.description.ilike(term),
            Article.tags.ilike(term),
            Article.category.ilike(term),
            Article.source_name.ilike(term),
        )
    )

    if category and category != "All":
        query = query.filter(Article.category == category)

    if source:
        query = query.filter(Article.source_name == source)

    if days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(Article.published_at >= cutoff)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Article.published_at.desc()).offset(offset).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return ArticleListResponse(
        items=[ArticleResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/api/admin/refresh")
async def trigger_refresh(response: Response):
    """Manually triggers an RSS news collection cycle."""
    if news_scheduler.is_running_job:
        response.status_code = status.HTTP_409_CONFLICT
        return {"status": "busy", "message": "News collection already running."}

    # Run in background via scheduler
    res = await news_scheduler.run_scheduled_collection()
    return res


@router.get("/api/admin/stats", response_model=AdminStatsResponse)
def get_admin_stats(db: Session = Depends(get_db)):
    """Provides key operational statistics for the admin dashboard."""
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    total_articles = db.query(Article).count()
    articles_today = db.query(Article).filter(Article.created_at >= today_start).count()
    articles_processed_today = (
        db.query(Article)
        .filter(Article.gemini_processed_at >= today_start)
        .count()
    )
    failed_articles = (
        db.query(Article)
        .filter(Article.processing_status == ProcessingStatus.FAILED)
        .count()
    )
    total_sources = db.query(Source).count()
    enabled_sources = db.query(Source).filter(Source.enabled.is_(True)).count()
    gemini_count = (
        db.query(Article)
        .filter(Article.gemini_processed_at.isnot(None))
        .count()
    )

    recent_logs = (
        db.query(ProcessingLog)
        .filter(ProcessingLog.level.in_(["WARNING", "ERROR"]))
        .order_by(ProcessingLog.created_at.desc())
        .limit(10)
        .all()
    )

    latest_errors = [
        {
            "id": log.id,
            "level": log.level,
            "message": log.message,
            "details": log.details,
            "source_name": log.source_name,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in recent_logs
    ]

    return AdminStatsResponse(
        total_articles=total_articles,
        articles_today=articles_today,
        articles_processed_today=articles_processed_today,
        failed_articles=failed_articles,
        total_sources=total_sources,
        enabled_sources=enabled_sources,
        last_refresh=news_scheduler.last_run_time,
        next_refresh=news_scheduler.get_next_run_time(),
        gemini_processed_count=gemini_count,
        latest_errors=latest_errors,
    )
