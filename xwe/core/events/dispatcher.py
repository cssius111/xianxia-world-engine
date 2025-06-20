"""
事件调度器 - 实现发布-订阅模式
用于游戏中各模块之间的松耦合通信
"""

import asyncio
import logging
import weakref
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """事件处理优先级"""

    LOWEST = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    HIGHEST = 4


@dataclass
class Event:
    """事件数据"""

    name: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    cancelled: bool = False

    def cancel(self) -> None:
        """取消事件传播"""
        self.cancelled = True


@dataclass
class EventHandler:
    """事件处理器包装"""

    handler: Callable
    priority: EventPriority = EventPriority.NORMAL
    once: bool = False

    def __lt__(self, other):
        """用于优先级排序"""
        return self.priority.value > other.priority.value


class EventDispatcher:
    """
    事件调度器

    特性：
    - 同步/异步事件处理
    - 事件优先级
    - 一次性监听器
    - 弱引用支持（防止内存泄漏）
    - 事件历史记录
    - 延迟事件
    """

    def __init__(self, max_history: int = 1000):
        self.listeners: Dict[str, List[EventHandler]] = defaultdict(list)
        self.async_listeners: Dict[str, List[EventHandler]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.max_history = max_history
        self._weak_refs: Dict[str, Set[weakref.ref]] = defaultdict(set)

    def on(
        self,
        event_name: str,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
        weak: bool = False,
    ) -> Callable:
        """
        订阅事件

        Args:
            event_name: 事件名称，支持通配符 *
            handler: 事件处理函数
            priority: 处理优先级
            once: 是否只触发一次
            weak: 是否使用弱引用

        Returns:
            handler，支持装饰器使用
        """
        wrapped_handler = EventHandler(handler, priority, once)

        if weak:
            # 使用弱引用
            weak_ref = weakref.ref(handler, lambda ref: self._clean_weak_ref(event_name, ref))
            self._weak_refs[event_name].add(weak_ref)
            wrapped_handler.handler = weak_ref

        if asyncio.iscoroutinefunction(handler):
            self.async_listeners[event_name].append(wrapped_handler)
            self.async_listeners[event_name].sort()
        else:
            self.listeners[event_name].append(wrapped_handler)
            self.listeners[event_name].sort()

        logger.debug(
            f"Registered handler for '{event_name}' "
            f"(priority={priority.name}, once={once}, weak={weak})"
        )

        return handler

    def off(self, event_name: str, handler: Callable) -> None:
        """
        取消订阅

        Args:
            event_name: 事件名称
            handler: 要移除的处理函数
        """
        # 从同步监听器中移除
        self.listeners[event_name] = [
            h
            for h in self.listeners[event_name]
            if h.handler != handler
            and (not isinstance(h.handler, weakref.ref) or h.handler() != handler)
        ]

        # 从异步监听器中移除
        self.async_listeners[event_name] = [
            h
            for h in self.async_listeners[event_name]
            if h.handler != handler
            and (not isinstance(h.handler, weakref.ref) or h.handler() != handler)
        ]

        # 清理弱引用
        self._weak_refs[event_name] = {
            ref for ref in self._weak_refs[event_name] if ref() != handler
        }

        logger.debug(f"Removed handler for '{event_name}'")

    def emit(
        self, event_name: str, data: Optional[Dict[str, Any]] = None, source: Optional[str] = None
    ) -> Event:
        """
        发布事件（同步）

        Args:
            event_name: 事件名称
            data: 事件数据
            source: 事件源标识

        Returns:
            发布的事件对象
        """
        event = Event(event_name, data or {}, source=source)

        # 记录历史
        self._add_to_history(event)

        # 获取所有相关的处理器
        handlers = self._get_handlers(event_name)

        # 执行处理器
        for handler in handlers:
            if event.cancelled:
                break

            try:
                if isinstance(handler.handler, weakref.ref):
                    actual_handler = handler.handler()
                    if actual_handler:
                        actual_handler(event)
                else:
                    handler.handler(event)

            except Exception as e:
                logger.error(f"Error in event handler for '{event_name}': {e}", exc_info=True)

        # 清理一次性处理器
        self._clean_once_handlers(event_name)

        return event

    async def emit_async(
        self, event_name: str, data: Optional[Dict[str, Any]] = None, source: Optional[str] = None
    ) -> Event:
        """
        发布事件（异步）

        Args:
            event_name: 事件名称
            data: 事件数据
            source: 事件源标识

        Returns:
            发布的事件对象
        """
        event = Event(event_name, data or {}, source=source)

        # 记录历史
        self._add_to_history(event)

        # 获取所有相关的处理器
        sync_handlers = self._get_handlers(event_name, async_only=False)
        async_handlers = self._get_handlers(event_name, sync_only=False)

        tasks = []

        # 处理异步处理器
        for handler in async_handlers:
            if event.cancelled:
                break

            if isinstance(handler.handler, weakref.ref):
                actual_handler = handler.handler()
                if actual_handler:
                    tasks.append(asyncio.create_task(actual_handler(event)))
            else:
                tasks.append(asyncio.create_task(handler.handler(event)))

        # 同步处理器转异步
        for handler in sync_handlers:
            if event.cancelled:
                break

            if isinstance(handler.handler, weakref.ref):
                actual_handler = handler.handler()
                if actual_handler:
                    tasks.append(asyncio.create_task(asyncio.to_thread(actual_handler, event)))
            else:
                tasks.append(asyncio.create_task(asyncio.to_thread(handler.handler, event)))

        # 等待所有任务完成
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        # 清理一次性处理器
        self._clean_once_handlers(event_name)

        return event

    def emit_delayed(
        self,
        event_name: str,
        delay: float,
        data: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
    ) -> asyncio.Task:
        """
        延迟发布事件

        Args:
            event_name: 事件名称
            delay: 延迟秒数
            data: 事件数据
            source: 事件源标识

        Returns:
            异步任务对象
        """

        async def _delayed_emit():
            await asyncio.sleep(delay)
            await self.emit_async(event_name, data, source)

        return asyncio.create_task(_delayed_emit())

    def once(self, event_name: str) -> Callable:
        """
        装饰器：一次性事件监听

        Usage:
            @dispatcher.once('game.started')
            def on_game_start(event):
                pass
        """

        def decorator(handler: Callable) -> Callable:
            self.on(event_name, handler, once=True)
            return handler

        return decorator

    def _get_handlers(
        self, event_name: str, sync_only: bool = True, async_only: bool = True
    ) -> List[EventHandler]:
        """获取事件的所有处理器"""
        handlers = []

        # 精确匹配
        if sync_only:
            handlers.extend(self.listeners.get(event_name, []))
        if async_only:
            handlers.extend(self.async_listeners.get(event_name, []))

        # 通配符匹配
        if sync_only:
            handlers.extend(self.listeners.get("*", []))
        if async_only:
            handlers.extend(self.async_listeners.get("*", []))

        # 按优先级排序
        handlers.sort()

        return handlers

    def _clean_once_handlers(self, event_name: str) -> None:
        """清理一次性处理器"""
        self.listeners[event_name] = [h for h in self.listeners[event_name] if not h.once]
        self.async_listeners[event_name] = [
            h for h in self.async_listeners[event_name] if not h.once
        ]

    def _clean_weak_ref(self, event_name: str, ref: weakref.ref) -> None:
        """清理失效的弱引用"""
        self._weak_refs[event_name].discard(ref)

        # 从监听器中移除
        self.listeners[event_name] = [
            h
            for h in self.listeners[event_name]
            if not isinstance(h.handler, weakref.ref) or h.handler != ref
        ]
        self.async_listeners[event_name] = [
            h
            for h in self.async_listeners[event_name]
            if not isinstance(h.handler, weakref.ref) or h.handler != ref
        ]

    def _add_to_history(self, event: Event) -> None:
        """添加事件到历史记录"""
        self.event_history.append(event)

        # 限制历史记录大小
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

    def get_history(self, event_name: Optional[str] = None, limit: int = 100) -> List[Event]:
        """
        获取事件历史

        Args:
            event_name: 筛选特定事件名
            limit: 返回数量限制

        Returns:
            事件列表
        """
        history = self.event_history

        if event_name:
            history = [e for e in history if e.name == event_name]

        return history[-limit:]

    def clear_listeners(self, event_name: Optional[str] = None) -> None:
        """
        清除监听器

        Args:
            event_name: 特定事件名，None表示清除所有
        """
        if event_name:
            self.listeners[event_name].clear()
            self.async_listeners[event_name].clear()
            self._weak_refs[event_name].clear()
        else:
            self.listeners.clear()
            self.async_listeners.clear()
            self._weak_refs.clear()

        logger.info(f"Cleared listeners for: {event_name or 'all events'}")


# 全局事件调度器实例（可选）
_global_dispatcher: Optional[EventDispatcher] = None


def get_global_dispatcher() -> EventDispatcher:
    """获取全局事件调度器"""
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = EventDispatcher()
    return _global_dispatcher
