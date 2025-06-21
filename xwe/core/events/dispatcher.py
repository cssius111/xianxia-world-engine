from __future__ import annotations

"""Simple event dispatch system for core modules."""

from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, List
import logging


class EventPriority(Enum):
    """Priority levels for event handlers."""

    LOW = 1
    NORMAL = 2
    HIGH = 3


@dataclass
class Event:
    """Basic event class."""

    name: str
    data: Dict[str, Any] = field(default_factory=dict)


class EventHandler:
    """Wrapper for a handler callable with priority."""

    def __init__(
        self,
        callback: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        self.callback = callback
        self.priority = priority

    def handle(self, event: Event) -> None:
        self.callback(event)


class EventDispatcher:
    """Dispatch events to subscribed handlers."""

    def __init__(self) -> None:
        self._handlers: DefaultDict[str, List[EventHandler]] = defaultdict(list)
        self.logger = logging.getLogger(self.__class__.__name__)

    def subscribe(
        self,
        event_name: str,
        handler: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        wrapper = EventHandler(handler, priority)
        handlers = self._handlers[event_name]
        handlers.append(wrapper)
        handlers.sort(key=lambda h: h.priority.value, reverse=True)

    def unsubscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        handlers = self._handlers.get(event_name, [])
        self._handlers[event_name] = [h for h in handlers if h.callback != handler]

    def dispatch(self, event: Event) -> None:
        for handler in list(self._handlers.get(event.name, [])):
            try:
                handler.handle(event)
            except Exception as exc:  # pragma: no cover - logging only
                self.logger.error("Error handling event %s: %s", event.name, exc)


_global_dispatcher = EventDispatcher()


def get_global_dispatcher() -> EventDispatcher:
    """Return the module level dispatcher."""

    return _global_dispatcher
