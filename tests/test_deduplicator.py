from datetime import datetime, timezone
from app.models.article import Article, ProcessingStatus
from app.services.deduplicator import Deduplicator


def test_url_normalization():
    raw_url = "https://example.com/ai-breakthrough/?utm_source=twitter&utm_medium=social#heading"
    normalized = Deduplicator.normalize_url(raw_url)
    assert normalized == "https://example.com/ai-breakthrough"


def test_exact_url_duplicate(db_session):
    art = Article(
        url="https://example.com/story-1",
        canonical_url="https://example.com/story-1",
        title="Google Releases Gemini 2.5 Flash Model",
        source_name="Tech Crunch",
        content_hash=Deduplicator.compute_content_hash("Google Releases Gemini 2.5 Flash Model", "Sample description"),
        published_at=datetime.now(timezone.utc),
        processing_status=ProcessingStatus.PROCESSED,
    )
    db_session.add(art)
    db_session.commit()

    dedup = Deduplicator()
    is_dup, reason, _ = dedup.is_duplicate(
        db=db_session,
        url="https://example.com/story-1?utm_source=newsletter",
        title="Different headline title",
        description="Different content",
    )
    assert is_dup is True
    assert "URL match" in reason


def test_title_similarity_duplicate(db_session):
    art = Article(
        url="https://source-a.com/gemini-announcement",
        canonical_url="https://source-a.com/gemini-announcement",
        title="OpenAI announces GPT-5 with autonomous agents capabilities",
        source_name="Source A",
        content_hash="hash_123",
        published_at=datetime.now(timezone.utc),
        processing_status=ProcessingStatus.PROCESSED,
    )
    db_session.add(art)
    db_session.commit()

    dedup = Deduplicator()
    # Slightly reworded title from a different publisher
    is_dup, reason, _ = dedup.is_duplicate(
        db=db_session,
        url="https://source-b.com/different-url",
        title="OpenAI announces GPT 5 with autonomous agents capabilities",
        description="Completely different article text.",
    )
    assert is_dup is True
    assert "Near-duplicate title" in reason


def test_unique_article_allowed(db_session):
    art = Article(
        url="https://source-a.com/story-alpha",
        canonical_url="https://source-a.com/story-alpha",
        title="NVIDIA unveils Blackwell ultra architecture for AI supercomputing",
        source_name="NVIDIA",
        content_hash="hash_nv",
        published_at=datetime.now(timezone.utc),
        processing_status=ProcessingStatus.PROCESSED,
    )
    db_session.add(art)
    db_session.commit()

    dedup = Deduplicator()
    is_dup, reason, _ = dedup.is_duplicate(
        db=db_session,
        url="https://source-b.com/story-beta",
        title="Anthropic releases Claude 3.7 Sonnet hybrid reasoning model",
        description="Anthropic today announced new reasoning updates.",
    )
    assert is_dup is False
    assert reason is None
