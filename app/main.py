import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.database import init_db, SessionLocal
from app.routes import api, web, admin
from app.services.rss_collector import sync_sources_from_yaml
from app.services.scheduler import news_scheduler

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("ai_news_hub")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes DB, syncs RSS sources, and starts scheduler."""
    logger.info("Starting AI News Hub application...")

    # 1. Initialize DB schema
    init_db()

    # 2. Sync sources from config/sources.yaml and seed initial articles if empty
    db = SessionLocal()
    try:
        synced = sync_sources_from_yaml(db)
        logger.info(f"Synchronized {synced} sources from sources.yaml")
        from app.database_seed import seed_initial_articles_if_empty
        seeded = seed_initial_articles_if_empty(db)
        if seeded:
            logger.info(f"Seeded {seeded} initial AI news articles.")
    finally:
        db.close()

    # 3. Start background news scheduler
    news_scheduler.start()

    yield

    # Shutdown
    logger.info("Shutting down AI News Hub...")
    news_scheduler.shutdown()


app = FastAPI(
    title="AI News Hub",
    description="Production-quality RSS-first AI news collector, summarizer with Gemini, deduplicator, and modern technology news publication platform.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Mount static files
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Register routers
app.include_router(web.router)
app.include_router(admin.router)
app.include_router(api.router)
