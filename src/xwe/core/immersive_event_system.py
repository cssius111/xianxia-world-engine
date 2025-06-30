from enum import Enum
from typing import Any, Dict, Callable


class EventType(Enum):
    """事件类型占位枚举"""

    GENERIC = "generic"


class ImmersiveEventSystem:
    """简化的沉浸式事件系统"""

    def __init__(self, output_func: Callable[[str], None]) -> None:
        self.output_func = output_func

    def start_event(self, event_name: str, context: Dict[str, Any] | None = None) -> None:
        context = context or {}
        self.output_func(f"[事件] {event_name}: {context}")


class SpecialEventHandler:
    """处理特殊事件的占位实现"""

    @staticmethod
    def handle_cultivation_event(event_system: ImmersiveEventSystem, context: Dict[str, Any], duration: int) -> int:
        """处理修炼事件，返回获得的经验值"""
        event_system.start_event("cultivation", context)
        return 10 * duration
