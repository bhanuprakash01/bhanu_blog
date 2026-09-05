import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.config import settings
from app.models.article import Article, ProcessingStatus
from app.models.processing_log import ProcessingLog
from app.models.source import Source
from app.services.deduplicator import Deduplicator
from app.services.gemini_service import get_ai_provider
from app.services.relevance_filter import RelevanceFilter
from app.services.rss_collector import RSSDiscoveryProvider, sync_sources_from_yaml
from app.services.trending import TrendingCalculator

logger = logging.getLogger(__name__)


class ArticleProcessor:
    """
    Coordinates the full news collection and summarization lifecycle:
    RSS -> Normalize -> Age Filter -> Deduplicate -> AI Relevance -> Store -> Gemini -> Trend
    """

    def __init__(self, db: Session):
        self.db = db
        self.deduplicator = Deduplicator()
        self.relevance_filter = RelevanceFilter()
        self.discovery_provider = RSSDiscoveryProvider()
        self.ai_provider = get_ai_provider()

    async def run_collection_cycle(self) -> dict:
        """Runs a complete scheduled or manual collection cycle."""
        start_time = datetime.now(timezone.utc)
        self._log("INFO", "News collection cycle started", None)

        # 1. Sync sources from sources.yaml
        synced_count = sync_sources_from_yaml(self.db)
        if synced_count > 0:
            logger.info(f"Synced {synced_count} new sources from sources.yaml")

        # 2. Load enabled sources
        sources = self.db.query(Source).filter(Source.enabled.is_(True)).all()
        if not sources:
            self._log("WARNING", "No enabled sources found in database", None)
            return {"status": "no_sources", "new_articles": 0, "processed": 0}

        # 3. Fetch RSS feeds
        logger.info(f"Fetching RSS feeds for {len(sources)} enabled sources...")
        discovered = await self.discovery_provider.discover_articles(sources)
        self.db.commit()

        stats = {
            "discovered": len(discovered),
            "duplicates_skipped": 0,
            "too_old_skipped": 0,
            "not_ai_skipped": 0,
            "new_stored": 0,
            "summarized": 0,
            "failed": 0,
        }

        # Calculate max age cutoff
        max_age_cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.ARTICLE_MAX_AGE_HOURS)

        new_articles_to_summarize: list[Article] = []

        # 4-11: Process each discovered entry
        for item in discovered:
            # Check URL validity
            if not item.url or not item.url.startswith(("http://", "https://")):
                continue

            # Check age limit
            pub_date = item.published_at
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)

            if pub_date < max_age_cutoff:
                stats["too_old_skipped"] += 1
                continue

            # Check duplicates (Levels 1 to 4)
            is_dup, dup_reason, _ = self.deduplicator.is_duplicate(
                db=self.db,
                url=item.url,
                title=item.title,
                description=item.description,
            )
            if is_dup:
                stats["duplicates_skipped"] += 1
                continue

            # Check AI Relevance filter
            is_relevant, rel_score, matched_keywords = self.relevance_filter.evaluate(
                title=item.title,
                description=item.description,
                source_category=item.category,
            )

            canonical_url = self.deduplicator.normalize_url(item.url)
            content_hash = self.deduplicator.compute_content_hash(item.title, item.description)

            # Create article record
            article = Article(
                title=item.title,
                url=item.url,
                canonical_url=canonical_url,
                source_name=item.source_name,
                source_url=item.source_url,
                author=item.author,
                published_at=pub_date,
                image_url=item.image_url,
                description=item.description,
                category=item.category,
                relevance_score=rel_score,
                content_hash=content_hash,
                processing_status=ProcessingStatus.NEW if is_relevant else ProcessingStatus.SKIPPED,
            )
            article.tags_list = matched_keywords or [item.category]

            if not is_relevant:
                stats["not_ai_skipped"] += 1
                article.failure_reason = "Filtered: Low AI relevance score"
                self.db.add(article)
                self.db.commit()
                continue

            # Save as NEW and queue for Gemini
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            stats["new_stored"] += 1
            new_articles_to_summarize.append(article)

        logger.info(f"Discovered {stats['discovered']} entries; {len(new_articles_to_summarize)} new AI articles stored for summarization.")

        # 12-15: Send new relevant articles to Gemini
        for article in new_articles_to_summarize:
            article.processing_status = ProcessingStatus.PROCESSING
            self.db.commit()

            try:
                summary_data = await self.ai_provider.summarize_article(
                    title=article.title,
                    description=article.description,
                    source_name=article.source_name,
                )

                article.summary = summary_data.summary
                article.takeaways_list = summary_data.key_takeaways
                article.why_it_matters = summary_data.why_it_matters
                article.category = summary_data.category
                article.tags_list = summary_data.tags
                article.importance_score = summary_data.importance_score
                article.processing_status = ProcessingStatus.PROCESSED
                article.gemini_processed_at = datetime.now(timezone.utc)
                stats["summarized"] += 1

            except Exception as e:
                logger.error(f"Summarization failed for article '{article.title}': {e}")
                article.processing_status = ProcessingStatus.FAILED
                article.failure_reason = str(e)[:500]
                stats["failed"] += 1
                self._log("ERROR", f"Summarization failed for '{article.title[:50]}'", str(e), article.source_name)

            self.db.commit()

        # Update trending scores
        TrendingCalculator.update_all_trending_scores(self.db)

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        completion_msg = (
            f"Collection cycle complete in {duration:.1f}s: "
            f"{stats['discovered']} found, {stats['new_stored']} new, "
            f"{stats['summarized']} summarized, {stats['duplicates_skipped']} duplicates."
        )
        logger.info(completion_msg)
        self._log("INFO", completion_msg, None)

        return stats

    def retry_failed_articles(self, limit: int = 10) -> int:
        """Retries summarization for failed articles."""
        failed_articles = (
            self.db.query(Article)
            .filter(Article.processing_status == ProcessingStatus.FAILED)
            .limit(limit)
            .all()
        )
        retried = 0
        for art in failed_articles:
            art.processing_status = ProcessingStatus.NEW
            art.failure_reason = None
            retried += 1
        self.db.commit()
        return retried

    def clear_failed_articles(self) -> int:
        """Deletes unrecoverable failed articles."""
        count = (
            self.db.query(Article)
            .filter(Article.processing_status == ProcessingStatus.FAILED)
            .delete()
        )
        self.db.commit()
        return count

    def _log(self, level: str, message: str, details: str = None, source_name: str = None):
        """Records a log entry in the database for admin observability."""
        try:
            entry = ProcessingLog(
                level=level,
                message=message[:255],
                details=details,
                source_name=source_name,
            )
            self.db.add(entry)
            self.db.commit()
        except Exception:
            self.db.rollback()
