import re
from typing import Optional

# High-weight AI terms
PRIMARY_AI_KEYWORDS = {
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "large language model",
    "llm",
    "llms",
    "generative ai",
    "genai",
    "chatgpt",
    "gemini",
    "claude",
    "openai",
    "anthropic",
    "deepmind",
    "hugging face",
    "neural network",
    "neural networks",
    "transformers",
    "transformer architecture",
    "diffusion model",
    "stable diffusion",
    "midjourney",
    "ai agent",
    "ai agents",
    "agentic",
    "coding agent",
    "coding agents",
    "copilot",
    "ai safety",
    "ai alignment",
    "ai regulation",
    "frontier model",
    "foundation model",
    "multimodal",
    "reasoning model",
}

# Secondary keywords (strong signals when in tech context)
SECONDARY_AI_KEYWORDS = {
    "ai",
    "nlp",
    "computer vision",
    "robotics",
    "humanoid",
    "gpu",
    "gpus",
    "tpu",
    "npu",
    "ai chip",
    "ai chips",
    "nvidia",
    "cuda",
    "pytorch",
    "tensorflow",
    "reinforcement learning",
    "fine-tuning",
    "rag",
    "retrieval augmented generation",
    "prompt engineering",
    "synthetic data",
    "superalignment",
    "agi",
    "artificial general intelligence",
    "autonomous agent",
}

# Negative/irrelevant terms to avoid false positives (e.g. Adobe Illustrator "AI" files)
DISQUALIFYING_PATTERNS = [
    r"\.ai\s+file",
    r"adobe\s+illustrator",
    r"save\s+as\s+\.ai",
]


class RelevanceFilter:
    """
    Lightweight rule-based relevance filter to determine if an RSS article
    is AI-related BEFORE invoking the Gemini API.
    """

    def __init__(self):
        # Precompile regexes for fast matching
        # Word boundary matching is critical for short acronyms like 'ai'
        self.primary_regexes = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            for kw in PRIMARY_AI_KEYWORDS
        ]
        self.secondary_regexes = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            for kw in SECONDARY_AI_KEYWORDS
        ]
        self.disqualify_regexes = [
            re.compile(p, re.IGNORECASE)
            for p in DISQUALIFYING_PATTERNS
        ]

    def evaluate(
        self,
        title: str,
        description: Optional[str] = None,
        source_category: Optional[str] = None,
    ) -> tuple[bool, float, list[str]]:
        """
        Evaluates an article's AI relevance.
        Returns:
            (is_relevant: bool, score: float between 0.0 and 1.0, matched_keywords: list[str])
        """
        text = f"{title or ''} {description or ''}".lower()

        # Check disqualifying patterns first
        for pat in self.disqualify_regexes:
            if pat.search(text):
                return False, 0.0, []

        matches = set()
        score = 0.0

        # Title matches carry 3x weight
        title_text = (title or "").lower()
        for kw, regex in zip(PRIMARY_AI_KEYWORDS, self.primary_regexes):
            if regex.search(title_text):
                matches.add(kw)
                score += 3.0
            elif regex.search(text):
                matches.add(kw)
                score += 1.5

        for kw, regex in zip(SECONDARY_AI_KEYWORDS, self.secondary_regexes):
            if regex.search(title_text):
                matches.add(kw)
                score += 2.0
            elif regex.search(text):
                matches.add(kw)
                score += 1.0

        # If the source category is explicitly AI and there is at least one mild hit
        if source_category and "ai" in source_category.lower() and score > 0:
            score += 1.0

        # Normalize score between 0.0 and 1.0 (threshold of 1.5 needed for relevance)
        normalized_score = min(1.0, round(score / 5.0, 2))
        is_relevant = score >= 1.5

        return is_relevant, normalized_score, list(matches)

    def is_relevant(
        self,
        title: str,
        description: Optional[str] = None,
        source_category: Optional[str] = None,
    ) -> tuple[bool, str, float]:
        """Convenience method returning (is_relevant, reason, score)."""
        rel, score, matches = self.evaluate(title, description, source_category)
        reason = f"Passed keyword criteria: {', '.join(matches)}" if rel else "No recognized AI keywords found"
        return rel, reason, score

