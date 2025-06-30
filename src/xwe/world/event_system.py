# world/event_system.py
"""简化的世界事件系统"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from xwe.events import WorldEvent


@dataclass
class EventDefinition:
    """事件定义"""

    id: str
    name: str
    trigger: Dict[str, Any]
    intro_text: str


class EventSystem:
    """管理世界事件"""

    def __init__(self) -> None:
        self.events: Dict[str, EventDefinition] = {}

    def add_event(self, event: EventDefinition) -> None:
        self.events[event.id] = event

    def check_triggers(self, context: Dict[str, Any]) -> List[WorldEvent]:
        triggered: List[WorldEvent] = []
        for evt in self.events.values():
            if self._matches(evt.trigger, context):
                triggered.append(WorldEvent(type="world", data={"id": evt.id}))
        return triggered

    def trigger_event(self, event_id: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        evt = self.events.get(event_id)
        if not evt:
            return None
        return {"id": evt.id, "intro_text": evt.intro_text}

    @staticmethod
    def _matches(cond: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
        for key, value in cond.items():
            if key not in ctx or ctx[key] != value:
                return False
        return True
