from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ArticleRecord:
    title: str
    url: str
    source: str
    published_at: datetime
    category: str
    summary: str
    content: str
