"""简易游戏状态管理器"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from src.xwe.core.game_core import GameState


logger = logging.getLogger(__name__)


@dataclass
class ContextInfo:
    timestamp: str
    action: str = ""


@dataclass
class GameContext:
    state: GameState
    info: ContextInfo


class GameStateManager:
    """统一管理游戏状态并记录转移"""

    def __init__(self, log_dir: str = "logs") -> None:
        self._state: Optional[GameState] = None
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger.getChild(self.__class__.__name__)

    def set_state(self, state: GameState, action: str = "") -> None:
        self._state = state
        self._log_transition(action)

    def get_state(self) -> Optional[GameState]:
        return self._state

    def _log_transition(self, action: str) -> None:
        if not self._state:
            return
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "state": self._state.to_dict(),
        }
        log_file = self.log_dir / "state_transitions.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.logger.debug("记录状态转移: %s", action)

