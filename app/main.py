from datetime import UTC, datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.db import fetch_recent_articles, fetch_unindexed_articles, mark_articles_indexed, upsert_articles
from app.digest import generate_weekly_markdown
from app.rag import RagAgent
from app.rss import ingest_from_urls
from app.vector import VectorIndexer


class IngestRequest(BaseModel):
    rss_urls: list[str] | None = Field(default=None)
    max_items_per_feed: int = Field(default=30, ge=1, le=200)


class IndexRequest(BaseModel):
    limit: int = Field(default=250, ge=1, le=2000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int | None = Field(default=None, ge=1, le=20)


app = FastAPI(title="AI News Digest + RAG Agent API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
        "chroma_collection": settings.chroma_collection,
    }


@app.post("/ingest/rss")
def ingest_rss(payload: IngestRequest) -> dict:
    settings = get_settings()
    urls = payload.rss_urls or settings.rss_feed_urls
    if not urls:
        raise HTTPException(status_code=400, detail="No RSS urls provided and RSS_FEED_URLS is empty")
    records = ingest_from_urls(urls, max_items_per_feed=payload.max_items_per_feed)
    inserted_or_updated = upsert_articles(records)
    return {
        "rss_sources": len(urls),
        "normalized_records": len(records),
        "db_upserts": inserted_or_updated,
    }


@app.get("/digest/weekly")
def weekly_digest(days: int = 7, group_by: Literal["category", "source"] = "category") -> dict:
    articles = fetch_recent_articles(days=days)
    markdown = generate_weekly_markdown(articles, group_by=group_by)
    return {
        "days": days,
        "group_by": group_by,
        "article_count": len(articles),
        "markdown": markdown,
    }


@app.post("/index/articles")
def index_articles(payload: IndexRequest) -> dict:
    articles = fetch_unindexed_articles(limit=payload.limit)
    if not articles:
        return {
            "articles_selected": 0,
            "chunks_upserted": 0,
            "articles_marked_indexed": 0,
        }
    indexer = VectorIndexer()
    chunks = indexer.index_articles(articles)
    marked = mark_articles_indexed([int(item["id"]) for item in articles])
    return {
        "articles_selected": len(articles),
        "chunks_upserted": chunks,
        "articles_marked_indexed": marked,
    }


@app.post("/chat")
def chat(payload: ChatRequest) -> dict:
    rag_agent = RagAgent()
    result = rag_agent.answer(payload.question, top_k=payload.top_k)
    return result
