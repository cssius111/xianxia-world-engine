# world/time_system.py
"""简单的时间系统实现"""

from __future__ import annotations

from typing import Dict, Optional


class TimeSystem:
    """管理游戏内时间流逝"""

    def __init__(self) -> None:
        # 每个动作消耗的小时数
        self.action_costs: Dict[str, float] = {
            "move_location": 1.0,
            "explore_area": 1.0,
            "cultivate_basic": 2.0,
            "npc_conversation": 0.5,
        }

    def advance_time(self, action: str, game_state: "GameState", modifiers: Optional[Dict[str, str]] = None) -> None:
        """根据动作推进时间"""
        modifiers = modifiers or {}
        hours = self.action_costs.get(action, 1.0)
        # 可根据修炼速度等修正耗时
        if "hours" in modifiers:
            try:
                hours = float(modifiers["hours"])
            except (TypeError, ValueError):
                pass
        game_state.game_time += hours
        game_state.active_hours += hours
