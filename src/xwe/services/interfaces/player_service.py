from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from src.xwe.services import IService


@dataclass
class PlayerData:
    """玩家存档数据"""

    name: str
    level: int = 1
    extra: dict[str, Any] | None = None


class IPlayerService(IService, ABC):
    """玩家服务接口"""

    @abstractmethod
    def get_player(self) -> PlayerData:
        """获取玩家数据"""
        raise NotImplementedError

    @abstractmethod
    def set_player(self, data: PlayerData) -> None:
        """设置玩家数据"""
        raise NotImplementedError
