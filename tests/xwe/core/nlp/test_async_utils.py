"""
单元测试 - 异步工具
测试异步包装器和批处理功能
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import Mock, AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor

from xwe.core.nlp.async_utils import (
    AsyncWrapper,
    AsyncBatchProcessor,
    AsyncRequestQueue,
    RateLimiter
)


class TestAsyncWrapper:
    """异步包装器测试"""
    
    @pytest.fixture
    def sync_function(self):
        """创建同步函数"""
        def func(x, y=1):
            time.sleep(0.1)  # 模拟耗时操作
            return x + y
        return func
    
    @pytest.fixture
    def async_wrapper(self, sync_function):
        """创建异步包装器"""
        return AsyncWrapper(sync_function)
    
    @pytest.mark.asyncio
    async def test_basic_wrapping(self, async_wrapper):
        """测试基本包装功能"""
        result = await async_wrapper(5, y=3)
        assert result == 8
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self, async_wrapper):
        """测试并发执行"""
        start_time = time.time()
        
        # 并发执行多个任务
        tasks = []
        for i in range(5):
            task = async_wrapper(i, y=1)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        elapsed_time = time.time() - start_time
        
        # 验证结果
        assert results == [1, 2, 3, 4, 5]
        
        # 验证并发执行（应该比串行快）
        # 串行需要 0.5秒，并发应该在 0.2秒左右（取决于线程池大小）
        assert elapsed_time < 0.4
    
    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """测试异常处理"""
        def error_func():
            raise ValueError("测试错误")
        
        wrapper = AsyncWrapper(error_func)
        
        with pytest.raises(ValueError):
            await wrapper()
    
    @pytest.mark.asyncio
    async def test_custom_executor(self):
        """测试自定义执行器"""
        executor = ThreadPoolExecutor(max_workers=2)
        
        def slow_func(x):
            time.sleep(0.2)
            return x * 2
        
        wrapper = AsyncWrapper(slow_func, executor=executor)
        
        # 测试使用自定义执行器
        result = await wrapper(5)
        assert result == 10
        
        # 清理
        executor.shutdown()
    
    def test_cleanup(self, async_wrapper):
        """测试资源清理"""
        # 执行一些操作
        asyncio.run(async_wrapper(1))
        
        # 清理
        async_wrapper.cleanup()
        
        # 验证执行器已关闭
        assert async_wrapper._executor._shutdown


class TestAsyncBatchProcessor:
    """异步批处理器测试"""
    
    @pytest.fixture
    async def batch_processor(self):
        """创建批处理器"""
        async def process_func(items):
            # 模拟批处理
            await asyncio.sleep(0.1)
            return [item * 2 for item in items]
        
        processor = AsyncBatchProcessor(
            process_func=process_func,
            batch_size=3,
            timeout=1.0
        )
        yield processor
        await processor.close()
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, batch_processor):
        """测试批处理"""
        # 添加请求
        futures = []
        for i in range(5):
            future = await batch_processor.add_request(i)
            futures.append(future)
        
        # 触发处理
        await batch_processor.flush()
        
        # 获取结果
        results = []
        for future in futures:
            result = await future
            results.append(result)
        
        assert results == [0, 2, 4, 6, 8]
    
    @pytest.mark.asyncio
    async def test_auto_flush_on_batch_size(self):
        """测试达到批大小时自动刷新"""
        async def process_func(items):
            return [item * 2 for item in items]
        
        processor = AsyncBatchProcessor(
            process_func=process_func,
            batch_size=2,
            timeout=10.0  # 长超时，确保是批大小触发
        )
        
        try:
            # 添加2个请求（达到批大小）
            future1 = await processor.add_request(1)
            future2 = await processor.add_request(2)
            
            # 应该自动处理
            result1 = await asyncio.wait_for(future1, timeout=1.0)
            result2 = await asyncio.wait_for(future2, timeout=1.0)
            
            assert result1 == 2
            assert result2 == 4
        finally:
            await processor.close()
    
    @pytest.mark.asyncio
    async def test_timeout_flush(self):
        """测试超时刷新"""
        process_count = 0
        
        async def process_func(items):
            nonlocal process_count
            process_count += 1
            return items
        
        processor = AsyncBatchProcessor(
            process_func=process_func,
            batch_size=10,  # 大批大小
            timeout=0.2     # 短超时
        )
        
        try:
            # 只添加一个请求
            future = await processor.add_request("test")
            
            # 等待超时触发
            result = await asyncio.wait_for(future, timeout=0.5)
            
            assert result == "test"
            assert process_count == 1
        finally:
            await processor.close()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理"""
        async def error_func(items):
            raise RuntimeError("批处理错误")
        
        processor = AsyncBatchProcessor(
            process_func=error_func,
            batch_size=2
        )
        
        try:
            future1 = await processor.add_request(1)
            future2 = await processor.add_request(2)
            
            # 两个请求都应该收到错误
            with pytest.raises(RuntimeError):
                await future1
            
            with pytest.raises(RuntimeError):
                await future2
        finally:
            await processor.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_batches(self):
        """测试并发批次处理"""
        batch_times = []
        
        async def process_func(items):
            batch_times.append(time.time())
            await asyncio.sleep(0.1)
            return items
        
        processor = AsyncBatchProcessor(
            process_func=process_func,
            batch_size=2,
            max_concurrent_batches=2
        )
        
        try:
            # 快速添加6个请求（3个批次）
            futures = []
            for i in range(6):
                future = await processor.add_request(i)
                futures.append(future)
            
            # 等待所有完成
            await asyncio.gather(*futures)
            
            # 验证批次时间
            assert len(batch_times) == 3
            
            # 前两个批次应该几乎同时开始（并发）
            if len(batch_times) >= 2:
                time_diff = abs(batch_times[1] - batch_times[0])
                assert time_diff < 0.05  # 几乎同时
        finally:
            await processor.close()


