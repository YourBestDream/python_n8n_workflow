import html
import re
from datetime import UTC, datetime
from urllib.parse import urlparse

from dateutil import parser as date_parser


TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    clean = TAG_RE.sub(" ", value)
    clean = html.unescape(clean)
    clean = WHITESPACE_RE.sub(" ", clean).strip()
    return clean


def parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    try:
        parsed = date_parser.parse(value)
    except (ValueError, TypeError):
        return datetime.now(UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def infer_source(feed_url: str, fallback: str | None = None) -> str:
    if fallback:
        fallback = fallback.strip()
        if fallback:
            return fallback
    host = urlparse(feed_url).netloc
    return host or "unknown"


def infer_category(title: str, summary: str) -> str:
    text = f"{title} {summary}".lower()
    if any(word in text for word in ("launch", "release", "product", "api")):
        return "Product"
    if any(word in text for word in ("research", "paper", "benchmark", "study")):
        return "Research"
    if any(word in text for word in ("funding", "investment", "acquire", "merger")):
        return "Business"
    if any(word in text for word in ("policy", "regulation", "law", "compliance")):
        return "Policy"
    return "General"
