import json
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class GeminiSummaryResponse(BaseModel):
    summary: str = Field(..., description="A concise factual summary of the article")
    key_takeaways: list[str] = Field(
        default_factory=list,
        description="3-5 bullet point takeaways"
    )
    why_it_matters: str = Field(
        ...,
        description="Why this development matters to the AI field or industry"
    )
    category: str = Field(
        ...,
        description="Assigned category from the allowed categories list"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Relevant AI keywords and entity tags"
    )
    importance_score: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Importance score from 1 to 10"
    )


class ArticleBase(BaseModel):
    title: str
    url: str
    canonical_url: str
    source_name: str
    source_url: Optional[str] = None
    author: Optional[str] = None
    published_at: datetime
    image_url: Optional[str] = None
    description: Optional[str] = None
    category: str = "AI News"
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v: Any) -> list[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if item]
            except Exception:
                pass
            return [t.strip() for t in v.split(",") if t.strip()]
        return []


class ArticleResponse(ArticleBase):
    id: int
    summary: Optional[str] = None
    key_takeaways: list[str] = Field(default_factory=list)
    why_it_matters: Optional[str] = None
    importance_score: int = 5
    relevance_score: float = 1.0
    trending_score: float = 0.0
    processing_status: str
    discovered_at: datetime
    gemini_processed_at: Optional[datetime] = None

    @field_validator("key_takeaways", mode="before")
    @classmethod
    def parse_takeaways(cls, v: Any) -> list[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if item]
            except Exception:
                pass
            return [item.strip() for item in v.split("\n") if item.strip()]
        return []

    model_config = ConfigDict(from_attributes=True)
