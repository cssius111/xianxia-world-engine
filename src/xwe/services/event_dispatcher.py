from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from xwe.events import DomainEvent, get_event_bus
from xwe.services import ServiceContainer
from xwe.services import ServiceBase


@dataclass
class EventStatistics:
    published: int = 0
    handled: int = 0


class IEventDispatcher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        raise NotImplementedError


class EventDispatcher(ServiceBase["EventDispatcher"], IEventDispatcher):
    def __init__(self, container: ServiceContainer) -> None:
        super().__init__(container)
        self._bus = get_event_bus()
        self.stats = EventStatistics()

    def publish(self, event: DomainEvent) -> None:
        self._bus.publish(event)
        self.stats.published += 1

    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        self._bus.subscribe(event_type, handler)

    def _do_initialize(self) -> None:
        self.logger.debug("EventDispatcher initialized")

    def _do_shutdown(self) -> None:
        self.logger.debug("EventDispatcher shutdown")
