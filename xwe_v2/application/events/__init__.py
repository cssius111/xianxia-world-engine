"""
XWE V2 Event System

Application layer event handling.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    """Base event class."""

    name: str
    data: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventBus:
    """Simple event bus for publishing and subscribing to events."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, handler: Callable) -> None:
        """Subscribe to an event."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """Unsubscribe from an event."""
        if event_name in self._handlers:
            self._handlers[event_name].remove(handler)

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        if event.name in self._handlers:
            for handler in self._handlers[event.name]:
                try:
                    handler(event)
                except Exception as e:
                    # Log error but don't stop other handlers
                    print(f"Error in event handler: {e}")


class EventSystemV3:
    """
    V3 Event System for compatibility with existing code.

    This wraps the new EventBus to provide the old interface.
    """

    def __init__(self):
        self.event_bus = EventBus()

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler (v1 compatibility)."""
        self.event_bus.subscribe(event_type, handler)

    def trigger(self, event_type: str, **kwargs) -> None:
        """Trigger an event (v1 compatibility)."""
        event = Event(name=event_type, data=kwargs)
        self.event_bus.publish(event)

    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event (alternative interface)."""
        event = Event(name=event_type, data=data)
        self.event_bus.publish(event)


# Global instance for compatibility
event_system = EventSystemV3()


__all__ = ["Event", "EventBus", "EventSystemV3", "event_system"]
