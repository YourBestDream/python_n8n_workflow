from pathlib import Path

from app.db import export_recent_articles_csv, fetch_recent_articles
from app.digest import generate_weekly_markdown


def main() -> None:
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    csv_path = outputs_dir / "sample_articles_export.csv"
    markdown_path = outputs_dir / "weekly_digest_example.md"

    exported = export_recent_articles_csv(csv_path, days=30)
    digest_md = generate_weekly_markdown(fetch_recent_articles(days=7), group_by="category")
    markdown_path.write_text(digest_md, encoding="utf-8")

    print(f"Exported {exported} rows to {csv_path}")
    print(f"Wrote digest markdown to {markdown_path}")


if __name__ == "__main__":
    main()