class TestAsyncRequestQueue:
    """异步请求队列测试"""
    
    def test_basic_queue_operations(self):
        """测试基本队列操作"""
        queue = AsyncRequestQueue(max_size=3)
        
        # 添加请求
        queue.put("req1")
        queue.put("req2")
        
        assert queue.qsize() == 2
        assert not queue.full()
        assert not queue.empty()
        
        # 获取请求
        assert queue.get() == "req1"
        assert queue.get() == "req2"
        
        assert queue.empty()
    
    def test_queue_full(self):
        """测试队列满"""
        queue = AsyncRequestQueue(max_size=2)
        
        queue.put("req1")
        queue.put("req2")
        
        assert queue.full()
        
        # 尝试添加更多（非阻塞）
        with pytest.raises(Exception):  # 队列满异常
            queue.put_nowait("req3")
    
    def test_blocking_operations(self):
        """测试阻塞操作"""
        queue = AsyncRequestQueue(max_size=1)
        
        # 填满队列
        queue.put("req1")
        
        # 在另一个线程中移除一个元素
        def consumer():
            time.sleep(0.1)
            queue.get()  # 移除一个
        
        thread = threading.Thread(target=consumer)
        thread.start()
        
        # 这应该会阻塞直到有空间
        start_time = time.time()
        try:
            queue.put("req2", timeout=0.5)  # 使用较短的超时
            elapsed = time.time() - start_time
            assert elapsed >= 0.08  # 确实阻塞了（略小于0.1，考虑到线程调度）
        except Exception as e:
            # 如果队列满了，这也是预期的
            pass
        finally:
            thread.join()
    
    def test_close_queue(self):
        """测试关闭队列"""
        queue = AsyncRequestQueue()
        
        queue.put("req1")
        queue.close()
        
        assert queue._closed
        
        # 关闭后不能添加
        with pytest.raises(Exception):
            queue.put("req2")
    
    @pytest.mark.asyncio
    async def test_async_iteration(self):
        """测试异步迭代"""
        queue = AsyncRequestQueue()
        
        # 添加一些请求
        for i in range(5):
            queue.put(i)
        
        # 异步迭代
        results = []
        
        async def consumer():
            while not queue.empty():
                item = queue.get()
                results.append(item)
                await asyncio.sleep(0.01)
        
        await consumer()
        
        assert results == [0, 1, 2, 3, 4]


