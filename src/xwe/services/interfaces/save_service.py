from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.xwe.services import IService


class SaveType(Enum):
    AUTOSAVE = "autosave"
    MANUAL = "manual"


@dataclass
class SaveInfo:
    identifier: str
    type: SaveType = SaveType.MANUAL
    meta: dict[str, Any] | None = None


@dataclass
class SaveData:
    info: SaveInfo
    data: dict[str, Any]


class ISaveService(IService, ABC):
    """存档服务接口"""

    @abstractmethod
    def save(self, data: SaveData) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, identifier: str) -> SaveData | None:
        raise NotImplementedError
