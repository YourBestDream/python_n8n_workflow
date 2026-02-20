from contextlib import contextmanager
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from app.config import get_settings
from app.models import ArticleRecord


UPSERT_SQL = """
INSERT INTO articles (
    title, url, source, published_at, category, summary, content, updated_at
)
VALUES (
    %(title)s, %(url)s, %(source)s, %(published_at)s, %(category)s, %(summary)s, %(content)s, NOW()
)
ON CONFLICT (url) DO UPDATE
SET
    title = EXCLUDED.title,
    source = EXCLUDED.source,
    published_at = EXCLUDED.published_at,
    category = EXCLUDED.category,
    summary = EXCLUDED.summary,
    content = EXCLUDED.content,
    updated_at = NOW();
"""


@contextmanager
def get_conn() -> psycopg.Connection:
    settings = get_settings()
    conn = psycopg.connect(settings.database_url, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def run_migration(sql_path: Path) -> None:
    sql_text = sql_path.read_text(encoding="utf-8")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text)
        conn.commit()


def upsert_articles(records: Iterable[ArticleRecord]) -> int:
    rows = [
        {
            "title": record.title,
            "url": record.url,
            "source": record.source,
            "published_at": record.published_at,
            "category": record.category,
            "summary": record.summary,
            "content": record.content,
        }
        for record in records
    ]
    if not rows:
        return 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(UPSERT_SQL, rows)
        conn.commit()
    return len(rows)


def fetch_recent_articles(days: int = 7) -> list[dict]:
    query = """
    SELECT id, title, url, source, published_at, category, summary, content
    FROM articles
    WHERE published_at >= (NOW() - (%(days)s * INTERVAL '1 day'))
    ORDER BY published_at DESC;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, {"days": days})
            return list(cur.fetchall())


def fetch_unindexed_articles(limit: int = 200) -> list[dict]:
    query = """
    SELECT id, title, url, source, published_at, category, summary, content
    FROM articles
    WHERE indexed_at IS NULL
    ORDER BY published_at DESC
    LIMIT %(limit)s;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, {"limit": limit})
            return list(cur.fetchall())


def mark_articles_indexed(article_ids: list[int]) -> int:
    if not article_ids:
        return 0
    query = """
    UPDATE articles
    SET indexed_at = NOW(), updated_at = NOW()
    WHERE id = ANY(%(ids)s);
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, {"ids": article_ids})
            updated = cur.rowcount or 0
        conn.commit()
    return updated


def export_recent_articles_csv(path: Path, days: int = 30) -> int:
    articles = fetch_recent_articles(days=days)
    if not articles:
        path.write_text("", encoding="utf-8")
        return 0
    headers = ["id", "title", "url", "source", "published_at", "category", "summary", "content"]
    lines = [",".join(headers)]
    for article in articles:
        values = []
        for header in headers:
            raw = article.get(header, "")
            if isinstance(raw, datetime):
                raw = raw.astimezone(UTC).isoformat()
            text = str(raw).replace('"', '""')
            values.append(f'"{text}"')
        lines.append(",".join(values))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(articles)