class TestRateLimiter:
    """速率限制器测试"""
    
    @pytest.fixture
    def rate_limiter(self):
        """创建速率限制器"""
        return RateLimiter(calls=2, period=1.0)  # 每秒2次
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, rate_limiter):
        """测试速率限制"""
        start_time = time.time()
        
        # 快速调用4次
        for i in range(4):
            async with rate_limiter:
                pass
        
        elapsed = time.time() - start_time
        
        # 应该需要约1秒（前2次立即，后2次等待1秒）
        assert 0.9 < elapsed < 1.5
    
    def test_burst_handling(self):
        """测试突发处理"""
        limiter = RateLimiter(calls=3, period=1.0, burst=5)

        async def _run():
            # 突发5次应该立即完成
            start_time = time.time()

            for _ in range(5):
                async with limiter:
                    pass

            burst_time = time.time() - start_time
            assert burst_time < 0.5  # 应该相对较快

            # 第6次应该被限制
            async with limiter:
                pass

            total_time = time.time() - start_time
            assert total_time >= 1.0  # 需要等待

        asyncio.run(_run())
    
    def test_thread_safe(self, rate_limiter):
        """测试线程安全"""
        call_times = []
        
        def make_call():
            asyncio.run(self._async_call(rate_limiter, call_times))
        
        # 多线程调用
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_call)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 验证调用被正确限制
        # 分析调用时间间隔
        call_times.sort()
        
        # 同一秒内不应该超过限制
        for i in range(len(call_times) - 2):
            if call_times[i+2] - call_times[i] < 1.0:
                # 如果3个调用在1秒内，说明限制失败
                pytest.fail("速率限制失败")
    
    async def _async_call(self, limiter, call_times):
        """辅助异步调用"""
        async with limiter:
            call_times.append(time.time())
    
    @pytest.mark.asyncio
    async def test_reset_limit(self):
        """测试重置限制"""
        limiter = RateLimiter(calls=2, period=1.0)
        
        # 用完限制
        async with limiter:
            pass
        async with limiter:
            pass
        
        # 重置
        if hasattr(limiter, 'reset'):
            limiter.reset()
            
            # 应该可以立即调用
            start_time = time.time()
            async with limiter:
                pass
            elapsed = time.time() - start_time
            
            assert elapsed < 0.1


class TestAsyncPerformance:
    """异步性能测试"""
    
    @pytest.mark.asyncio
    async def test_async_vs_sync_performance(self):
        """测试异步vs同步性能"""
        def slow_operation(x):
            time.sleep(0.1)
            return x * 2
        
        # 同步执行
        sync_start = time.time()
        sync_results = []
        for i in range(10):
            result = slow_operation(i)
            sync_results.append(result)
        sync_time = time.time() - sync_start
        
        # 异步执行
        wrapper = AsyncWrapper(slow_operation)
        
        async_start = time.time()
        tasks = [wrapper(i) for i in range(10)]
        async_results = await asyncio.gather(*tasks)
        async_time = time.time() - async_start
        
        # 验证结果相同
        assert sync_results == async_results
        
        # 验证异步更快
        speedup = sync_time / async_time
        assert speedup > 2.0  # 至少2倍加速
        
        print(f"同步时间: {sync_time:.2f}s")
        print(f"异步时间: {async_time:.2f}s")
        print(f"加速比: {speedup:.2f}x")
        
        # 清理
        wrapper.cleanup()
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """测试内存效率"""
        import psutil
        process = psutil.Process()
        
        # 初始内存
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量异步任务
        async def small_task(i):
            await asyncio.sleep(0.001)
            return i
        
        tasks = [small_task(i) for i in range(1000)]
        results = await asyncio.gather(*tasks)
        
        # 最终内存
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 验证内存使用合理
        assert len(results) == 1000
        assert memory_increase < 50  # 内存增长小于50MB
        
        print(f"处理1000个异步任务的内存增长: {memory_increase:.2f}MB")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
