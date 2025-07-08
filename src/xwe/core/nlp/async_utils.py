"""
LLM 异步配置和工具函数
"""

import os
import asyncio
from typing import Optional, List, Any, Callable, TypeVar, Coroutine
from concurrent.futures import ThreadPoolExecutor
import logging

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


class AsyncBatchProcessor:
    """异步批处理器"""
    
    def __init__(
        self,
        process_func: Callable,
        batch_size: int = 10,
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
        self.max_workers = max_workers
        self._is_async = asyncio.iscoroutinefunction(process_func)
    
    async def process_batch(self, items: List[Any]) -> List[Any]:
        """
        处理一批数据
        
        Args:
            items: 要处理的数据列表
            
        Returns:
            处理结果列表
        """
        results = []
        
        # 分批处理
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            
            if self._is_async:
                # 异步处理
                batch_tasks = [self.process_func(item) for item in batch]
                batch_results = await AsyncHelper.gather_with_limit(
                    batch_tasks, 
                    self.max_workers
                )
            else:
                # 同步处理（在线程池中）
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    batch_results = await asyncio.gather(
                        *[
                            loop.run_in_executor(executor, self.process_func, item)
                            for item in batch
                        ]
                    )
            
            results.extend(batch_results)
            logger.info(f"批次处理完成: {len(batch)} 项")
        
        return results


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
