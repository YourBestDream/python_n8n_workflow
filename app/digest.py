from collections.abc import Iterable
from collections import defaultdict
from datetime import UTC, datetime, timedelta


def generate_weekly_markdown(
    articles: Iterable[dict],
    group_by: str = "category",
    now: datetime | None = None,
) -> str:
    now = now or datetime.now(UTC)
    week_start = now - timedelta(days=7)
    header = (
        f"# AI News Digest\n\n"
        f"**Week Range:** {week_start.date().isoformat()} to {now.date().isoformat()}\n\n"
        f"Generated at {now.isoformat()}\n"
    )

    groups: dict[str, list[dict]] = defaultdict(list)
    for article in articles:
        group_key = str(article.get(group_by) or "Ungrouped").strip() or "Ungrouped"
        groups[group_key].append(article)

    if not groups:
        return header + "\nNo articles found for the selected window.\n"

    body_parts: list[str] = []
    for group in sorted(groups):
        body_parts.append(f"\n## {group}\n")
        group_articles = sorted(
            groups[group],
            key=lambda item: item.get("published_at"),
            reverse=True,
        )
        for article in group_articles:
            title = str(article.get("title", "Untitled")).strip()
            summary = str(article.get("summary", "")).strip()
            source = str(article.get("source", "unknown")).strip()
            url = str(article.get("url", "")).strip()
            published_at = article.get("published_at")
            if hasattr(published_at, "astimezone"):
                date_str = published_at.astimezone(UTC).date().isoformat()
            else:
                date_str = str(published_at)
            body_parts.append(
                f"- **{title}**\n"
                f"  - Summary: {summary[:260]}\n"
                f"  - Source: {source}\n"
                f"  - Date: {date_str}\n"
                f"  - URL: {url}\n"
            )

    return header + "\n".join(body_parts).strip() + "\n"
