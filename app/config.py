from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        enable_decoding=False,
    )

    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5433/ai_news_digest",
        alias="DATABASE_URL",
    )
    chroma_path: str = Field(default="./data/chroma", alias="CHROMA_PATH")
    chroma_collection: str = Field(default="ai_news_chunks", alias="CHROMA_COLLECTION")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="EMBEDDING_MODEL",
    )
    chat_model: str = Field(default="gpt-4o-mini", alias="CHAT_MODEL")

    rss_feed_urls: list[str] = Field(default_factory=list, alias="RSS_FEED_URLS")

    chunk_size: int = Field(default=1100, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=180, alias="CHUNK_OVERLAP")
    default_top_k: int = Field(default=6, alias="DEFAULT_TOP_K")

    @field_validator("rss_feed_urls", mode="before")
    @classmethod
    def parse_rss_urls(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [url.strip() for url in value.split(",") if url.strip()]
        raise TypeError("RSS_FEED_URLS must be a comma-separated string or list")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
