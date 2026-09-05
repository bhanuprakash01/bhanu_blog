import json
import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import ValidationError

from app.config import settings
from app.schemas.article import GeminiSummaryResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""You are an AI technology news editor.
Analyze the supplied article metadata and available text.
Create a concise, factual, and engaging summary for an AI news publication.

CRITICAL EDITORIAL GUIDELINES:
1. Do not invent facts.
2. Do not copy the article or reproduce copyrighted text verbatim.
3. Clearly distinguish verified facts from speculation or corporate claims.
4. Preserve important company names, model names, dates, numbers, and technical benchmarks.
5. Assign exactly one valid category from this list:
   {', '.join(settings.ALLOWED_CATEGORIES)}
6. Provide 3-5 concise bullet points in key_takeaways.
7. Provide an importance_score integer from 1 (minor update/rumor) to 10 (historic breakthrough/major frontier release).
8. The summary should allow a reader to understand the story without reading the entire article, while encouraging them to visit the original source.

Return ONLY valid JSON matching this schema:
{{
  "summary": "Concise factual summary (2-3 paragraphs)",
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "why_it_matters": "Why this development matters to AI practitioners, enterprises, or society",
  "category": "Allowed category name",
  "tags": ["AI", "OpenAI", "LLMs"],
  "importance_score": 8
}}
"""


class AIProvider(ABC):
    """Abstract interface for AI summarization providers."""

    @abstractmethod
    async def summarize_article(
        self,
        title: str,
        description: Optional[str],
        source_name: str,
        content_excerpt: Optional[str] = None,
    ) -> GeminiSummaryResponse:
        pass


class GeminiProvider(AIProvider):
    """Official Google GenAI SDK (google-genai) provider."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        self.model_name = model or os.environ.get("GEMINI_MODEL") or settings.GEMINI_MODEL
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not self.api_key:
                logger.warning("GEMINI_API_KEY is not configured. Fallback mode will be used.")
                return None
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize google-genai client: {e}")
                return None
        return self._client

    async def summarize_article(
        self,
        title: str,
        description: Optional[str],
        source_name: str,
        content_excerpt: Optional[str] = None,
    ) -> GeminiSummaryResponse:
        client = self._get_client()

        # If no API key is available, generate a clean fallback summary
        if not client:
            return self._generate_fallback(title, description, source_name)

        user_content = f"""SOURCE: {source_name}
TITLE: {title}
DESCRIPTION: {description or 'N/A'}
EXCERPT: {content_excerpt or 'N/A'}
"""

        # Retry once on failure
        for attempt in range(2):
            try:
                from google.genai import types

                response = client.models.generate_content(
                    model=self.model_name,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        response_schema=GeminiSummaryResponse,
                        temperature=0.2,
                    ),
                )

                raw_text = response.text
                if not raw_text:
                    raise ValueError("Gemini returned empty text response")

                # Parse and validate with Pydantic
                parsed = self._safe_parse_json(raw_text)
                validated = GeminiSummaryResponse.model_validate(parsed)

                # Validate category against allowed list
                if validated.category not in settings.ALLOWED_CATEGORIES:
                    matched = self._match_closest_category(validated.category)
                    validated.category = matched

                return validated

            except (ValidationError, json.JSONDecodeError) as parse_err:
                logger.warning(f"Attempt {attempt+1}: Failed to parse Gemini response: {parse_err}")
                if attempt == 1:
                    logger.error(f"Failed to produce valid summary after 2 attempts for: {title}")
                    raise
            except Exception as api_err:
                logger.warning(f"Attempt {attempt+1}: Gemini API call error: {api_err}")
                if attempt == 1:
                    raise

        raise RuntimeError(f"Could not generate summary for {title}")

    def _safe_parse_json(self, raw_text: str) -> dict:
        """Extracts and parses JSON even if wrapped in markdown codeblocks."""
        clean_text = raw_text.strip()
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?\n?", "", clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r"\n?```$", "", clean_text)
            clean_text = clean_text.strip()
        return json.loads(clean_text)

    def _match_closest_category(self, candidate: str) -> str:
        candidate_lower = (candidate or "").lower()
        for cat in settings.ALLOWED_CATEGORIES:
            if cat.lower() in candidate_lower or candidate_lower in cat.lower():
                return cat
        return "AI News"

    def _generate_fallback(self, title: str, description: Optional[str], source_name: str) -> GeminiSummaryResponse:
        """Fallback when GEMINI_API_KEY is not configured yet."""
        clean_desc = (description or "").strip()
        if len(clean_desc) < 30:
            clean_desc = f"{title}. Published by {source_name}."

        takeaways = [
            f"Original reporting published by {source_name}.",
            f"Focuses on key developments in: {title}.",
            "Configure GEMINI_API_KEY in .env to activate full AI summaries.",
        ]

        return GeminiSummaryResponse(
            summary=clean_desc,
            key_takeaways=takeaways,
            why_it_matters=f"This update from {source_name} reflects the rapid evolution of artificial intelligence technology and research.",
            category="AI News",
            tags=["AI", "Tech News", source_name],
            importance_score=6,
        )


class OllamaProvider(AIProvider):
    """Placeholder implementation for future local LLM integration via Ollama."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model

    async def summarize_article(
        self,
        title: str,
        description: Optional[str],
        source_name: str,
        content_excerpt: Optional[str] = None,
    ) -> GeminiSummaryResponse:
        raise NotImplementedError("OllamaProvider will be supported in a future update.")


def get_ai_provider() -> AIProvider:
    provider = settings.AI_PROVIDER.lower()
    if provider == "ollama":
        return OllamaProvider()
    return GeminiProvider()
