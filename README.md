# AI News Hub

A production-grade, self-hosted AI news aggregation and publishing platform designed to run continuously on home servers using **Proxmox VE + Docker**.

**AI News Hub** automatically collects articles and technical engineering posts from reputable Artificial Intelligence sources via an **RSS-first architecture**, normalizes and filters them for strict AI relevance, deduplicates stories across 4 intelligent layers, synthesizes deep bullet-point takeaways and impact analyses using **Google Gemini**, and serves them through a high-contrast technology publication interface.

---

## Architecture

```text
RSS FEEDS (sources.yaml / Admin UI)
       │
       ▼
Python Async RSS Collector (feedparser + aiohttp)
       │
       ▼
Article Normalizer & Canonical URL Extraction
       │
       ▼
4-Tier Deduplication Engine
 ├── Level 1: Exact URL Matching
 ├── Level 2: Canonical Parameter Stripping (utm_*, ref, etc.)
 ├── Level 3: SHA-256 Title & Excerpt Normalization Hash
 └── Level 4: Fuzzy Levenshtein & Jaccard Title Similarity (>85%)
       │
       ▼
Keyword Relevance Filter (AI/ML Term Validation + Negative Filtering)
       │
       ▼
Gemini Summarization Pipeline (google-genai SDK)
 ├── Factual Summary
 ├── 3-5 Bullet Point Key Takeaways
 ├── Why It Matters / Strategic Industry Impact
 ├── Categorization (Generative AI, LLMs, Robotics, Hardware, etc.)
 ├── Entity Tagging
 └── Importance Score (1 - 10)
       │
       ▼
Trending Calculator (Exponential Recency Decay + Importance Multiplier)
       │
       ▼
SQLite Database (WAL Mode + Thread-safe SQLAlchemy 2.x)
       │
       ▼
FastAPI Application (Uvicorn + Jinja2 Templates + Vanilla JS UI)
 ├── Modern 3-Column Responsive Editorial Interface
 ├── Real-time Search, Category Feeds, & Trending Rankings
 ├── Public RSS Feeds (/rss.xml, /rss/{category}.xml)
 ├── SEO Sitemap & Robots.txt
 └── HMAC Cookie-Protected Admin Dashboard
```

---

## Key Features

- **RSS-First Integrity**: Clean, respectful polling with custom `User-Agent` headers, ETags, and `Last-Modified` conditional requests. No fragile DOM scrapers or web search workarounds.
- **Cost-Optimized Gemini Processing**:
  - Rule-based keyword pre-filter eliminates non-AI articles *before* calling the Gemini API.
  - Skips stories older than 48 hours to protect API quotas.
  - Exponential backoff with rate-limit protection.
- **Robust 4-Level Deduplication**:
  1. Exact URL match
  2. Canonical URL normalization (removes query trackers, fragments, trailing slashes)
  3. Content SHA-256 hash
  4. SequenceMatcher & Jaccard token overlap for re-syndicated articles across different publications (>0.85 similarity threshold)
- **Trending Story Algorithm**:
  Combines an exponential half-life recency decay curve (24-hour half-life) with Gemini importance ratings (1-10), source reliability weighting, and topical cluster density.
- **Responsive Magazine UI**:
  - **Desktop (3 columns)**: Top breaking stories, curated center feed, and trending sidebar.
  - **Tablet (2 columns)**: Streamlined card grid with collapsible category filters.
  - **Mobile (1 column)**: High-performance touch targets (44px+ minimum), sticky header, and quick search.
  - **Article Modal / Detail Page**: Dedicated readability layout featuring *Why It Matters*, key bullet takeaways, and direct verified source links.
- **Admin Management & Observability**:
  - Web-based admin dashboard protected by HMAC cookie sessions.
  - Real-time job trigger (*"Fetch News Now"*).
  - Source management (enable/disable sources, adjust priorities).
  - Processing audit logs and failure troubleshooting.
- **Public Syndication**:
  - `/rss.xml` (global feed of processed stories)
  - `/rss/{category}.xml` (category-specific RSS syndication)
  - `/sitemap.xml` and `/robots.txt` for search engines.

---

## Project Structure

```text
ai-news-hub/
├── app/
│   ├── main.py                     # FastAPI application factory and lifespan manager
│   ├── config.py                   # Pydantic Settings and environment configuration
│   ├── database.py                 # SQLite engine (WAL mode) and SessionLocal
│   ├── database_seed.py            # Initial verified AI news bootstrap data
│   ├── models/
│   │   ├── article.py              # Article ORM schema & ProcessingStatus enum
│   │   ├── source.py               # RSS Source ORM schema
│   │   └── log.py                  # Processing audit log schema
│   ├── schemas/
│   │   └── article.py              # Pydantic validation models
│   ├── services/
│   │   ├── rss_collector.py        # Feed parser with timeout & safety checks
│   │   ├── deduplicator.py         # 4-tier deduplication engine
│   │   ├── relevance_filter.py     # AI keyword & disqualification filter
│   │   ├── gemini_service.py       # Google GenAI summarization & structuring
│   │   ├── trending.py             # Recency decay and trending score engine
│   │   ├── article_processor.py    # Pipeline coordinator
│   │   └── scheduler.py            # APScheduler background runner
│   ├── routes/
│   │   ├── web.py                  # HTML routes, RSS syndication, Sitemap
│   │   ├── api.py                  # REST API endpoints for articles & stats
│   │   └── admin.py                # Admin portal & authentication
│   ├── templates/                  # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── article.html
│   │   ├── category.html
│   │   ├── search.html
│   │   └── admin.html
│   └── static/
│       ├── css/style.css           # Modern editorial CSS stylesheet
│       └── js/app.js               # Modal handling, search, and admin controls
├── config/
│   └── sources.yaml                # Pre-configured AI RSS feeds with priorities
├── tests/
│   ├── conftest.py                 # In-memory test SQLite fixtures
│   ├── test_api.py                 # REST & HTML route test cases
│   ├── test_deduplicator.py        # URL normalization & duplicate detection tests
│   ├── test_relevance.py           # Keyword filter test cases
│   └── test_trending.py            # Score calculation & decay tests
├── Dockerfile                      # Production multi-stage Docker container
├── docker-compose.yml              # Proxmox / Docker deployment configuration
├── requirements.txt                # Pinned Python dependencies
└── .env.example                    # Environment variable reference
```

