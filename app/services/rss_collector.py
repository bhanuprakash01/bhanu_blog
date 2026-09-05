import asyncio
import email.utils
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup
import feedparser
import httpx
import yaml

from app.config import settings
from app.models.source import Source

logger = logging.getLogger(__name__)


class DiscoveredArticleData:
    def __init__(
        self,
        title: str,
        url: str,
        source_name: str,
        source_url: str,
        published_at: datetime,
        description: Optional[str] = None,
        author: Optional[str] = None,
        image_url: Optional[str] = None,
        category: Optional[str] = None,
    ):
        self.title = title
        self.url = url
        self.source_name = source_name
        self.source_url = source_url
        self.published_at = published_at
        self.description = description
        self.author = author
        self.image_url = image_url
        self.category = category or "AI News"


class NewsDiscoveryProvider(ABC):
    """Abstract interface for discovering news items."""

    @abstractmethod
    async def discover_articles(self, sources: list[Source]) -> list[DiscoveredArticleData]:
        pass


class SearchAPIProvider(NewsDiscoveryProvider):
    """Placeholder architecture for future official Search/News API discovery."""

    async def discover_articles(self, sources: list[Source]) -> list[DiscoveredArticleData]:
        logger.info("SearchAPIProvider invoked (future extension).")
        return []


