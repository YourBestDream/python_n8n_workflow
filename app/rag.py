import chromadb
from openai import OpenAI

from app.config import get_settings


SYSTEM_PROMPT = """
You are an AI news assistant. Answer using only the provided context snippets.
If context is insufficient, say so clearly.
Always include citations as absolute URLs in a final "Sources" section.
""".strip()


class RagAgent:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for chat answers")
        self.settings = settings
        self.openai = OpenAI(api_key=settings.openai_api_key)
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection
        )

    def _embed_query(self, question: str) -> list[float]:
        response = self.openai.embeddings.create(
            model=self.settings.embedding_model,
            input=question,
        )
        return response.data[0].embedding

    def _search(self, vector: list[float], top_k: int) -> dict:
        return self.collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

    def answer(self, question: str, top_k: int | None = None) -> dict:
        top_k = top_k or self.settings.default_top_k
        results = self._search(self._embed_query(question), top_k=top_k)

        docs = (results.get("documents") or [[]])[0]
        metas = (results.get("metadatas") or [[]])[0]

        contexts: list[str] = []
        citations: list[str] = []
        for idx, (doc, meta) in enumerate(zip(docs, metas), start=1):
            metadata = meta or {}
            text = str(doc or "").strip()
            url = str(metadata.get("url", "")).strip()
            source = str(metadata.get("source", "")).strip()
            if url:
                citations.append(url)
            contexts.append(f"[{idx}] {source} | {url}\n{text}")

        context_block = "\n\n".join(contexts) if contexts else "No context found."
        user_prompt = (
            f"Question:\n{question}\n\n"
            f"Retrieved context:\n{context_block}\n\n"
            "Respond with concise bullet points and include only factual claims present in context."
        )

        response = self.openai.chat.completions.create(
            model=self.settings.chat_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        answer_text = response.choices[0].message.content or ""

        unique_citations = sorted({url for url in citations if url})
        if unique_citations and "Sources:" not in answer_text:
            sources = "\n".join(f"- {url}" for url in unique_citations)
            answer_text = f"{answer_text.strip()}\n\nSources:\n{sources}"

        return {
            "answer": answer_text.strip(),
            "citations": unique_citations,
            "retrieved_chunks": len(docs),
        }
