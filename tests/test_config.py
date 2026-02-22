import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_parses_rss_feed_urls_from_csv_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RSS_FEED_URLS", "https://a.example/rss.xml, https://b.example/feed.xml")
    settings = Settings(_env_file=None)
    assert settings.rss_feed_urls == [
        "https://a.example/rss.xml",
        "https://b.example/feed.xml",
    ]


def test_settings_invalid_rss_feed_urls_type_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, rss_feed_urls=123)
