from pathlib import Path

from app.db import run_migration


def main() -> None:
    migration = Path("migrations/001_create_articles.sql")
    run_migration(migration)
    print(f"Applied migration: {migration}")


if __name__ == "__main__":
    main()

