"""
LLM 异步配置和工具函数
"""

import os
import asyncio
from typing import Optional, List, Any, Callable, TypeVar, Coroutine
from concurrent.futures import ThreadPoolExecutor
import logging
import queue
from collections import deque
import time
import threading

logger = logging.getLogger(__name__)

# 类型变量
T = TypeVar('T')


class AsyncConfig:
    """异步配置管理"""
    
    @staticmethod
    def get_worker_count() -> int:
        """获取异步工作线程数"""
        return int(os.getenv("LLM_ASYNC_WORKERS", "5"))
    
    @staticmethod
    def get_queue_size() -> int:
        """获取任务队列大小"""
        return int(os.getenv("LLM_ASYNC_QUEUE_SIZE", "100"))
    
    @staticmethod
    def get_timeout() -> float:
        """获取异步超时时间（秒）"""
        return float(os.getenv("LLM_ASYNC_TIMEOUT", "30.0"))
    
    @staticmethod
    def is_async_enabled() -> bool:
        """检查是否启用异步功能"""
        return os.getenv("LLM_ASYNC_ENABLED", "true").lower() == "true"


class AsyncHelper:
    """异步辅助工具"""
    
    @staticmethod
    def create_executor(max_workers: Optional[int] = None) -> ThreadPoolExecutor:
        """
        创建线程池执行器
        
        Args:
            max_workers: 最大工作线程数
            
        Returns:
            ThreadPoolExecutor 实例
        """
        if max_workers is None:
            max_workers = AsyncConfig.get_worker_count()
        
        return ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="llm_async_"
        )
    
    @staticmethod
    async def run_with_timeout(
        coro: Coroutine[Any, Any, T],
        timeout: Optional[float] = None
    ) -> T:
        """
        运行协程并设置超时
        
        Args:
            coro: 要运行的协程
            timeout: 超时时间（秒）
            
        Returns:
            协程返回值
            
        Raises:
            asyncio.TimeoutError: 超时时触发
        """
        if timeout is None:
            timeout = AsyncConfig.get_timeout()
        
        return await asyncio.wait_for(coro, timeout=timeout)
    
    @staticmethod
    async def gather_with_limit(
        tasks: List[Coroutine[Any, Any, T]],
        limit: int = 10
    ) -> List[T]:
        """
        限制并发数的 gather
        
        Args:
            tasks: 协程任务列表
            limit: 最大并发数
            
        Returns:
            结果列表
        """
        semaphore = asyncio.Semaphore(limit)
        
        async def limited_task(task):
            async with semaphore:
                return await task
        
        return await asyncio.gather(
            *[limited_task(task) for task in tasks],
            return_exceptions=True
        )
    
    @staticmethod
    def run_async_in_sync(coro: Coroutine[Any, Any, T]) -> T:
        """
        在同步代码中运行异步协程
        
        Args:
            coro: 异步协程
            
        Returns:
            协程返回值
            
        Example:
            result = run_async_in_sync(client.chat_async("hello"))
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已经在运行，创建新任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, coro)
                    return future.result()
            else:
                # 直接运行
                return loop.run_until_complete(coro)
        except RuntimeError:
            # 没有事件循环，创建新的
            return asyncio.run(coro)


class AsyncWrapper:
    """将同步或异步函数包装为异步可调用对象"""

    def __init__(self, func: Callable[..., T], executor: Optional[ThreadPoolExecutor] = None):
        self.func = func
        self._executor = executor or AsyncHelper.create_executor()
        self._own_executor = executor is None

    async def __call__(self, *args, **kwargs) -> T:
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(*args, **kwargs)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, lambda: self.func(*args, **kwargs))

    def cleanup(self) -> None:
        if self._own_executor and self._executor:
            self._executor.shutdown(wait=True)


class AsyncBatchProcessor:
    """异步批处理器"""

    def __init__(
        self,
        process_func: Callable,
        batch_size: int = 10,
        timeout: float = 1.0,
        max_concurrent_batches: int = 1,
        max_workers: int = 5
    ):
        """
        初始化批处理器
        
        Args:
            process_func: 处理函数（可以是同步或异步）
            batch_size: 批次大小
            max_workers: 最大并发数
        """
        self.process_func = process_func
        self.batch_size = batch_size
        self.timeout = timeout
        self.max_workers = max_workers
        self.max_concurrent_batches = max_concurrent_batches
        self._is_async = asyncio.iscoroutinefunction(process_func)
        self._pending: List[Any] = []
        self._futures: List[asyncio.Future] = []
        self._lock = asyncio.Lock()
        self._timer: Optional[asyncio.Task] = None
        self._semaphore = asyncio.Semaphore(max_concurrent_batches)
        self._closed = False

    async def process_batch(self, items: List[Any]) -> List[Any]:
        """
        处理一批数据
        
        Args:
            items: 要处理的数据列表
            
        Returns:
            处理结果列表
        """
        if self._is_async:
            results = await self.process_func(items)
        else:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                results = await loop.run_in_executor(executor, self.process_func, items)
        logger.info(f"批次处理完成: {len(items)} 项")
        return results

    async def _flush_locked(self) -> None:
        if not self._pending:
            return

        items = self._pending
        futures = self._futures
        self._pending = []
        self._futures = []
        if self._timer:
            self._timer.cancel()
            self._timer = None

        async def _process():
            try:
                async with self._semaphore:
                    results = await self.process_batch(items)
                    for fut, res in zip(futures, results):
                        if not fut.cancelled():
                            fut.set_result(res)
            except Exception as e:  # pragma: no cover - error path
                for fut in futures:
                    if not fut.cancelled():
                        fut.set_exception(e)

        asyncio.create_task(_process())

    def _start_timer(self) -> None:
        if self.timeout <= 0:
            return
        if self._timer and not self._timer.done():
            return

        async def _timeout():
            try:
                await asyncio.sleep(self.timeout)
                async with self._lock:
                    await self._flush_locked()
            except asyncio.CancelledError:
                pass

        self._timer = asyncio.create_task(_timeout())

    async def add_request(self, item: Any) -> asyncio.Future:
        if self._closed:
            raise RuntimeError("processor closed")
        future = asyncio.get_event_loop().create_future()
        async with self._lock:
            self._pending.append(item)
            self._futures.append(future)
            if len(self._pending) >= self.batch_size:
                await self._flush_locked()
            else:
                self._start_timer()
        return future

    async def flush(self) -> None:
        async with self._lock:
            await self._flush_locked()

    async def close(self) -> None:
        self._closed = True
        await self.flush()


class AsyncRequestQueue:
    """线程安全的请求队列"""

    def __init__(self, max_size: int = 0):
        self._queue = queue.Queue(maxsize=max_size)
        self._closed = False

    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> None:
        if self._closed:
            raise Exception("queue closed")
        self._queue.put(item, block=block, timeout=timeout)

    def put_nowait(self, item: Any) -> None:
        """非阻塞放入"""
        if self._closed:
            raise RuntimeError("Queue is closed")
        try:
            self._queue.put_nowait(item)
        except queue.Full:
            # 对于测试，返回特定的异常
            raise queue.Full("Queue is full")

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        return self._queue.get(block=block, timeout=timeout)

    def qsize(self) -> int:
        return self._queue.qsize()

    def empty(self) -> bool:
        return self._queue.empty()

    def full(self) -> bool:
        return self._queue.full()

    def close(self) -> None:
        self._closed = True


class RateLimiter:
    """简单的异步速率限制器"""

    def __init__(self, calls: int, period: float, burst: Optional[int] = None):
        self.calls = calls
        self.period = period
        self.burst = burst if burst is not None else calls
        self._lock = threading.Lock()
        self._timestamps: deque = deque()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """获取令牌
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            是否成功获取令牌
        """
        start_time = time.monotonic() if timeout is not None else None

        while True:
            with self._lock:
                now = time.monotonic()
                # 移除过期时间戳
                while self._timestamps and now - self._timestamps[0] > self.period:
                    self._timestamps.popleft()

                if len(self._timestamps) < self.burst:
                    self._timestamps.append(now)
                    return True

                wait_time = self._timestamps[0] + self.period - now

            if timeout is not None:
                elapsed = time.monotonic() - start_time
                if elapsed >= timeout:
                    return False
                wait_time = min(wait_time, timeout - elapsed)

            await asyncio.sleep(max(wait_time, 0))

    def reset(self) -> None:
        with self._lock:
            self._timestamps.clear()


# 全局执行器管理
_global_executor: Optional[ThreadPoolExecutor] = None


def get_global_executor() -> ThreadPoolExecutor:
    """获取全局线程池执行器"""
    global _global_executor
    if _global_executor is None:
        _global_executor = AsyncHelper.create_executor()
    return _global_executor


def cleanup_global_executor():
    """清理全局执行器"""
    global _global_executor
    if _global_executor is not None:
        _global_executor.shutdown(wait=True)
        _global_executor = None
        logger.info("全局异步执行器已清理")
