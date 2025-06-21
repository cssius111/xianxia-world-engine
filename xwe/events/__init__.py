"""
事件系统
实现基于事件的解耦通信机制
"""

import asyncio
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent:
    """领域事件基类"""

    type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    correlation_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.type:
            raise ValueError("Event type cannot be empty")


# 具体事件类型
@dataclass
class GameEvent(DomainEvent):
    """游戏事件"""

    pass


@dataclass
class PlayerEvent(DomainEvent):
    """玩家事件"""

    pass


@dataclass
class CombatEvent(DomainEvent):
    """战斗事件"""

    pass


@dataclass
class WorldEvent(DomainEvent):
    """世界事件"""

    pass


@dataclass
class SystemEvent(DomainEvent):
    """系统事件"""

    pass


class IEventHandler(ABC):
    """事件处理器接口"""

    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        """处理事件"""
        pass

    @abstractmethod
    def can_handle(self, event: DomainEvent) -> bool:
        """判断是否可以处理该事件"""
        pass


class EventHandler(IEventHandler):
    """事件处理器基类"""

    def __init__(self, event_types: Optional[List[str]] = None) -> None:
        self.event_types = event_types or []
        self.logger = logger.getChild(self.__class__.__name__)

    def can_handle(self, event: DomainEvent) -> bool:
        """判断是否可以处理该事件"""
        if not self.event_types:  # 如果没有指定类型，处理所有事件
            return True
        return event.type in self.event_types

    def handle(self, event: DomainEvent) -> None:
        """处理事件"""
        if not self.can_handle(event):
            return

        try:
            self._do_handle(event)
        except Exception as e:
            self.logger.error(f"Error handling event {event.type}: {e}")

    def _do_handle(self, event: DomainEvent) -> None:
        """子类实现的处理逻辑"""
        pass


class FunctionEventHandler(EventHandler):
    """函数式事件处理器"""

    def __init__(
        self, handler_func: Callable[[DomainEvent], None], event_types: Optional[List[str]] = None
    ):
        super().__init__(event_types)
        self.handler_func = handler_func

    def _do_handle(self, event: DomainEvent) -> None:
        """调用处理函数"""
        self.handler_func(event)


