
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

"""情报系统
提供全球新闻和个人情报的管理接口"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class IntelItem:
    """单条情报或新闻"""

    id: str
    title: str
    content: str
    ttl: int
    raw_event: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    interactable_task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def is_expired(self) -> bool:
        return (datetime.now() - self.created_at).total_seconds() > self.ttl

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "ttl": self.ttl,
            "category": self.category,
            "interactable_task_id": self.interactable_task_id,
            "created_at": self.created_at.isoformat(),
        }


class IntelligenceSystem:
    """情报系统管理器"""

    def __init__(self) -> None:
        self.global_news: List[IntelItem] = []
        self.personal_intel: Dict[str, List[IntelItem]] = {}

    def add_global_news(self, item: IntelItem) -> None:
        """添加全球新闻"""
        self.global_news.append(item)
        self._cleanup()

    def add_personal_intel(self, player_id: str, item: IntelItem) -> None:
        """为指定玩家添加个人情报"""
        self.personal_intel.setdefault(player_id, []).append(item)
        self._cleanup()

    def get_global_news(self) -> List[IntelItem]:
        self._cleanup()
        return list(self.global_news)

    def get_personal_intel(self, player_id: str) -> List[IntelItem]:
        self._cleanup()
        return list(self.personal_intel.get(player_id, []))

    def _cleanup(self) -> None:
        """清理过期情报"""
        self.global_news = [n for n in self.global_news if not n.is_expired()]
        empty_players = []
        for pid, items in self.personal_intel.items():
            valid = [i for i in items if not i.is_expired()]
            if valid:
                self.personal_intel[pid] = valid
            else:
                empty_players.append(pid)
        for pid in empty_players:
            self.personal_intel.pop(pid, None)


# 全局实例
intelligence_system = IntelligenceSystem()


def integrate_intelligence_system(game_core) -> None:
    """将情报系统集成到游戏核心"""

    def push_global(news_data: Dict[str, str]) -> None:
        item = IntelItem(**news_data)
        intelligence_system.add_global_news(item)
        game_core.output(f"【情报】{item.title}")

    def push_personal(news_data: Dict[str, str], player_id: Optional[str] = None) -> None:
        pid = player_id or getattr(game_core.game_state.player, "id", "player")
        item = IntelItem(**news_data)
        intelligence_system.add_personal_intel(pid, item)
        if game_core.game_state.player and pid == game_core.game_state.player.id:
            game_core.output(f"【密闻】{item.title}")

    def wrapped_process_command(text: str) -> None:
        intelligence_system._cleanup()
        original_process_command(text)

    original_process_command = game_core.process_command
    game_core.process_command = wrapped_process_command
    game_core.push_global_news = push_global
    game_core.push_personal_intel = push_personal

    game_core.output("情报系统已就绪")
