import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    AI_PROVIDER: str = "gemini"

    # Database
    DATABASE_URL: str = "sqlite:///./data/news.db"

    # Collection settings
    NEWS_REFRESH_MINUTES: int = 30
    ARTICLE_MAX_AGE_HOURS: int = 72
    USER_AGENT: str = "AI-News-Hub/1.0 (+https://github.com/ainewshub; home-server-collector)"
    FEED_TIMEOUT_SECONDS: int = 15

    # Admin Dashboard
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "CHANGE_ME"
    SECRET_KEY: str = "ai-news-hub-default-secret-key-please-change"

    # Observability
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # Web URL
    BASE_URL: str = "http://localhost:8000"

    # Canonical Categories
    ALLOWED_CATEGORIES: list[str] = [
        "AI News",
        "Generative AI",
        "LLMs",
        "AI Agents",
        "AI Research",
        "Robotics",
        "AI Hardware",
        "AI Coding",
        "Computer Vision",
        "Open Source AI",
        "Enterprise AI",
        "AI Regulation",
        "AI Safety",
        "Startups",
    ]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure data and logs directories exist
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)