class EventBus:
    """事件总线"""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[IEventHandler]] = defaultdict(list)
        self._async_handlers: Dict[str, List[IEventHandler]] = defaultdict(list)
        self._middleware: List[Callable] = []
        self._event_store: Optional["EventStore"] = None
        self.logger = logger.getChild("EventBus")

    def subscribe(self, event_type: str, handler: IEventHandler) -> None:
        """订阅事件"""
        self._handlers[event_type].append(handler)
        self.logger.debug(f"Handler subscribed to {event_type}")

    def subscribe_async(self, event_type: str, handler: IEventHandler) -> None:
        """订阅异步事件"""
        self._async_handlers[event_type].append(handler)
        self.logger.debug(f"Async handler subscribed to {event_type}")

    def subscribe_handler(self, handler: IEventHandler) -> None:
        """订阅处理器（自动识别事件类型）"""
        if hasattr(handler, "event_types"):
            for event_type in handler.event_types:
                self.subscribe(event_type, handler)
        else:
            # 订阅到所有事件
            self.subscribe("*", handler)

    def unsubscribe(self, event_type: str, handler: IEventHandler) -> None:
        """取消订阅"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

        if event_type in self._async_handlers:
            self._async_handlers[event_type].remove(handler)

    def publish(self, event: DomainEvent) -> None:
        """发布事件"""
        self.logger.debug(f"Publishing event: {event.type}")

        # 应用中间件
        for middleware in self._middleware:
            event = middleware(event)
            if event is None:
                return  # 中间件取消了事件

        # 存储事件
        if self._event_store:
            self._event_store.append(event)

        # 同步处理
        self._publish_sync(event)

        # 异步处理
        self._publish_async(event)

    def _publish_sync(self, event: DomainEvent) -> None:
        """同步发布事件"""
        # 处理特定类型的处理器
        for handler in self._handlers.get(event.type, []):
            try:
                handler.handle(event)
            except Exception as e:
                self.logger.error(f"Error in sync handler: {e}")

        # 处理通配符处理器
        for handler in self._handlers.get("*", []):
            try:
                handler.handle(event)
            except Exception as e:
                self.logger.error(f"Error in wildcard handler: {e}")

    def _publish_async(self, event: DomainEvent) -> None:
        """异步发布事件"""
        handlers = self._async_handlers.get(event.type, []) + self._async_handlers.get("*", [])

        if not handlers:
            return

        # 在新线程中处理异步事件
        def run_async() -> None:
            for handler in handlers:
                try:
                    handler.handle(event)
                except Exception as e:
                    self.logger.error(f"Error in async handler: {e}")

        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()

    def add_middleware(self, middleware: Callable[[DomainEvent], DomainEvent]) -> None:
        """添加中间件"""
        self._middleware.append(middleware)

    def set_event_store(self, event_store: "EventStore") -> None:
        """设置事件存储"""
        self._event_store = event_store


class EventStore:
    """事件存储"""

    def __init__(self, max_size: int = 10000) -> None:
        self._events: List[DomainEvent] = []
        self._max_size = max_size
        self._lock = threading.Lock()

    def append(self, event: DomainEvent) -> None:
        """添加事件"""
        with self._lock:
            self._events.append(event)

            # 限制大小
            if len(self._events) > self._max_size:
                self._events = self._events[-self._max_size // 2 :]

    def get_events(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100,
    ) -> List[DomainEvent]:
        """查询事件"""
        with self._lock:
            events = self._events

            # 过滤事件类型
            if event_type:
                events = [e for e in events if e.type == event_type]

            # 过滤时间范围
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]

            if end_time:
                events = [e for e in events if e.timestamp <= end_time]

            # 限制数量
            if limit and len(events) > limit:
                events = events[-limit:]

            return events

    def get_event_types(self) -> List[str]:
        """获取所有事件类型"""
        with self._lock:
            types = set(e.type for e in self._events)
            return sorted(list(types))

    def clear(self) -> None:
        """清空事件"""
        with self._lock:
            self._events.clear()

    def __len__(self) -> int:
        """获取事件数量"""
        return len(self._events)


class EventAggregator:
    """事件聚合器 - 用于批量处理事件"""

    def __init__(
        self,
        handler: Callable[[List[DomainEvent]], None],
        batch_size: int = 10,
        timeout: float = 1.0,
    ):
        self.handler = handler
        self.batch_size = batch_size
        self.timeout = timeout
        self._buffer: List[DomainEvent] = []
        self._lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None

    def add_event(self, event: DomainEvent) -> None:
        """添加事件到缓冲区"""
        with self._lock:
            self._buffer.append(event)

            # 检查是否需要处理
            if len(self._buffer) >= self.batch_size:
                self._process_batch()
            else:
                # 启动定时器
                if self._timer is None:
                    self._timer = threading.Timer(self.timeout, self._timeout_handler)
                    self._timer.start()

    def _timeout_handler(self) -> None:
        """超时处理"""
        with self._lock:
            self._process_batch()

    def _process_batch(self) -> None:
        """处理批量事件"""
        if not self._buffer:
            return

        # 取出事件
        events = self._buffer.copy()
        self._buffer.clear()

        # 取消定时器
        if self._timer:
            self._timer.cancel()
            self._timer = None

        # 处理事件
        try:
            self.handler(events)
        except Exception as e:
            logger.error(f"Error processing event batch: {e}")


# 全局事件总线实例
_global_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """获取全局事件总线"""
    return _global_event_bus


def publish_event(event: DomainEvent) -> None:
    """发布事件到全局事件总线"""
    _global_event_bus.publish(event)


def subscribe_event(event_type: str, handler: Callable[[DomainEvent], None]) -> None:
    """订阅全局事件"""
    handler_obj = FunctionEventHandler(handler, [event_type])
    _global_event_bus.subscribe(event_type, handler_obj)
