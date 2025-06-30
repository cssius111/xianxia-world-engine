from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from xwe.services import IService


class CultivationRealm(Enum):
    MORTAL = "mortal"
    QI_REFINING = "qi_refining"
    FOUNDATION = "foundation"
    GOLDEN_CORE = "golden_core"
    NASCENT_SOUL = "nascent_soul"
    SOUL_FORMATION = "soul_formation"
    VOID_REFINEMENT = "void_refinement"
    TRIBULATION = "tribulation"
    IMMORTAL = "immortal"


class CultivationType(Enum):
    MEDITATION = "meditation"
    PILL = "pill"
    TECHNIQUE = "technique"


class SpiritualRoot(Enum):
    NONE = "none"
    METAL = "metal"
    WOOD = "wood"
    WATER = "water"
    FIRE = "fire"
    EARTH = "earth"


@dataclass
class CultivationTechnique:
    name: str
    element: SpiritualRoot = SpiritualRoot.NONE
    multiplier: float = 1.0


@dataclass
class CultivationResult:
    success: bool
    message: str = ""


@dataclass
class BreakthroughInfo:
    realm: CultivationRealm
    possible: bool
    requirements: dict[str, Any] | None = None


@dataclass
class Tribulation:
    description: str
    difficulty: int = 1


class ICultivationService(IService, ABC):
    """修炼服务接口"""

    @abstractmethod
    def cultivate(self, player: Any, technique: CultivationTechnique) -> CultivationResult:
        raise NotImplementedError

    @abstractmethod
    def check_breakthrough(self, player: Any) -> BreakthroughInfo:
        raise NotImplementedError
