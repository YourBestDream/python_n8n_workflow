# Runbook

## 1. Environment Configuration

Set these in `.env`:

- `DATABASE_URL`: PostgreSQL DSN for the `articles` table
- `RSS_FEED_URLS`: comma-separated RSS sources (2-3 minimum)
- `CHROMA_PATH`: local path for ChromaDB persistence
- `CHROMA_COLLECTION`: collection name for article chunks
- `OPENAI_API_KEY`: used for embeddings + chat completion
- `EMBEDDING_MODEL`: embedding model name
- `CHAT_MODEL`: chat model name
- `CHUNK_SIZE`: characters per chunk
- `CHUNK_OVERLAP`: overlap size between chunks
- `DEFAULT_TOP_K`: default retrieval count for chat

## 2. Bring up Services

With Docker Compose:

```bash
docker compose up -d --build postgres api n8n
```

With Make:

```bash
make up
```

The `api` service runs DB migration on startup and then launches Uvicorn on port `8000`.

## 3. Apply DB Migration (manual, optional)

From API container:

```bash
docker compose exec api python -m scripts.run_migration
```

From local Python environment:

```bash
make migrate
```

## 4. Start Backend API

In Docker:

```bash
docker compose up -d api
```

```bash
make api
```

Locally (without Dockerized API):

```bash
make api-local
```

## 5. Import and Run n8n Workflows

Import files from `n8n/workflows/`:

1. `01_rss_to_db.json`
2. `02_weekly_digest_markdown.json`
3. `03_vector_indexing.json`
4. `04_rag_chat_agent.json`

Run order:

1. Run `01 - RSS to Database` (ingests + normalizes + upserts)
2. Run `03 - Vector Indexing` (chunks + embeds + upserts vectors)
3. Run `02 - Weekly Digest Markdown` (produces markdown output)
4. Activate `04 - RAG Chat Agent` and call webhook

Equivalent API triggers via Make:

```bash
make ingest
make index
make digest
make chat QUESTION="What product launches happened this week?"
```

Built-in schedules (UTC):

- `01 - RSS to Database`: daily at 08:00
- `03 - Vector Indexing`: daily at 08:20
- `02 - Weekly Digest Markdown`: Monday at 09:00

To use schedules, toggle each workflow to `Active`.

## 6. Workflow Outputs

- RSS ingestion output: node response with `db_upserts` count
- Weekly digest:
  - n8n JSON output field `markdown`
  - file output `/outputs/weekly_digest_latest.md`
- Vector indexing output: counts for selected articles and upserted chunks
- Chat output: JSON answer with `citations`

## 7. Example Chat Request

POST to active webhook URL:

```json
{
  "question": "What product launches happened this week and which sources reported them?"
}
```

## 8. Makefile Aliases

If you have `make` installed, use:

```bash
make help
make bootstrap
make api
make api-local
make ingest
make index
make digest
make chat QUESTION="What product launches happened this week?"
```

To stop services:

```bash
make down
```

Expected response shape:

```json
{
  "answer": "...",
  "citations": [
    "https://..."
  ],
  "retrieved_chunks": 6
}
```
