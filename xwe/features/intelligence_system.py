"""Intelligence system for dispatching major news."""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class NewsItem:
    """Simple news item."""
    id: str
    title: str
    content: str
    raw_event: Dict[str, Any]


class IntelligenceSystem:
    """Store major news events."""

    def __init__(self) -> None:
        self.global_news: List[NewsItem] = []

    def add_global_news(self, news: NewsItem) -> None:
        self.global_news.append(news)

    def get_global_news(self) -> List[NewsItem]:
        return list(self.global_news)