---

## Configuration & Environment Variables

Copy `.env.example` to `.env` and fill in your settings:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(empty)* | Google Gemini API Key for summarization and tagging |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name (`gemini-2.5-flash`, `gemini-1.5-flash`, etc.) |
| `DATABASE_URL` | `sqlite:////app/data/news.db` | SQLAlchemy SQLite database path |
| `NEWS_REFRESH_MINUTES` | `30` | Interval between automatic RSS collection runs |
| `ADMIN_USERNAME` | `admin` | Admin dashboard username |
| `ADMIN_PASSWORD` | `admin123` | Admin dashboard password (**change this!**) |
| `SECRET_KEY` | `your-secret-key-change-in-production` | Secret key used for signing admin session cookies |
| `LOG_LEVEL` | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `LOG_FILE` | `/app/logs/app.log` | Persistent log file destination |
| `PORT` | `8000` | HTTP port on which the app listens |
| `BASE_URL` | `http://localhost:8000` | Base URL used for RSS feeds and sitemap generation |

---

## Proxmox Deployment Guide

### Recommended Setup: Proxmox LXC Container with Docker

Running Docker inside an unprivileged LXC container provides ideal resource isolation, near-zero virtualization overhead, and seamless backups.

#### Step 1: Create the LXC Container in Proxmox
1. In the Proxmox Web GUI, select **Create CT**.
2. **General**:
   - Hostname: `ai-news-hub`
   - Uncheck *Unprivileged container* **OR** keep it unprivileged and enable nesting in options.
3. **Template**: Select standard `debian-12-standard` or `ubuntu-24.04-standard`.
4. **Disks**: Allocate at least **15 GB** storage.
5. **CPU / Memory**: Allocate **2 cores** and **2048 MB RAM** (1024 MB swap).
6. **Network**: Configure a static IP (e.g. `192.168.1.150/24`) or DHCP with your gateway.
7. **Options (Crucial for Docker inside LXC)**:
   - Go to `CT > Options > Features`.
   - Check **Nesting: 1** (and optionally **keyctl: 1**).

#### Step 2: Install Docker & Docker Compose inside the Container
SSH into your LXC container or open the Proxmox Console:

```bash
# Update and install Docker prerequisites
apt update && apt upgrade -y
apt install -y curl git ca-certificates gnupg

# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Enable Docker service
systemctl enable --now docker
```

#### Step 3: Clone and Configure AI News Hub
```bash
# Create application directory
mkdir -p /opt/ai-news-hub
cd /opt/ai-news-hub

# Clone your repository (or copy the project files)
git clone <your-repository-url> .

# Configure environment variables
cp .env.example .env
nano .env
```
*(Add your `GEMINI_API_KEY`, set a strong `ADMIN_PASSWORD`, and update `SECRET_KEY`)*.

#### Step 4: Create Persistent Volume Directories
```bash
mkdir -p /opt/ai-news-hub/data /opt/ai-news-hub/logs
chmod -R 755 /opt/ai-news-hub/data /opt/ai-news-hub/logs
```

#### Step 5: Start the Container
```bash
docker compose up -d --build
```

Verify the container is running and healthy:
```bash
docker compose ps
docker compose logs -f
```

Access the application in your browser:
- Public News Site: `http://192.168.1.150:8000/`
- Admin Dashboard: `http://192.168.1.150:8000/admin`
- Health Endpoint: `http://192.168.1.150:8000/health`

---

## Reverse Proxy Configuration (Nginx / Nginx Proxy Manager)

If exposing AI News Hub via your local domain or reverse proxy:

```nginx
server {
    listen 80;
    server_name news.home.arpa;

    location / {
        proxy_pass http://192.168.1.150:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
}
```

---

## Managing RSS Sources

Default RSS feeds are pre-loaded from `config/sources.yaml`. You can add new sources either by editing `config/sources.yaml` or directly from the `/admin` web interface.

Example `config/sources.yaml`:
```yaml
sources:
  - name: Google DeepMind Blog
    feed_url: https://deepmind.google/blog/rss.xml
    site_url: https://deepmind.google/blog/
    category: Generative AI
    priority: 10
    enabled: true

  - name: Anthropic Research
    feed_url: https://www.anthropic.com/news/rss
    site_url: https://www.anthropic.com/news
    category: LLMs
    priority: 10
    enabled: true
```

---

## Running Automated Tests

Run the complete test suite with `pytest`:

```bash
python3 -m pytest -v
```

All 13 test suites verify:
- Health check endpoints and API contracts
- HTML template response rendering
- 4-tier deduplication algorithms
- Keyword relevance pre-filter and disqualification rules
- Recency exponential decay and trending score calculations

---

## License

MIT License. Open source and self-hostable.
