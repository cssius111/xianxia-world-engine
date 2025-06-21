"""
事件系统模块

提供事件发布-订阅机制，用于实现游戏各模块之间的松耦合通信。
"""

from .dispatcher import (
    Event,
    EventDispatcher,
    EventHandler,
    EventPriority,
    get_global_dispatcher,
)

# 为了兼容性，创建 EventBus 别名
EventBus = EventDispatcher

__all__ = [
    "Event",
    "EventBus",
    "EventDispatcher",
    "EventPriority",
    "EventHandler",
    "get_global_dispatcher",
]
