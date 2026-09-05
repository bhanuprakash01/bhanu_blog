import hashlib
import re
import urllib.parse
from difflib import SequenceMatcher
from typing import Optional
from sqlalchemy.orm import Session
from app.models.article import Article

# Parameters to strip from URLs to compute canonical version
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "fbclid", "gclid", "msclkid", "mc_cid", "mc_eid",
    "ref", "source", "feature", "platform", "_ga", "_gl"
}


class Deduplicator:
    """
    Multi-level duplicate detection:
    Level 1: Exact URL match
    Level 2: Canonical URL normalization
    Level 3: Content/title hash
    Level 4: Near-duplicate title detection
    """

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Produces a canonical URL by removing tracking query params,
        stripping fragments, normalizing trailing slashes, and lowercasing host.
        """
        if not url:
            return ""
        parsed = urllib.parse.urlparse(url.strip())
        query_dict = urllib.parse.parse_qs(parsed.query, keep_blank_values=False)

        # Filter out tracking parameters
        clean_query = {
            k: v for k, v in query_dict.items()
            if k.lower() not in TRACKING_PARAMS
        }

        # Sort query params for deterministic canonical URL
        encoded_query = urllib.parse.urlencode(clean_query, doseq=True)

        # Normalize path: remove trailing slash unless it's just "/"
        path = parsed.path
        if len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")

        canonical = urllib.parse.urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            "",  # params
            encoded_query,
            ""   # fragment
        ))
        return canonical

    @staticmethod
    def compute_content_hash(title: str, text: Optional[str] = None) -> str:
        """
        Computes a SHA-256 hash of the normalized title and optional excerpt.
        """
        norm_title = re.sub(r"[^\w\s]", "", (title or "").lower())
        norm_title = re.sub(r"\s+", " ", norm_title).strip()

        norm_text = ""
        if text:
            norm_text = re.sub(r"[^\w\s]", "", text[:200].lower())
            norm_text = re.sub(r"\s+", " ", norm_text).strip()

        payload = f"{norm_title}::{norm_text}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def title_similarity(t1: str, t2: str) -> float:
        """
        Calculates similarity ratio between two titles after normalizing whitespace and punctuation.
        """
        def clean(s: str) -> str:
            s = re.sub(r"[^\w\s]", "", s.lower())
            return " ".join(s.split())

        s1 = clean(t1)
        s2 = clean(t2)

        if not s1 or not s2:
            return 0.0

        # Sequence matcher ratio
        seq_ratio = SequenceMatcher(None, s1, s2).ratio()

        # Token set overlap (Jaccard similarity on words)
        words1 = set(s1.split())
        words2 = set(s2.split())
        if words1 and words2:
            jaccard = len(words1 & words2) / len(words1 | words2)
        else:
            jaccard = 0.0

        return max(seq_ratio, jaccard)

    def is_duplicate(
        self,
        db: Session,
        url: str,
        title: str,
        description: Optional[str] = None,
        similarity_threshold: float = 0.85,
        recent_window_days: int = 7,
    ) -> tuple[bool, Optional[str], Optional[int]]:
        """
        Checks if an article is a duplicate across all 4 levels.
        Returns: (is_dup: bool, reason: str, existing_article_id: Optional[int])
        """
        clean_url = url.strip()
        canonical = self.normalize_url(clean_url)
        content_hash = self.compute_content_hash(title, description)

        # Level 1: Exact URL match
        match = db.query(Article).filter(Article.url == clean_url).first()
        if match:
            return True, "Exact URL match", match.id

        # Level 2: Canonical URL match
        match = db.query(Article).filter(Article.canonical_url == canonical).first()
        if match:
            return True, "Canonical URL match", match.id

        # Level 3: Content/title hash match
        match = db.query(Article).filter(Article.content_hash == content_hash).first()
        if match:
            return True, "Content hash match", match.id

        # Level 4: Near-duplicate title detection within recent window
        recent_articles = (
            db.query(Article.id, Article.title)
            .order_by(Article.published_at.desc())
            .limit(100)
            .all()
        )
        for art_id, art_title in recent_articles:
            sim = self.title_similarity(title, art_title)
            if sim >= similarity_threshold:
                return True, f"Near-duplicate title match ({sim:.2f})", art_id

        return False, None, None
