from datetime import datetime, timezone
from app.models.article import Article, ProcessingStatus


def test_health_check_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"


def test_categories_endpoint(client):
    res = client.get("/api/categories")
    assert res.status_code == 200
    cats = res.json()
    assert isinstance(cats, list)
    assert any(c["name"] == "Generative AI" for c in cats)


def test_articles_list_and_search(client, db_session):
    art = Article(
        url="https://example.com/claude-test",
        canonical_url="https://example.com/claude-test",
        title="Anthropic launches Claude with deep reasoning benchmarks",
        source_name="Anthropic",
        category="Generative AI",
        summary="A breakthrough in model reasoning and agent tool execution.",
        importance_score=9,
        trending_score=85.5,
        content_hash="hash_claude",
        published_at=datetime.now(timezone.utc),
        processing_status=ProcessingStatus.PROCESSED,
    )
    db_session.add(art)
    db_session.commit()

    # Query articles API
    res = client.get("/api/articles")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any(item["title"] == art.title for item in data["items"])

    # Query search API
    search_res = client.get("/api/search?q=Claude")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total"] >= 1
    assert search_data["items"][0]["title"] == art.title

    # Query single article
    single_res = client.get(f"/api/articles/{art.id}")
    assert single_res.status_code == 200
    assert single_res.json()["category"] == "Generative AI"


def test_web_html_routes(client, db_session):
    # Test Homepage
    home = client.get("/")
    assert home.status_code == 200
    assert "AI News Hub" in home.text

    # Test Trending page
    trending = client.get("/trending")
    assert trending.status_code == 200

    # Test Category page
    cat_page = client.get("/category/Generative AI")
    assert cat_page.status_code == 200
