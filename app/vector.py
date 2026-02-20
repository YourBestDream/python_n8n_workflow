from collections.abc import Iterable
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import chromadb
from openai import OpenAI

from app.config import get_settings


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    if overlap >= size:
        overlap = max(0, size // 5)
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = start + size
        chunks.append(clean[start:end])
        if end >= len(clean):
            break
        start = max(0, end - overlap)
    return chunks


class VectorIndexer:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for vector indexing")

        self.settings = settings
        self.openai = OpenAI(api_key=settings.openai_api_key)
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection
        )

    def _embed(self, texts: list[str]) -> list[list[float]]:
        response = self.openai.embeddings.create(
            model=self.settings.embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def _article_chunks(self, article: dict) -> list[tuple[str, dict[str, Any]]]:
        base_text = (
            f"{article.get('title', '')}\n\n"
            f"{article.get('content') or article.get('summary') or ''}"
        )
        chunks = chunk_text(
            base_text,
            size=self.settings.chunk_size,
            overlap=self.settings.chunk_overlap,
        )
        output: list[tuple[str, dict[str, Any]]] = []
        for idx, chunk in enumerate(chunks):
            output.append(
                (
                    chunk,
                    {
                        "article_id": int(article["id"]),
                        "source": str(article.get("source", "")),
                        "category": str(article.get("category", "")),
                        "published_at": str(article.get("published_at", "")),
                        "url": str(article.get("url", "")),
                        "title": str(article.get("title", "")),
                        "chunk_index": idx,
                    },
                )
            )
        return output

    def index_articles(self, articles: Iterable[dict]) -> int:
        prepared: list[tuple[str, dict[str, Any]]] = []
        for article in articles:
            prepared.extend(self._article_chunks(article))
        if not prepared:
            return 0

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []
        for text, payload in prepared:
            point_id = str(
                uuid5(
                    NAMESPACE_URL,
                    f"{payload['article_id']}:{payload['chunk_index']}:{payload['url']}",
                )
            )
            ids.append(point_id)
            documents.append(text)
            metadatas.append(payload)

        embeddings = self._embed(documents)
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return len(ids)
