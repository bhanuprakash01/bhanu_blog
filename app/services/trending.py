import math
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.source import Source


class TrendingCalculator:
    """
    Computes trending scores for articles based on:
    1. Recency decay (exponential decay over hours)
    2. AI Importance Score (1-10 evaluated by Gemini)
    3. Source Reputation / Priority (1-10)
    4. Cluster density (count of related articles on same topic/category in 48h)
    """

    @staticmethod
    def calculate_recency_score(published_at: datetime, half_life_hours: float = 24.0) -> float:
        """Calculates exponential decay score from 0.0 to 10.0 based on elapsed hours."""
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        elapsed_hours = max(0.0, (now - published_at).total_seconds() / 3600.0)

        # Exponential decay: 10 * (0.5 ^ (hours / half_life))
        decay = math.pow(0.5, elapsed_hours / half_life_hours)
        return round(10.0 * decay, 2)

    @classmethod
    def compute_article_score(
        cls,
        published_at: datetime,
        importance_score: float = 5.0,
        source_priority: float = 5.0,
        category_density: float = 1.0,
    ) -> float:
        """Calculates a trending score (0-100) for a single article."""
        recency = cls.calculate_recency_score(published_at)
        raw_score = (
            (recency * 4.0) +
            (float(importance_score) * 3.0) +
            (float(source_priority) * 1.5) +
            (min(5.0, float(category_density) * 0.5) * 3.0)
        )
        return round(min(100.0, raw_score), 1)

    @classmethod
    def update_all_trending_scores(cls, db: Session):
        """Recalculates trending scores across recent articles in the database."""
        articles = (
            db.query(Article)
            .order_by(Article.published_at.desc())
            .limit(200)
            .all()
        )

        sources_map = {
            s.name: s.priority
            for s in db.query(Source.name, Source.priority).all()
        }

        # Category density in last 48h
        category_counts = {}
        for a in articles:
            category_counts[a.category] = category_counts.get(a.category, 0) + 1

        for a in articles:
            recency = cls.calculate_recency_score(a.published_at)
            importance = float(a.importance_score or 5)
            source_priority = float(sources_map.get(a.source_name, 5))
            related_density = min(5.0, category_counts.get(a.category, 1) * 0.5)

            # Combined weighted score:
            # Recency: 40% weight
            # Importance: 30% weight
            # Source Priority: 15% weight
            # Related Cluster: 15% weight
            raw_score = (
                (recency * 4.0) +
                (importance * 3.0) +
                (source_priority * 1.5) +
                (related_density * 3.0)
            )

            # Normalize to 0 - 100
            normalized = round(min(100.0, raw_score), 1)
            a.trending_score = normalized

        db.commit()
