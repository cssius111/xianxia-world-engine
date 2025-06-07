# xwe/core/optimizations/async_event_system.py

import asyncio
from asyncio import Queue, Task
from typing import Dict, List, Set, Callable, Any, Optional
import concurrent.futures
from dataclasses import dataclass
import threading
from collections import defaultdict
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class AsyncEvent:
    """异步事件"""
    type: str
    data: Dict[str, Any]
    priority: int = 0
    timestamp: float = 0
    
    def __lt__(self, other):
        # 优先级高的先处理
        return self.priority > other.priority
        

class AsyncEventSystem:
    """高性能异步事件系统"""
    
    def __init__(self, 
                 worker_count: int = 4,
                 max_queue_size: int = 10000):
        self.worker_count = worker_count
        self.event_queue = asyncio.PriorityQueue(maxsize=max_queue_size)
        self.handlers = defaultdict(list)
        self.workers = []
        self.running = False
        
        # 线程池用于CPU密集型任务
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=worker_count
        )
        
        # 事件批处理
        self.batch_handlers = {}
        self.batch_buffers = defaultdict(list)
        self.batch_timers = {}
        
        # 统计信息
        self.stats = {
            'events_processed': 0,
            'events_failed': 0,
            'batch_processed': 0,
            'average_latency': 0
        }
        
    async def start(self):
        """启动事件系统"""
        self.running = True
        
        # 启动工作协程
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
            
        # 启动批处理定时器
        asyncio.create_task(self._batch_processor())
        
        logger.info(f"Async event system started with {self.worker_count} workers")
        
    async def stop(self):
        """停止事件系统"""
        self.running = False
        
        # 等待队列清空
        await self.event_queue.join()
        
        # 取消所有工作协程
        for worker in self.workers:
            worker.cancel()
            
        # 等待工作协程结束
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # 关闭线程池
        self.thread_pool.shutdown(wait=True)
        
        logger.info("Async event system stopped")
        
    def register_handler(self,
                        event_type: str,
                        handler: Callable,
                        priority: int = 0,
                        is_async: bool = True,
                        is_cpu_intensive: bool = False):
        """注册事件处理器"""
        
        handler_info = {
            'func': handler,
            'priority': priority,
            'is_async': is_async,
            'is_cpu_intensive': is_cpu_intensive
        }
        
        self.handlers[event_type].append(handler_info)
        # 按优先级排序
        self.handlers[event_type].sort(
            key=lambda h: h['priority'], 
            reverse=True
        )
        
        logger.debug(f"Registered handler for event type: {event_type}")
        
    def register_batch_handler(self,
                              event_type: str,
                              handler: Callable,
                              batch_size: int = 100,
                              max_wait: float = 0.1):
        """注册批处理器"""
        
        self.batch_handlers[event_type] = {
            'handler': handler,
            'batch_size': batch_size,
            'max_wait': max_wait
        }
        
        logger.debug(f"Registered batch handler for event type: {event_type}")
        
    async def emit(self, 
                   event_type: str,
                   data: Dict[str, Any],
                   priority: int = 0):
        """发送事件"""
        
        event = AsyncEvent(
            type=event_type,
            data=data,
            priority=priority,
            timestamp=time.time()
        )
        
        # 检查是否有批处理器
        if event_type in self.batch_handlers:
            await self._add_to_batch(event)
        else:
            await self.event_queue.put(event)
            
    async def _worker(self, worker_id: str):
        """工作协程"""
        
        logger.debug(f"{worker_id} started")
        
        while self.running:
            try:
                # 获取事件
                event = await asyncio.wait_for(
                    self.event_queue.get(), 
                    timeout=1.0
                )
                
                # 记录延迟
                latency = time.time() - event.timestamp
                self._update_latency(latency)
                
                # 处理事件
                await self._process_event(event)
                
                # 标记完成
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"{worker_id} error: {e}")
                self.stats['events_failed'] += 1
                
    async def _process_event(self, event: AsyncEvent):
        """处理单个事件"""
        
        handlers = self.handlers.get(event.type, [])
        
        if not handlers:
            logger.warning(f"No handlers for event type: {event.type}")
            return
        
        for handler_info in handlers:
            try:
                if handler_info['is_cpu_intensive']:
                    # CPU密集型任务放到线程池
                    await self._run_in_thread_pool(
                        handler_info['func'],
                        event
                    )
                elif handler_info['is_async']:
                    # 异步处理
                    await handler_info['func'](event)
                else:
                    # 同步处理
                    handler_info['func'](event)
                    
            except Exception as e:
                logger.error(f"Handler error for {event.type}: {e}")
                
        self.stats['events_processed'] += 1
                
    async def _run_in_thread_pool(self, func: Callable, event: AsyncEvent):
        """在线程池中运行CPU密集型任务"""
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.thread_pool,
            func,
            event
        )
        return result
        
    async def _add_to_batch(self, event: AsyncEvent):
        """添加到批处理缓冲"""
        
        event_type = event.type
        self.batch_buffers[event_type].append(event)
        
        batch_config = self.batch_handlers[event_type]
        
        # 检查是否达到批处理大小
        if len(self.batch_buffers[event_type]) >= batch_config['batch_size']:
            await self._flush_batch(event_type)
            
        # 设置定时器
        elif event_type not in self.batch_timers:
            self.batch_timers[event_type] = asyncio.create_task(
                self._batch_timeout(event_type, batch_config['max_wait'])
            )
            
    async def _batch_timeout(self, event_type: str, timeout: float):
        """批处理超时"""
        
        await asyncio.sleep(timeout)
        await self._flush_batch(event_type)
        
    async def _flush_batch(self, event_type: str):
        """刷新批处理缓冲"""
        
        if not self.batch_buffers[event_type]:
            return
            
        # 获取批处理器
        batch_handler = self.batch_handlers[event_type]['handler']
        events = self.batch_buffers[event_type].copy()
        self.batch_buffers[event_type].clear()
        
        # 取消定时器
        if event_type in self.batch_timers:
            self.batch_timers[event_type].cancel()
            del self.batch_timers[event_type]
            
        # 处理批次
        try:
            if asyncio.iscoroutinefunction(batch_handler):
                await batch_handler(events)
            else:
                batch_handler(events)
                
            self.stats['batch_processed'] += 1
            self.stats['events_processed'] += len(events)
            
        except Exception as e:
            logger.error(f"Batch handler error for {event_type}: {e}")
            self.stats['events_failed'] += len(events)
            
    async def _batch_processor(self):
        """批处理器协程"""
        
        while self.running:
            # 定期检查并刷新所有批处理缓冲
            await asyncio.sleep(1.0)
            
            for event_type in list(self.batch_handlers.keys()):
                if (event_type in self.batch_buffers and 
                    self.batch_buffers[event_type] and
                    event_type not in self.batch_timers):
                    # 重新设置定时器
                    max_wait = self.batch_handlers[event_type]['max_wait']
                    self.batch_timers[event_type] = asyncio.create_task(
                        self._batch_timeout(event_type, max_wait)
                    )
                    
    def _update_latency(self, latency: float):
        """更新延迟统计"""
        # 使用指数移动平均
        alpha = 0.1
        self.stats['average_latency'] = (
            alpha * latency + 
            (1 - alpha) * self.stats['average_latency']
        )
        
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
        
    def unregister_handler(self, event_type: str, handler: Callable):
        """注销事件处理器"""
        if event_type in self.handlers:
            self.handlers[event_type] = [
                h for h in self.handlers[event_type]
                if h['func'] != handler
            ]
            
    def clear_handlers(self, event_type: Optional[str] = None):
        """清除处理器"""
        if event_type:
            self.handlers[event_type] = []
        else:
            self.handlers.clear()


