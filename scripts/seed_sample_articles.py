from datetime import UTC, datetime, timedelta

from app.db import upsert_articles
from app.models import ArticleRecord


def sample_articles() -> list[ArticleRecord]:
    now = datetime.now(UTC)
    return [
        ArticleRecord(
            title="OpenAI releases new reasoning model for enterprise copilots",
            url="https://example.com/openai-enterprise-reasoning-model",
            source="Example AI Wire",
            published_at=now - timedelta(days=1, hours=2),
            category="Product",
            summary="OpenAI announced a new model variant focused on reliable tool use in enterprise copilots.",
            content="OpenAI introduced a new reasoning model focused on longer tool chains, observability, and enterprise controls.",
        ),
        ArticleRecord(
            title="Anthropic research team publishes long-context evaluation benchmark",
            url="https://example.com/anthropic-long-context-benchmark",
            source="Example Research Daily",
            published_at=now - timedelta(days=2, hours=4),
            category="Research",
            summary="New benchmark evaluates retrieval precision and hallucination behavior over 200K-token contexts.",
            content="Anthropic published an evaluation benchmark measuring long-context retrieval precision and error modes.",
        ),
        ArticleRecord(
            title="EU AI compliance deadline clarified for high-risk providers",
            url="https://example.com/eu-ai-compliance-high-risk-clarified",
            source="Example Policy Desk",
            published_at=now - timedelta(days=3),
            category="Policy",
            summary="Regulators clarified timeline checkpoints for technical documentation and post-market monitoring.",
            content="Regulators clarified compliance milestones for high-risk AI systems, including documentation requirements.",
        ),
        ArticleRecord(
            title="Major cloud provider launches managed vector database tier",
            url="https://example.com/cloud-managed-vector-database-tier",
            source="Example Infra Today",
            published_at=now - timedelta(days=4, hours=1),
            category="Product",
            summary="New service tier targets low-latency semantic retrieval for production RAG systems.",
            content="A major cloud provider introduced a managed vector database tier with autoscaling and SLA-backed latency.",
        ),
        ArticleRecord(
            title="Startup raises $40M to build multimodal industrial copilots",
            url="https://example.com/startup-multimodal-industrial-copilots-series-b",
            source="Example Venture Report",
            published_at=now - timedelta(days=5, hours=3),
            category="Business",
            summary="Series B funding will expand deployments for manufacturing and field-service assistants.",
            content="The startup raised funding to scale multimodal copilots for industrial diagnostics and field operations.",
        ),
    ]


def main() -> None:
    count = upsert_articles(sample_articles())
    print(f"Upserted {count} sample article records.")


if __name__ == "__main__":
    main()
