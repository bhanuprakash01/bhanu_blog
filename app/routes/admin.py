import hmac
import hashlib
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.article import Article, ProcessingStatus
from app.models.source import Source
from app.models.processing_log import ProcessingLog
from app.services.article_processor import ArticleProcessor
from app.services.scheduler import news_scheduler

router = APIRouter(tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")

COOKIE_NAME = "ai_news_hub_admin_token"


def make_token(username: str) -> str:
    """Generates an HMAC SHA-256 token for cookie authentication."""
    key = settings.SECRET_KEY.encode()
    msg = f"{username}:{settings.ADMIN_PASSWORD}".encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify_admin(request: Request) -> bool:
    """Checks if the request has a valid admin session cookie."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
    expected = make_token(settings.ADMIN_USERNAME)
    return hmac.compare_digest(token, expected)


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Admin dashboard view displaying system stats, logs, and controls."""
    if not verify_admin(request):
        return templates.TemplateResponse(
            request=request,
            name="admin.html",
            context={
                "authenticated": False,
                "error": None,
            },
        )

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
    sources = db.query(Source).order_by(Source.priority.desc(), Source.name).all()
    gemini_count = (
        db.query(Article)
        .filter(Article.gemini_processed_at.isnot(None))
        .count()
    )
    logs = (
        db.query(ProcessingLog)
        .order_by(ProcessingLog.created_at.desc())
        .limit(20)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "authenticated": True,
            "total_articles": total_articles,
            "articles_today": articles_today,
            "articles_processed_today": articles_processed_today,
            "failed_articles": failed_articles,
            "total_sources": len(sources),
            "enabled_sources": len([s for s in sources if s.enabled]),
            "sources": sources,
            "gemini_count": gemini_count,
            "logs": logs,
            "last_refresh": news_scheduler.last_run_time,
            "next_refresh": news_scheduler.get_next_run_time(),
            "scheduler_running": news_scheduler.scheduler.running,
            "is_busy": news_scheduler.is_running_job,
            "categories": settings.ALLOWED_CATEGORIES,
        },
    )


@router.post("/admin/login")
def admin_login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Processes admin login submission."""
    # Compare credentials safely
    is_user_match = hmac.compare_digest(username, settings.ADMIN_USERNAME)
    is_pass_match = hmac.compare_digest(password, settings.ADMIN_PASSWORD)

    if not (is_user_match and is_pass_match):
        return templates.TemplateResponse(
            request=request,
            name="admin.html",
            context={
                "authenticated": False,
                "error": "Invalid admin username or password.",
            },
            status_code=401,
        )

    res = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    token = make_token(username)
    res.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400 * 7,  # 7 days
    )
    return res


@router.get("/admin/logout")
def admin_logout():
    """Logs the admin out by clearing the auth cookie."""
    res = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    res.delete_cookie(COOKIE_NAME)
    return res


@router.post("/admin/sources/add")
def add_source(
    request: Request,
    name: str = Form(...),
    url: str = Form(...),
    category: str = Form(...),
    priority: int = Form(5),
    db: Session = Depends(get_db),
):
    if not verify_admin(request):
        raise HTTPException(status_code=403, detail="Unauthorized")

    existing = db.query(Source).filter(Source.url == url.strip()).first()
    if existing:
        return RedirectResponse(url="/admin?error=Source+already+exists", status_code=303)

    src = Source(
        name=name.strip(),
        url=url.strip(),
        category=category,
        priority=priority,
        enabled=True,
    )
    db.add(src)
    db.commit()
    return RedirectResponse(url="/admin?success=Source+added+successfully", status_code=303)


@router.post("/admin/sources/{source_id}/toggle")
def toggle_source(source_id: int, request: Request, db: Session = Depends(get_db)):
    if not verify_admin(request):
        raise HTTPException(status_code=403, detail="Unauthorized")

    src = db.query(Source).filter(Source.id == source_id).first()
    if src:
        src.enabled = not src.enabled
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/sources/{source_id}/delete")
def delete_source(source_id: int, request: Request, db: Session = Depends(get_db)):
    if not verify_admin(request):
        raise HTTPException(status_code=403, detail="Unauthorized")

    src = db.query(Source).filter(Source.id == source_id).first()
    if src:
        db.delete(src)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/sources/{source_id}/priority")
def update_priority(
    source_id: int,
    request: Request,
    priority: int = Form(...),
    db: Session = Depends(get_db),
):
    if not verify_admin(request):
        raise HTTPException(status_code=403, detail="Unauthorized")

    src = db.query(Source).filter(Source.id == source_id).first()
    if src:
        src.priority = max(1, min(10, priority))
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/retry-failed")
def retry_failed(request: Request, db: Session = Depends(get_db)):
    if not verify_admin(request):
        raise HTTPException(status_code=403, detail="Unauthorized")

    processor = ArticleProcessor(db)
    count = processor.retry_failed_articles()
    return RedirectResponse(url=f"/admin?success=Queued+{count}+failed+articles+for+retry", status_code=303)


@router.post("/admin/clear-failed")
def clear_failed(request: Request, db: Session = Depends(get_db)):
    if not verify_admin(request):
        raise HTTPException(status_code=403, detail="Unauthorized")

    processor = ArticleProcessor(db)
    count = processor.clear_failed_articles()
    return RedirectResponse(url=f"/admin?success=Cleared+{count}+failed+articles", status_code=303)
