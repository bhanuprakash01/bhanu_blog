from datetime import datetime, timezone, timedelta
from app.services.trending import TrendingCalculator


def test_trending_recency_decay():
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    last_week = now - timedelta(days=7)

    score_fresh = TrendingCalculator.compute_article_score(published_at=now, importance_score=8, source_priority=5)
    score_yesterday = TrendingCalculator.compute_article_score(published_at=yesterday, importance_score=8, source_priority=5)
    score_old = TrendingCalculator.compute_article_score(published_at=last_week, importance_score=8, source_priority=5)

    assert score_fresh > score_yesterday
    assert score_yesterday > score_old


def test_trending_importance_multiplier():
    now = datetime.now(timezone.utc)

    score_high_imp = TrendingCalculator.compute_article_score(published_at=now, importance_score=10, source_priority=5)
    score_low_imp = TrendingCalculator.compute_article_score(published_at=now, importance_score=2, source_priority=5)

    assert score_high_imp > score_low_imp
