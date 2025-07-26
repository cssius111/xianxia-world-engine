"""
LLMClient 异步功能测试
"""

import asyncio
import pytest
import time
import os
from unittest.mock import Mock, patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor

from src.xwe.core.nlp.llm_client import LLMClient
from src.xwe.core.nlp.async_utils import (
    AsyncConfig, AsyncHelper, AsyncBatchProcessor,
    get_global_executor, cleanup_global_executor
)


class TestLLMClientAsync:
    """测试 LLMClient 的异步功能"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        os.environ["DEEPSEEK_API_KEY"] = "test"
        with patch.object(LLMClient, "chat", return_value="ok"):
            client = LLMClient()
            yield client
            client.cleanup()
        del os.environ["DEEPSEEK_API_KEY"]
    
    @pytest.mark.asyncio
    async def test_chat_async_basic(self, client):
        """测试基本的异步聊天功能"""
        response = await client.chat_async("测试消息")
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_chat_async_with_params(self, client):
        """测试带参数的异步聊天"""
        response = await client.chat_async(
            "测试消息",
            temperature=0.5,
            max_tokens=100,
            system_prompt="你是一个游戏助手"
        )
        assert isinstance(response, str)
    
    @pytest.mark.asyncio
    async def test_chat_with_context_async(self, client):
        """测试异步上下文聊天"""
        messages = [
            {"role": "system", "content": "你是游戏助手"},
            {"role": "user", "content": "如何提升等级？"}
        ]
        response = await client.chat_with_context_async(messages)
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """测试并发请求"""
        # 创建多个并发请求
        tasks = [
            client.chat_async(f"消息 {i}")
            for i in range(5)
        ]
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        # 验证所有请求都成功
        assert len(responses) == 5
        assert all(isinstance(r, str) for r in responses)
        
        # 并发执行应该比串行快
        print(f"并发执行 5 个请求耗时: {duration:.2f}秒")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """测试错误处理"""
        # 模拟错误
        with patch.object(client, 'chat', side_effect=Exception("模拟错误")):
            with pytest.raises(Exception) as exc_info:
                await client.chat_async("测试")
            assert "模拟错误" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_executor_cleanup(self):
        """测试执行器清理"""
        client = LLMClient()
        assert client._executor_initialized
        
        # 执行一些任务
        await client.chat_async("测试")
        
        # 清理
        client.cleanup()
        assert not client._executor_initialized
        
        # 清理后不能再使用
        with pytest.raises(RuntimeError):
            await client.chat_async("测试")
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, client):
        """测试超时处理"""
        # 模拟慢响应
        async def slow_chat(*args, **kwargs):
            await asyncio.sleep(2)
            return "慢响应"
        
        with patch.object(client, 'chat', side_effect=lambda *a, **k: time.sleep(2) or "慢响应"):
            # 使用 AsyncHelper 的超时功能
            with pytest.raises(asyncio.TimeoutError):
                await AsyncHelper.run_with_timeout(
                    client.chat_async("测试"),
                    timeout=0.1
                )


class TestAsyncUtils:
    """测试异步工具函数"""
    
    def test_async_config(self):
        """测试异步配置"""
        # 测试默认值
        assert AsyncConfig.get_worker_count() == 5
        assert AsyncConfig.get_queue_size() == 100
        assert AsyncConfig.get_timeout() == 30.0
        assert AsyncConfig.is_async_enabled() is True
        
        # 测试环境变量覆盖
        os.environ["LLM_ASYNC_WORKERS"] = "10"
        assert AsyncConfig.get_worker_count() == 10
        del os.environ["LLM_ASYNC_WORKERS"]
    
    def test_create_executor(self):
        """测试创建执行器"""
        executor = AsyncHelper.create_executor(max_workers=3)
        assert isinstance(executor, ThreadPoolExecutor)
        assert executor._max_workers == 3
        executor.shutdown()
    
    @pytest.mark.asyncio
    async def test_run_with_timeout(self):
        """测试超时运行"""
        # 正常完成
        async def quick_task():
            await asyncio.sleep(0.1)
            return "完成"
        
        result = await AsyncHelper.run_with_timeout(quick_task(), timeout=1.0)
        assert result == "完成"
        
        # 超时
        async def slow_task():
            await asyncio.sleep(2)
            return "永远不会完成"
        
        with pytest.raises(asyncio.TimeoutError):
            await AsyncHelper.run_with_timeout(slow_task(), timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_gather_with_limit(self):
        """测试限制并发的 gather"""
        call_times = []
        
        async def task(i):
            call_times.append(time.time())
            await asyncio.sleep(0.1)
            return i
        
        # 创建 10 个任务，限制并发为 2
        tasks = [task(i) for i in range(10)]
        results = await AsyncHelper.gather_with_limit(tasks, limit=2)
        
        # 验证结果
        assert len(results) == 10
        assert results == list(range(10))
        
        # 验证并发限制（应该分 5 批执行）
        # 由于并发限制，执行时间应该接近 0.5 秒
        total_time = max(call_times) - min(call_times)
        assert total_time >= 0.4  # 允许一些误差
    
    def test_run_async_in_sync(self):
        """测试在同步代码中运行异步函数"""
        async def async_func():
            await asyncio.sleep(0.1)
            return "异步结果"
        
        result = AsyncHelper.run_async_in_sync(async_func())
        assert result == "异步结果"
    
    @pytest.mark.asyncio
    async def test_batch_processor(self):
        """测试批处理器"""
        processed_items = []
        
        async def process_item(item):
            await asyncio.sleep(0.01)
            processed_items.append(item)
            return item * 2
        
        processor = AsyncBatchProcessor(
            process_func=process_item,
            batch_size=3,
            max_workers=2
        )
        
        items = list(range(10))
        results = await processor.process_batch(items)
        
        # 验证结果
        assert results == [i * 2 for i in range(10)]
        assert len(processed_items) == 10
    
    def test_global_executor(self):
        """测试全局执行器"""
        # 获取执行器
        executor1 = get_global_executor()
        executor2 = get_global_executor()
        
        # 应该是同一个实例
        assert executor1 is executor2
        
        # 清理
        cleanup_global_executor()
        
        # 清理后应该创建新的
        executor3 = get_global_executor()
        assert executor3 is not executor1
        
        # 最终清理
        cleanup_global_executor()


class TestIntegrationAsync:
    """异步功能集成测试"""
    
    @pytest.mark.asyncio
    async def test_nlp_processor_async_integration(self):
        """测试与 NLPProcessor 的集成"""
        from src.xwe.core.nlp.nlp_processor import DeepSeekNLPProcessor
        
        os.environ["DEEPSEEK_API_KEY"] = "test"
        processor = DeepSeekNLPProcessor()
        with patch.object(processor.llm, "chat", return_value='{"normalized_command":"探索","intent":"action","args":{}}'):

            # 异步解析多个命令
            commands = ["探索", "查看背包", "使用物品"]

            async def parse_async(cmd):
                # 模拟异步解析（实际上 parse 是同步的）
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, processor.parse, cmd)

            # 并发解析
            results = await asyncio.gather(*[parse_async(cmd) for cmd in commands])

            # 验证结果
            assert len(results) == 3
            assert all(r.normalized_command != "未知" for r in results)
        
        # 清理
        del os.environ["DEEPSEEK_API_KEY"]
    
    @pytest.mark.asyncio
    async def test_performance_comparison(self):
        """性能对比测试"""
        client = LLMClient()
        
        # 测试消息
        messages = [f"消息 {i}" for i in range(10)]
        
        # 同步执行
        sync_start = time.time()
        sync_results = []
        for msg in messages:
            result = client.chat(msg)
            sync_results.append(result)
        sync_duration = time.time() - sync_start
        
        # 异步执行
        async_start = time.time()
        async_tasks = [client.chat_async(msg) for msg in messages]
        async_results = await asyncio.gather(*async_tasks)
        async_duration = time.time() - async_start
        
        # 清理
        client.cleanup()
        
        # 输出性能对比
        print(f"\n性能对比:")
        print(f"同步执行 10 个请求: {sync_duration:.2f}秒")
        print(f"异步执行 10 个请求: {async_duration:.2f}秒")
        print(f"性能提升: {(sync_duration / async_duration):.2f}倍")
        
        # 验证结果一致性
        assert len(sync_results) == len(async_results)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
