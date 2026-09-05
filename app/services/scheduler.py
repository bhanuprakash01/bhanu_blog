import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import SessionLocal
from app.services.article_processor import ArticleProcessor

logger = logging.getLogger(__name__)


class NewsScheduler:
    """Manages periodic background news collection via APScheduler."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running_job = False
        self._lock = asyncio.Lock()
        self.last_run_time: datetime | None = None
        self.last_run_stats: dict | None = None

    def start(self):
        """Starts the APScheduler."""
        trigger = IntervalTrigger(minutes=settings.NEWS_REFRESH_MINUTES)
        self.scheduler.add_job(
            self.run_scheduled_collection,
            trigger=trigger,
            id="news_collection_job",
            name="Periodic RSS News Collector",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info(f"NewsScheduler started. Refreshing every {settings.NEWS_REFRESH_MINUTES} minutes.")

        # Schedule initial run shortly after startup (after 5 seconds)
        asyncio.create_task(self._delayed_initial_run(delay=3))

    async def _delayed_initial_run(self, delay: int = 3):
        await asyncio.sleep(delay)
        logger.info("Executing initial automatic news collection on startup...")
        await self.run_scheduled_collection()

    def shutdown(self):
        """Gracefully stops the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("NewsScheduler shut down.")

    async def run_scheduled_collection(self) -> dict:
        """Executes the collection pipeline with concurrency protection."""
        if self._lock.locked() or self.is_running_job:
            logger.warning("News collection is already in progress. Skipping duplicate invocation.")
            return {"status": "busy", "message": "News collection already running."}

        async with self._lock:
            self.is_running_job = True
            db = SessionLocal()
            try:
                processor = ArticleProcessor(db)
                stats = await processor.run_collection_cycle()
                self.last_run_time = datetime.now(timezone.utc)
                self.last_run_stats = stats
                return {"status": "success", "stats": stats}
            except Exception as e:
                logger.error(f"Error during scheduled collection: {e}", exc_info=True)
                return {"status": "error", "message": str(e)}
            finally:
                db.close()
                self.is_running_job = False

    def get_next_run_time(self) -> datetime | None:
        job = self.scheduler.get_job("news_collection_job")
        if job and job.next_run_time:
            return job.next_run_time
        return None


# Global scheduler singleton
news_scheduler = NewsScheduler()
