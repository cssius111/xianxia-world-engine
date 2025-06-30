"""简易异步事件系统"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, List


EventHandler = Callable[..., Awaitable[None]]


class AsyncEvent:
    """异步事件"""

    def __init__(self) -> None:
        self._listeners: List[EventHandler] = []

    def connect(self, listener: EventHandler) -> None:
        self._listeners.append(listener)

    async def emit(self, *args: Any, **kwargs: Any) -> None:
        for listener in list(self._listeners):
            await listener(*args, **kwargs)


class EventBus:
    """异步事件总线"""

    def __init__(self) -> None:
        self._events: Dict[str, AsyncEvent] = defaultdict(AsyncEvent)

    def on(self, name: str) -> AsyncEvent:
        return self._events[name]


class AsyncEventSystem:
    """异步事件系统"""

    def __init__(self) -> None:
        self.bus = EventBus()

    async def emit(self, name: str, *args: Any, **kwargs: Any) -> None:
        await self.bus.on(name).emit(*args, **kwargs)

    def listener(self, name: str) -> Callable[[EventHandler], EventHandler]:
        def decorator(func: EventHandler) -> EventHandler:
            self.bus.on(name).connect(func)
            return func

        return decorator
