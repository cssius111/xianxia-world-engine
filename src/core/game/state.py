from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from src.xwe.core.character import Character


@dataclass
class GameState:
    """游戏状态"""

    player: Optional[Character] = None
    current_location: str = "qingyun_city"
    current_combat: Optional[str] = None
    game_time: float = 0.0
    active_hours: float = 0.0
    game_mode: str = "player"
    flags: Dict[str, Any] = field(default_factory=dict)
    npcs: Dict[str, Character] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player": self.player.to_dict() if self.player else None,
            "current_location": self.current_location,
            "current_combat": self.current_combat,
            "game_time": self.game_time,
            "active_hours": self.active_hours,
            "game_mode": self.game_mode,
            "flags": self.flags,
            "npcs": {nid: npc.to_dict() for nid, npc in self.npcs.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        state = cls()
        if data.get("player"):
            state.player = Character.from_dict(data["player"])
        state.current_location = data.get("current_location", "qingyun_city")
        state.current_combat = data.get("current_combat")
        state.game_time = data.get("game_time", 0.0)
        state.active_hours = data.get("active_hours", 0.0)
        state.game_mode = data.get("game_mode", "player")
        state.flags = data.get("flags", {})
        if "npcs" in data:
            state.npcs = {nid: Character.from_dict(nc) for nid, nc in data["npcs"].items()}
        return state