class EventBus:
    """事件总线 - 同步版本（向后兼容）"""
    
    def __init__(self):
        self.handlers = defaultdict(list)
        self.async_system = None
        
    def register(self, event_type: str, handler: Callable, priority: int = 0):
        """注册事件处理器"""
        self.handlers[event_type].append({
            'func': handler,
            'priority': priority
        })
        
        # 按优先级排序
        self.handlers[event_type].sort(
            key=lambda h: h['priority'],
            reverse=True
        )
        
    def emit(self, event_type: str, data: Dict[str, Any]):
        """发送事件（同步）"""
        for handler_info in self.handlers.get(event_type, []):
            try:
                handler_info['func'](data)
            except Exception as e:
                logger.error(f"Handler error for {event_type}: {e}")
                
    def enable_async(self, worker_count: int = 4):
        """启用异步模式"""
        self.async_system = AsyncEventSystem(worker_count=worker_count)
        
        # 将现有处理器迁移到异步系统
        for event_type, handlers in self.handlers.items():
            for handler_info in handlers:
                self.async_system.register_handler(
                    event_type,
                    handler_info['func'],
                    handler_info['priority'],
                    is_async=False  # 保持向后兼容
                )
                
    async def async_emit(self, event_type: str, data: Dict[str, Any], 
                        priority: int = 0):
        """异步发送事件"""
        if self.async_system and self.async_system.running:
            await self.async_system.emit(event_type, data, priority)
        else:
            # 降级到同步处理
            self.emit(event_type, data)
