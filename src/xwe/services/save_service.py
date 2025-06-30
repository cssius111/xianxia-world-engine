from __future__ import annotations

import json
from pathlib import Path
from typing import List

from src.xwe.services import ServiceBase, ServiceContainer
from src.xwe.services.interfaces.save_service import ISaveService, SaveData, SaveInfo, SaveType


class SaveService(ServiceBase["SaveService"], ISaveService):
    def __init__(self, container: ServiceContainer, save_dir: str | None = None) -> None:
        super().__init__(container)
        self.save_dir = Path(save_dir or "saves")
        self.save_dir.mkdir(exist_ok=True)

    def save(self, data: SaveData) -> None:
        path = self.save_dir / f"{data.info.identifier}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(data.data, f, ensure_ascii=False, indent=2)

    def load(self, identifier: str) -> SaveData | None:
        path = self.save_dir / f"{identifier}.json"
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            content = json.load(f)
        return SaveData(info=SaveInfo(identifier=identifier), data=content)

    def list_saves(self) -> List[SaveInfo]:
        infos: List[SaveInfo] = []
        for file in self.save_dir.glob("*.json"):
            infos.append(SaveInfo(identifier=file.stem))
        return infos

    def _do_initialize(self) -> None:
        self.logger.debug("SaveService initialized")

    def _do_shutdown(self) -> None:
        self.logger.debug("SaveService shutdown")
