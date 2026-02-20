.DEFAULT_GOAL := help

PYTHON ?= python
PIP ?= $(PYTHON) -m pip
DOCKER_COMPOSE ?= docker compose
API_URL ?= http://localhost:8000
QUESTION ?= What happened in AI news this week?

.PHONY: help install up down migrate seed api test bootstrap ingest index digest chat outputs

help:
	@echo Available targets:
	@echo   make install    - Install Python dependencies
	@echo   make up         - Start postgres + n8n containers
	@echo   make down       - Stop containers
	@echo   make migrate    - Apply DB migration
	@echo   make seed       - Seed sample articles
	@echo   make api        - Run FastAPI app on :8000
	@echo   make test       - Run unit tests
	@echo   make bootstrap  - install + up + migrate + seed
	@echo   make ingest     - Trigger RSS ingest endpoint
	@echo   make index      - Trigger vector indexing endpoint
	@echo   make digest     - Print weekly markdown digest response
	@echo   make chat QUESTION='...' - Ask RAG chat endpoint
	@echo   make outputs    - Generate sample CSV + markdown outputs

install:
	$(PIP) install -r requirements.txt

up:
	$(DOCKER_COMPOSE) up -d postgres n8n

down:
	$(DOCKER_COMPOSE) down

migrate:
	$(PYTHON) -m scripts.run_migration

seed:
	$(PYTHON) -m scripts.seed_sample_articles

api:
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	$(PYTHON) -m pytest -q

bootstrap: install up migrate seed

ingest:
	curl -sS -X POST "$(API_URL)/ingest/rss" -H "Content-Type: application/json" -d "{}"

index:
	curl -sS -X POST "$(API_URL)/index/articles" -H "Content-Type: application/json" -d "{\"limit\": 300}"

digest:
	curl -sS "$(API_URL)/digest/weekly?days=7&group_by=category"

chat:
	curl -sS -X POST "$(API_URL)/chat" -H "Content-Type: application/json" -d "{\"question\": \"$(QUESTION)\"}"

outputs:
	$(PYTHON) -m scripts.generate_example_outputs
