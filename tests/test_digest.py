from datetime import UTC, datetime

from app.digest import generate_weekly_markdown


def test_generate_weekly_markdown_groups_by_category() -> None:
    articles = [
        {
            "title": "A",
            "url": "https://a.example",
            "source": "Source A",
            "published_at": datetime(2026, 2, 18, tzinfo=UTC),
            "category": "Research",
            "summary": "summary a",
            "content": "content a",
        },
        {
            "title": "B",
            "url": "https://b.example",
            "source": "Source B",
            "published_at": datetime(2026, 2, 19, tzinfo=UTC),
            "category": "Product",
            "summary": "summary b",
            "content": "content b",
        },
    ]
    md = generate_weekly_markdown(articles, group_by="category", now=datetime(2026, 2, 20, tzinfo=UTC))
    assert "**Week Range:** 2026-02-13 to 2026-02-20" in md
    assert "## Product" in md
    assert "## Research" in md
    assert "https://a.example" in md
    assert "https://b.example" in md