class RSSDiscoveryProvider(NewsDiscoveryProvider):
    """Production RSS feed discovery service."""

    def __init__(self):
        self.user_agent = settings.USER_AGENT
        self.timeout = settings.FEED_TIMEOUT_SECONDS

    async def discover_articles(self, sources: list[Source]) -> list[DiscoveredArticleData]:
        tasks = [self.fetch_source(src) for src in sources if src.enabled]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles: list[DiscoveredArticleData] = []
        for src, res in zip(sources, results):
            if isinstance(res, Exception):
                logger.error(f"Error fetching source {src.name}: {res}")
                src.last_status = "ERROR"
                src.last_error = str(res)[:500]
                src.consecutive_failures = (src.consecutive_failures or 0) + 1
            else:
                articles, error_msg = res
                if error_msg:
                    src.last_status = "ERROR"
                    src.last_error = error_msg[:500]
                    src.consecutive_failures = (src.consecutive_failures or 0) + 1
                else:
                    src.last_status = "OK"
                    src.last_error = None
                    src.consecutive_failures = 0
                    src.total_articles_fetched = (src.total_articles_fetched or 0) + len(articles)
                    all_articles.extend(articles)

            src.last_fetched_at = datetime.now(timezone.utc)

        return all_articles

    async def fetch_source(self, source: Source) -> tuple[list[DiscoveredArticleData], Optional[str]]:
        """
        Fetches an individual RSS feed using httpx with retries.
        Returns: (articles, error_message)
        """
        articles: list[DiscoveredArticleData] = []
        feed_content = None
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
        }

        # Up to 2 retries with exponential backoff
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.get(source.url, headers=headers)
                    if resp.status_code == 200:
                        feed_content = resp.text
                        break
                    else:
                        logger.warning(f"HTTP {resp.status_code} fetching feed {source.name} (attempt {attempt+1})")
            except httpx.TimeoutException:
                logger.warning(f"Timeout fetching feed {source.name} (attempt {attempt+1})")
            except Exception as e:
                logger.warning(f"Network error fetching {source.name} (attempt {attempt+1}): {e}")

            if attempt < 1:
                await asyncio.sleep(2)

        if not feed_content:
            return [], f"Failed to retrieve feed content from {source.url}"

        # Parse feed with feedparser
        try:
            parsed = feedparser.parse(feed_content)
            if parsed.bozo and not parsed.entries:
                return [], f"Feed parse error: {getattr(parsed, 'bozo_exception', 'Unknown parse error')}"

            for entry in parsed.entries:
                item = self._normalize_entry(entry, source)
                if item:
                    articles.append(item)

            return articles, None
        except Exception as e:
            return [], f"Exception parsing feed XML: {e}"

    def _normalize_entry(self, entry, source: Source) -> Optional[DiscoveredArticleData]:
        """Normalizes an individual feed entry into a DiscoveredArticleData object."""
        title = entry.get("title", "").strip()
        url = entry.get("link", "").strip()
        if not title or not url:
            return None

        # Determine published date
        published_at = self._parse_published_date(entry)
        if not published_at:
            published_at = datetime.now(timezone.utc)

        # Extract text description / excerpt
        description = self._extract_clean_text(entry)

        # Extract author
        author = entry.get("author") or entry.get("creator") or source.name

        # Extract image URL
        image_url = self._extract_image_url(entry)

        return DiscoveredArticleData(
            title=title,
            url=url,
            source_name=source.name,
            source_url=source.url,
            published_at=published_at,
            description=description,
            author=author,
            image_url=image_url,
            category=source.category,
        )

    def _parse_published_date(self, entry) -> Optional[datetime]:
        """Parses various RSS date representations into an aware UTC datetime."""
        # 1. feedparser parsed time tuple
        time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
        if time_struct:
            try:
                return datetime(*time_struct[:6], tzinfo=timezone.utc)
            except Exception:
                pass

        # 2. String published date via email.utils
        date_str = entry.get("published") or entry.get("updated")
        if date_str:
            try:
                parsed_tuple = email.utils.parsedate_to_datetime(date_str)
                if parsed_tuple.tzinfo is None:
                    parsed_tuple = parsed_tuple.replace(tzinfo=timezone.utc)
                return parsed_tuple.astimezone(timezone.utc)
            except Exception:
                pass

        return None

    def _extract_clean_text(self, entry) -> str:
        """Cleans HTML tags and returns a readable text snippet."""
        raw_html = ""
        if "summary" in entry:
            raw_html = entry.summary
        elif "description" in entry:
            raw_html = entry.description
        elif "content" in entry and len(entry.content) > 0:
            raw_html = entry.content[0].get("value", "")

        if not raw_html:
            return ""

        soup = BeautifulSoup(raw_html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return " ".join(text.split())[:1200]

    def _extract_image_url(self, entry) -> Optional[str]:
        """Tries multiple methods to find an article preview image."""
        # Method 1: media_content
        if "media_content" in entry and len(entry.media_content) > 0:
            for media in entry.media_content:
                url = media.get("url")
                if url and any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]) or "image" in media.get("type", ""):
                    return url

        # Method 2: enclosures
        if "enclosures" in entry and len(entry.enclosures) > 0:
            for enc in entry.enclosures:
                url = enc.get("href")
                if url and ("image" in enc.get("type", "") or any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"])):
                    return url

        # Method 3: media_thumbnail
        if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
            url = entry.media_thumbnail[0].get("url")
            if url:
                return url

        # Method 4: first <img> in HTML summary
        raw_html = entry.get("summary", "") or entry.get("description", "")
        if raw_html:
            soup = BeautifulSoup(raw_html, "html.parser")
            img = soup.find("img")
            if img and img.get("src"):
                src = img["src"]
                if src.startswith("http"):
                    return src

        return None


def sync_sources_from_yaml(db_session) -> int:
    """Reads sources.yaml and ensures all sources exist in the database."""
    yaml_path = Path(__file__).resolve().parent.parent.parent / "config" / "sources.yaml"
    if not yaml_path.exists():
        logger.warning(f"sources.yaml not found at {yaml_path}")
        return 0

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        sources_data = data.get("sources", [])
        synced = 0
        for item in sources_data:
            name = item.get("name")
            url = item.get("url")
            category = item.get("category", "AI News")
            enabled = item.get("enabled", True)
            priority = item.get("priority", 5)

            if not name or not url:
                continue

            existing = db_session.query(Source).filter(Source.url == url).first()
            if not existing:
                src = Source(
                    name=name,
                    url=url,
                    category=category,
                    enabled=enabled,
                    priority=priority,
                )
                db_session.add(src)
                synced += 1
            else:
                # Update metadata if needed
                existing.name = name
                existing.category = category
                existing.priority = priority

        db_session.commit()
        return synced
    except Exception as e:
        logger.error(f"Error syncing sources from YAML: {e}")
        db_session.rollback()
        return 0
