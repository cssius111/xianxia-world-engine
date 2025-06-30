from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.xwe.services import IService


class CombatResult(Enum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"


@dataclass
class CombatSummary:
    result: CombatResult
    details: Any | None = None


class ICombatService(IService, ABC):
    """战斗服务接口"""

    @abstractmethod
    def engage(self, attacker: Any, defender: Any) -> CombatSummary:
        """进行战斗并返回结果"""
        raise NotImplementedError
