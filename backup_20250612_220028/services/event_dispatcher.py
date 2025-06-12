"""
事件分发器服务
提供高层的事件分发和管理功能
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass, field
import time
import logging
from collections import defaultdict, deque
import threading

from . import ServiceBase, ServiceContainer
from ..events import (
    DomainEvent, EventBus, EventStore, EventHandler,
    GameEvent, PlayerEvent, CombatEvent, WorldEvent, SystemEvent
)


@dataclass
class EventStatistics:
    """事件统计信息"""
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    events_per_minute: float = 0.0
    average_processing_time: float = 0.0
    failed_events: int = 0


class IEventDispatcher(ABC):
    """事件分发器接口"""
    
    @abstractmethod
    def dispatch(self, event: DomainEvent) -> None:
        """分发事件"""
        pass
        
    @abstractmethod
    def dispatch_async(self, event: DomainEvent) -> None:
        """异步分发事件"""
        pass
        
    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None],
                  priority: int = 0) -> None:
        """订阅事件"""
        pass
        
    @abstractmethod
    def unsubscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """取消订阅"""
        pass
        
    @abstractmethod
    def get_event_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[DomainEvent]:
        """获取事件历史"""
        pass
        
    @abstractmethod
    def get_statistics(self) -> EventStatistics:
        """获取事件统计信息"""
        pass
        
    @abstractmethod
    def clear_history(self) -> None:
        """清空历史记录"""
        pass


class EventDispatcher(ServiceBase[IEventDispatcher], IEventDispatcher):
    """事件分发器实现"""
    
    def __init__(self, container: ServiceContainer):
        super().__init__(container)
        self._event_bus: Optional[EventBus] = None
        self._event_store: Optional[EventStore] = None
        self._statistics = EventStatistics()
        self._event_queue: deque = deque(maxlen=1000)
        self._processing_times: deque = deque(maxlen=100)
        self._start_time = time.time()
        self._lock = threading.RLock()
        self._subscriber_map: Dict[str, List[Callable]] = defaultdict(list)
        
    def _do_initialize(self) -> None:
        """初始化服务"""
        # 创建事件总线和存储
        self._event_bus = EventBus()
        self._event_store = EventStore(max_size=10000)
        
        # 设置事件存储
        self._event_bus.set_event_store(self._event_store)
        
        # 添加统计中间件
        self._event_bus.add_middleware(self._statistics_middleware)
        
        # 注册内置事件处理器
        self._register_builtin_handlers()
        
        self.logger.info("Event dispatcher initialized")
        
    def _register_builtin_handlers(self) -> None:
        """注册内置事件处理器"""
        # 系统事件处理器
        system_handler = SystemEventHandler()
        self._event_bus.subscribe_handler(system_handler)
        
        # 日志事件处理器
        log_handler = LogEventHandler()
        self._event_bus.subscribe_handler(log_handler)
        
    def _statistics_middleware(self, event: DomainEvent) -> DomainEvent:
        """统计中间件"""
        start_time = time.time()
        
        with self._lock:
            # 更新统计信息
            self._statistics.total_events += 1
            
            if event.type not in self._statistics.events_by_type:
                self._statistics.events_by_type[event.type] = 0
            self._statistics.events_by_type[event.type] += 1
            
            # 记录到队列
            self._event_queue.append({
                'timestamp': event.timestamp,
                'type': event.type
            })
            
        # 记录处理时间（在事件处理后）
        def record_time() -> Any:
            processing_time = time.time() - start_time
            with self._lock:
                self._processing_times.append(processing_time)
                
        # 延迟记录
        threading.Timer(0.01, record_time).start()
        
        return event
        
    def dispatch(self, event: DomainEvent) -> None:
        """分发事件"""
        try:
            self._event_bus.publish(event)
            self.logger.debug(f"Dispatched event: {event.type}")
        except Exception as e:
            self.logger.error(f"Error dispatching event {event.type}: {e}")
            with self._lock:
                self._statistics.failed_events += 1
                
    def dispatch_async(self, event: DomainEvent) -> None:
        """异步分发事件"""
        def async_dispatch() -> None:
            try:
                self.dispatch(event)
            except Exception as e:
                self.logger.error(f"Error in async dispatch: {e}")
                
        thread = threading.Thread(target=async_dispatch, daemon=True)
        thread.start()
        
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None],
                  priority: int = 0) -> None:
        """订阅事件"""
        # 创建事件处理器包装
        from ..events import FunctionEventHandler
        handler_wrapper = FunctionEventHandler(handler, [event_type])
        
        # 注册到事件总线
        self._event_bus.subscribe(event_type, handler_wrapper)
        
        # 记录订阅关系
        with self._lock:
            self._subscriber_map[event_type].append(handler)
            
        self.logger.info(f"Subscribed handler to event: {event_type}")
        
    def unsubscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """取消订阅"""
        # 从订阅关系中移除
        with self._lock:
            if event_type in self._subscriber_map:
                self._subscriber_map[event_type].remove(handler)
                
        self.logger.info(f"Unsubscribed handler from event: {event_type}")
        
    def get_event_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[DomainEvent]:
        """获取事件历史"""
        return self._event_store.get_events(
            event_type=event_type,
            limit=limit
        )
        
    def get_statistics(self) -> EventStatistics:
        """获取事件统计信息"""
        with self._lock:
            # 计算每分钟事件数
            elapsed_time = time.time() - self._start_time
            if elapsed_time > 0:
                self._statistics.events_per_minute = (
                    self._statistics.total_events / elapsed_time * 60
                )
                
            # 计算平均处理时间
            if self._processing_times:
                self._statistics.average_processing_time = (
                    sum(self._processing_times) / len(self._processing_times)
                )
                
            return EventStatistics(
                total_events=self._statistics.total_events,
                events_by_type=dict(self._statistics.events_by_type),
                events_per_minute=self._statistics.events_per_minute,
                average_processing_time=self._statistics.average_processing_time,
                failed_events=self._statistics.failed_events
            )
            
    def clear_history(self) -> None:
        """清空历史记录"""
        self._event_store.clear()
        
        with self._lock:
            self._event_queue.clear()
            
        self.logger.info("Event history cleared")
        
    # 便捷方法
    def dispatch_game_event(self, event_type: str, data: Dict[str, Any],
                           source: Optional[str] = None) -> None:
        """分发游戏事件"""
        event = GameEvent(event_type, data, source=source)
        self.dispatch(event)
        
    def dispatch_player_event(self, event_type: str, data: Dict[str, Any],
                             player_id: Optional[str] = None) -> None:
        """分发玩家事件"""
        if player_id:
            data['player_id'] = player_id
        event = PlayerEvent(event_type, data)
        self.dispatch(event)
        
    def dispatch_combat_event(self, event_type: str, data: Dict[str, Any],
                             combat_id: Optional[str] = None) -> None:
        """分发战斗事件"""
        if combat_id:
            data['combat_id'] = combat_id
        event = CombatEvent(event_type, data)
        self.dispatch(event)
        
    def dispatch_world_event(self, event_type: str, data: Dict[str, Any],
                            location: Optional[str] = None) -> None:
        """分发世界事件"""
        if location:
            data['location'] = location
        event = WorldEvent(event_type, data)
        self.dispatch(event)
        
    def dispatch_system_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """分发系统事件"""
        event = SystemEvent(event_type, data)
        self.dispatch(event)


class SystemEventHandler(EventHandler):
    """系统事件处理器"""
    
    def __init__(self):
        super().__init__(event_types=[
            'system_startup',
            'system_shutdown',
            'error_occurred',
            'performance_warning'
        ])
        
    def _do_handle(self, event: DomainEvent) -> None:
        """处理系统事件"""
        if event.type == 'system_startup':
            self.logger.info("System started")
        elif event.type == 'system_shutdown':
            self.logger.info("System shutting down")
        elif event.type == 'error_occurred':
            self.logger.error(f"System error: {event.data.get('error', 'Unknown error')}")
        elif event.type == 'performance_warning':
            self.logger.warning(f"Performance warning: {event.data.get('message', 'Unknown issue')}")


class LogEventHandler(EventHandler):
    """日志事件处理器"""
    
    def __init__(self):
        super().__init__()  # 处理所有事件
        self.event_log = []
        self.max_log_size = 1000
        
    def _do_handle(self, event: DomainEvent) -> None:
        """记录事件到日志"""
        log_entry = {
            'timestamp': event.timestamp,
            'type': event.type,
            'source': event.source,
            'data': event.data
        }
        
        self.event_log.append(log_entry)
        
        # 限制日志大小
        if len(self.event_log) > self.max_log_size:
            self.event_log = self.event_log[-self.max_log_size // 2:]
            
        # 根据事件类型记录不同级别的日志
        if event.type.startswith('error_'):
            self.logger.error(f"Event: {event.type} - {event.data}")
        elif event.type.startswith('warning_'):
            self.logger.warning(f"Event: {event.type} - {event.data}")
        else:
            self.logger.debug(f"Event: {event.type}")
