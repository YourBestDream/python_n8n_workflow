# Runbook

## 1. Purpose

This project runs an AI news pipeline with four n8n workflows:

1. RSS ingestion into PostgreSQL
2. Weekly digest generation (Markdown)
3. Vector indexing (Chroma + embeddings)
4. RAG chat agent (Webhook + Chat Trigger)

## 2. Prerequisites

- Docker Desktop (required for `docker compose` and `host.docker.internal`)
- `make` (optional, recommended)
- `.env` populated from `.env.example`

## 3. Environment Configuration

Set these in `.env`:

- `DATABASE_URL`: PostgreSQL DSN for `articles` table
- `RSS_FEED_URLS`: comma-separated RSS sources
- `CHROMA_PATH`: path for Chroma persistence
- `CHROMA_COLLECTION`: Chroma collection name
- `OPENAI_API_KEY`: OpenAI API key
- `EMBEDDING_MODEL`: embedding model name
- `CHAT_MODEL`: chat model name
- `CHUNK_SIZE`: chunk size for indexing
- `CHUNK_OVERLAP`: chunk overlap for indexing
- `DEFAULT_TOP_K`: default retrieval count for chat

## 4. Local Test Environment (Optional)

If you want to run tests outside Docker, create and use a virtual environment.

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux/macOS (bash/zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run tests (all OS):

```bash
make test
```

Equivalent:

```bash
python -m pytest -q
```

## 5. Start Services

Preferred:

```bash
make up
```

Equivalent:

```bash
docker compose up -d --build postgres api n8n
```

This starts:

- PostgreSQL on `localhost:5433`
- API on `localhost:8000`
- n8n on `localhost:5678`

The API container runs DB migration on startup, then starts Uvicorn.

## 6. Optional Migration Commands

Migration is automatic on API startup. Manual options:

```bash
docker compose exec api python -m scripts.run_migration
```

```bash
make migrate
```

## 7. Verify Services

API health:

Linux/macOS:

```bash
curl -sS http://localhost:8000/health
```

Windows (PowerShell):

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health -Method Get
```

Open n8n UI:

- `http://localhost:5678`

## 8. Import n8n Workflows

Import these files from `n8n/workflows/`:

1. `01_rss_to_db.json`
2. `02_weekly_digest_markdown.json`
3. `03_vector_indexing.json`
4. `04_rag_chat_agent.json`

## 9. Run Current Flow

### Manual run order in n8n

1. Run `01 - RSS to Database`
2. Run `03 - Vector Indexing`
3. Run `02 - Weekly Digest Markdown`
4. Run `04 - RAG Chat Agent` using either Webhook or Chat Trigger

### Equivalent API calls via Make

```bash
make ingest
make index
make digest
make chat QUESTION="What happened in AI news this week?"
```

## 10. Schedules (UTC)

- `01 - RSS to Database`: daily at 08:00
- `03 - Vector Indexing`: daily at 08:20
- `02 - Weekly Digest Markdown`: Monday at 09:00

To use schedules, set those workflows to `Active`.

## 11. RAG Chat Usage

`04 - RAG Chat Agent` supports two entry points:

1. **Webhook path** (`Chat Webhook` node):
   - POST JSON body with `question`
   - Active URL shape in n8n: `/webhook/ai-news-rag-chat`
2. **Chat Trigger** (`Chat Trigger` node):
   - Ask directly from n8n chat interface

The workflow normalizes inputs, calls API `/chat`, and returns a plain text response.
Responses are formatted for readability and may include inline source URLs in the answer text.

## 12. Outputs

- Weekly digest file: `outputs/weekly_digest_latest.md`
- Example digest file: `outputs/weekly_digest_example.md`
- Example chat transcript: `outputs/chat_transcript.md`
- Example CSV export: `outputs/sample_articles_export.csv`
- Flow screenshots: `outputs/screenshots/`

API endpoint response behavior:

- `GET /digest/weekly`: JSON including `markdown`
- `POST /chat`: JSON including `answer`, `citations`, `retrieved_chunks`
- n8n chat workflow (`04`) returns plain text to the caller

## 13. Shutdown

Preferred:

```bash
make down
```

Equivalent:

```bash
docker compose down
```

## 14. Useful Make Targets

```bash
make help
make install
make up
make down
make api
make api-local
make migrate
make seed
make test
make ingest
make index
make digest
make chat QUESTION="What product launches happened this week?"
make outputs
```
