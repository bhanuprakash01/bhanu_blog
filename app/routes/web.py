import math
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.article import Article, ProcessingStatus
from app.models.source import Source

router = APIRouter(tags=["Web Pages"])
templates = Jinja2Templates(directory="app/templates")


def format_time_ago(dt: datetime) -> str:
    """Helper filter to render human-readable relative time (e.g. '2h ago')."""
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = (now - dt).total_seconds()

    if diff < 60:
        return "Just now"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"{minutes}m ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours}h ago"
    elif diff < 86400 * 7:
        days = int(diff / 86400)
        return f"{days}d ago"
    else:
        return dt.strftime("%b %d, %Y")


# Register custom filters
templates.env.filters["time_ago"] = format_time_ago


@router.get("/", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db)):
    """
    Renders the professional modern homepage with Hero, Top Stories,
    Latest News (3-column grid), and Trending sidebar.
    """
    # Base query for displayed articles
    base_query = db.query(Article).filter(
        Article.processing_status.in_([ProcessingStatus.PROCESSED, ProcessingStatus.NEW])
    )

    # 1. Hero story: top trending or highest importance story with image
    hero_story = (
        base_query.filter(Article.image_url.isnot(None))
        .order_by(Article.importance_score.desc(), Article.trending_score.desc(), Article.published_at.desc())
        .first()
    )
    if not hero_story:
        hero_story = base_query.order_by(Article.published_at.desc()).first()

    hero_id = hero_story.id if hero_story else 0

    # 2. Top Stories (4-6 stories)
    top_stories = (
        base_query.filter(Article.id != hero_id)
        .order_by(Article.trending_score.desc(), Article.importance_score.desc())
        .limit(4)
        .all()
    )
    top_ids = [a.id for a in top_stories] + [hero_id]

    # 3. Latest AI News grid (excluding hero and top stories)
    latest_news = (
        base_query.filter(~Article.id.in_(top_ids))
        .order_by(Article.published_at.desc())
        .limit(12)
        .all()
    )

    # 4. Trending Now sidebar
    trending_stories = (
        base_query.order_by(Article.trending_score.desc(), Article.published_at.desc())
        .limit(6)
        .all()
    )

    # Categories with count
    category_counts = {}
    for cat in settings.ALLOWED_CATEGORIES:
        count = db.query(Article).filter(Article.category == cat).count()
        category_counts[cat] = count

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "hero_story": hero_story,
            "top_stories": top_stories,
            "latest_news": latest_news,
            "trending_stories": trending_stories,
            "categories": settings.ALLOWED_CATEGORIES,
            "category_counts": category_counts,
            "active_tab": "latest",
        },
    )


@router.get("/article/{article_id}", response_class=HTMLResponse)
def article_detail(article_id: int, request: Request, db: Session = Depends(get_db)):
    """Full article view with AI summary, takeaways, impact analysis, and source link."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Related articles in same category
    related_articles = (
        db.query(Article)
        .filter(Article.category == article.category, Article.id != article.id)
        .order_by(Article.published_at.desc())
        .limit(4)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="article.html",
        context={
            "article": article,
            "related_articles": related_articles,
            "categories": settings.ALLOWED_CATEGORIES,
        },
    )


@router.get("/category/{category_name}", response_class=HTMLResponse)
def category_page(
    category_name: str,
    request: Request,
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    """Articles filtered by specific category."""
    page_size = 12
    offset = (page - 1) * page_size

    query = db.query(Article).filter(Article.category.ilike(category_name))
    total = query.count()
    articles = query.order_by(Article.published_at.desc()).offset(offset).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="category.html",
        context={
            "category_name": category_name,
            "articles": articles,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "categories": settings.ALLOWED_CATEGORIES,
        },
    )


@router.get("/trending", response_class=HTMLResponse)
def trending_page(
    request: Request,
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    """Dedicated feed sorted by Trending Score."""
    page_size = 15
    offset = (page - 1) * page_size

    query = db.query(Article).filter(
        Article.processing_status.in_([ProcessingStatus.PROCESSED, ProcessingStatus.NEW])
    )
    total = query.count()
    articles = query.order_by(Article.trending_score.desc(), Article.published_at.desc()).offset(offset).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="category.html",
        context={
            "category_name": "Trending Now",
            "articles": articles,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "categories": settings.ALLOWED_CATEGORIES,
            "is_trending": True,
        },
    )


@router.get("/search", response_class=HTMLResponse)
def search_page(
    request: Request,
    q: str = Query("", alias="q"),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    date_range: Optional[str] = Query(None),  # today, 24h, 7d, 30d
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    """Search and filter page."""
    page_size = 12
    offset = (page - 1) * page_size
    query = db.query(Article)

    clean_q = q.strip()
    if clean_q:
        term = f"%{clean_q}%"
        query = query.filter(
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

    if source and source != "All":
        query = query.filter(Article.source_name == source)

    now = datetime.now(timezone.utc)
    if date_range == "today":
        start_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        query = query.filter(Article.published_at >= start_day)
    elif date_range == "24h":
        query = query.filter(Article.published_at >= now - timedelta(hours=24))
    elif date_range == "7d":
        query = query.filter(Article.published_at >= now - timedelta(days=7))
    elif date_range == "30d":
        query = query.filter(Article.published_at >= now - timedelta(days=30))

    total = query.count()
    articles = query.order_by(Article.published_at.desc()).offset(offset).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    sources = [s.name for s in db.query(Source.name).distinct().all()]

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "q": clean_q,
            "category": category or "All",
            "source": source or "All",
            "date_range": date_range or "all",
            "articles": articles,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "categories": settings.ALLOWED_CATEGORIES,
            "sources": sources,
        },
    )


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    """Search engine crawler rules."""
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/admin/

Sitemap: {settings.BASE_URL}/sitemap.xml
"""
    return content


@router.get("/sitemap.xml", response_class=Response)
def sitemap_xml(db: Session = Depends(get_db)):
    """Dynamically generated XML sitemap for SEO."""
    articles = (
        db.query(Article.id, Article.updated_at)
        .order_by(Article.published_at.desc())
        .limit(500)
        .all()
    )

    base = settings.BASE_URL.rstrip("/")
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    # Home & Core pages
    xml.append(f'  <url><loc>{base}/</loc><lastmod>{now_str}</lastmod><changefreq>hourly</changefreq><priority>1.0</priority></url>')
    xml.append(f'  <url><loc>{base}/trending</loc><lastmod>{now_str}</lastmod><changefreq>hourly</changefreq><priority>0.9</priority></url>')

    # Categories
    for cat in settings.ALLOWED_CATEGORIES:
        xml.append(f'  <url><loc>{base}/category/{cat.replace(" ", "%20")}</loc><changefreq>daily</changefreq><priority>0.8</priority></url>')

    # Articles
    for art in articles:
        dt_str = (art.updated_at or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        xml.append(f'  <url><loc>{base}/article/{art.id}</loc><lastmod>{dt_str}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>')

    xml.append('</urlset>')
    return Response(content="\n".join(xml), media_type="application/xml")
