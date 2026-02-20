from collections.abc import Iterable

import feedparser

from app.models import ArticleRecord
from app.utils import infer_category, infer_source, parse_timestamp, strip_html


def normalize_feed_entry(entry: dict, feed_url: str, feed_title: str | None = None) -> ArticleRecord | None:
    title = strip_html(entry.get("title", "")).strip()
    url = str(entry.get("link", "")).strip()
    if not title or not url:
        return None

    summary_html = entry.get("summary", "") or entry.get("description", "")
    summary = strip_html(summary_html)
    content_list = entry.get("content", [])
    content_html = ""
    if isinstance(content_list, list) and content_list:
        content_html = str(content_list[0].get("value", ""))
    content = strip_html(content_html) or summary

    published_at = parse_timestamp(
        entry.get("published")
        or entry.get("updated")
        or entry.get("pubDate")
        or entry.get("created")
    )

    category = "General"
    tags = entry.get("tags", [])
    if isinstance(tags, list) and tags:
        category = strip_html(str(tags[0].get("term", ""))) or category
    else:
        category = infer_category(title, summary)

    return ArticleRecord(
        title=title,
        url=url,
        source=infer_source(feed_url, feed_title),
        published_at=published_at,
        category=category,
        summary=summary[:1000],
        content=content[:20000],
    )


def fetch_feed_articles(feed_url: str, max_items: int = 30) -> list[ArticleRecord]:
    parsed = feedparser.parse(feed_url)
    if parsed.bozo:
        return []
    feed_title = parsed.feed.get("title")
    normalized: list[ArticleRecord] = []
    for entry in parsed.entries[:max_items]:
        record = normalize_feed_entry(entry, feed_url=feed_url, feed_title=feed_title)
        if record is not None:
            normalized.append(record)
    return normalized


def ingest_from_urls(feed_urls: Iterable[str], max_items_per_feed: int = 30) -> list[ArticleRecord]:
    records: list[ArticleRecord] = []
    for url in feed_urls:
        clean_url = url.strip()
        if not clean_url:
            continue
        records.extend(fetch_feed_articles(clean_url, max_items=max_items_per_feed))
    return records
