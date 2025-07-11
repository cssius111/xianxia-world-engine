#!/usr/bin/env python3
"""
测试三种 DeepSeek Client POC 实现的脚本
"""

import asyncio
import time
import sys
import os
from typing import Dict, Any
import importlib

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# 测试配置
TEST_PROMPTS = [
    "玩家想要突破到金丹期",
    "我要去禁地探索",
    "使用禁术攻击敌人",
]


class MockContext:
    """模拟游戏上下文"""
    def __init__(self):
        self.scene = "主城"
        self.player = type('Player', (), {'realm': '筑基期'})()
        self.target_realm = '金丹期'
        self.laws = [
            type('Law', (), {'enabled': True, 'code': 'FORBIDDEN_ARTS'})()
        ]


async def test_httpx_implementation():
    """测试 httpx.AsyncClient 实现"""
    print("\n" + "="*60)
    print("测试 httpx.AsyncClient 实现")
    print("="*60)
    
    try:
        from src.ai.poc.deepseek_client_httpx import DeepSeekClient
        client = DeepSeekClient()
        
        # 测试同步方法
        print("\n1. 测试同步方法:")
        start = time.time()
        result = client.chat("测试同步聊天")
        sync_time = time.time() - start
        print(f"   同步响应时间: {sync_time:.3f}s")
        print(f"   响应内容: {result.get('text', '')[:50]}...")
        
        # 测试异步方法
        print("\n2. 测试异步方法:")
        start = time.time()
        result = await client.chat_async("测试异步聊天")
        async_time = time.time() - start
        print(f"   异步响应时间: {async_time:.3f}s")
        print(f"   响应内容: {result.get('text', '')[:50]}...")
        
        # 测试并发请求
        print("\n3. 测试并发请求 (10个):")
        start = time.time()
        tasks = [client.chat_async(f"并发请求 {i}") for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_time = time.time() - start
        
        success_count = sum(1 for r in results if isinstance(r, dict) and 'text' in r)
        print(f"   并发响应时间: {concurrent_time:.3f}s")
        print(f"   成功请求数: {success_count}/10")
        print(f"   平均响应时间: {concurrent_time/10:.3f}s")
        
        # 清理资源
        await client.close()
        
        return {
            "implementation": "httpx.AsyncClient",
            "sync_time": sync_time,
            "async_time": async_time,
            "concurrent_time": concurrent_time,
            "concurrent_avg": concurrent_time/10,
            "success_rate": success_count/10
        }
        
    except Exception as e:
        print(f"   错误: {e}")
        return {"implementation": "httpx.AsyncClient", "error": str(e)}


async def test_threadpool_implementation():
    """测试 ThreadPoolExecutor 实现"""
    print("\n" + "="*60)
    print("测试 ThreadPoolExecutor 实现")
    print("="*60)
    
    try:
        from src.ai.poc.deepseek_client_threadpool import DeepSeekClient
        client = DeepSeekClient()
        
        # 测试同步方法
        print("\n1. 测试同步方法:")
        start = time.time()
        result = client.chat("测试同步聊天")
        sync_time = time.time() - start
        print(f"   同步响应时间: {sync_time:.3f}s")
        print(f"   响应内容: {result.get('text', '')[:50]}...")
        
        # 测试异步方法
        print("\n2. 测试异步方法:")
        start = time.time()
        result = await client.chat_async("测试异步聊天")
        async_time = time.time() - start
        print(f"   异步响应时间: {async_time:.3f}s")
        print(f"   响应内容: {result.get('text', '')[:50]}...")
        
        # 测试并发请求
        print("\n3. 测试并发请求 (10个):")
        start = time.time()
        tasks = [client.chat_async(f"并发请求 {i}") for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_time = time.time() - start
        
        success_count = sum(1 for r in results if isinstance(r, dict) and 'text' in r)
        print(f"   并发响应时间: {concurrent_time:.3f}s")
        print(f"   成功请求数: {success_count}/10")
        print(f"   平均响应时间: {concurrent_time/10:.3f}s")
        
        # 清理资源
        DeepSeekClient.shutdown_executor()
        
        return {
            "implementation": "ThreadPoolExecutor",
            "sync_time": sync_time,
            "async_time": async_time,
            "concurrent_time": concurrent_time,
            "concurrent_avg": concurrent_time/10,
            "success_rate": success_count/10
        }
        
    except Exception as e:
        print(f"   错误: {e}")
        return {"implementation": "ThreadPoolExecutor", "error": str(e)}


async def test_celery_implementation():
    """测试 Celery + Redis 实现"""
    print("\n" + "="*60)
    print("测试 Celery + Redis 实现")
    print("="*60)
    
    # 检查 Redis 连接
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis 连接正常")
    except Exception as e:
        print(f"✗ Redis 连接失败: {e}")
        print("  请确保 Redis 服务已启动")
        return {"implementation": "Celery", "error": "Redis not available"}
    
    try:
        from src.ai.poc.deepseek_client_celery import DeepSeekClient
        client = DeepSeekClient()
        
        # 测试同步方法
        print("\n1. 测试同步方法:")
        start = time.time()
        result = client.chat("测试同步聊天")
        sync_time = time.time() - start
        print(f"   同步响应时间: {sync_time:.3f}s")
        print(f"   响应内容: {result.get('text', '')[:50]}...")
        
        # 测试异步方法（等待结果）
        print("\n2. 测试异步方法（等待结果）:")
        start = time.time()
        result = await client.chat_async("测试异步聊天", wait_for_result=True)
        async_time = time.time() - start
        print(f"   异步响应时间: {async_time:.3f}s")
        print(f"   响应内容: {result.get('text', '')[:50]}...")
        
        # 测试异步方法（立即返回）
        print("\n3. 测试异步方法（立即返回任务ID）:")
        start = time.time()
        result = await client.chat_async("测试异步聊天", wait_for_result=False)
        submit_time = time.time() - start
        print(f"   提交时间: {submit_time:.3f}s")
        print(f"   任务ID: {result.get('task_id', 'N/A')}")
        
        if 'task_id' in result:
            # 轮询任务状态
            await asyncio.sleep(1)
            status = client.get_task_status(result['task_id'])
            print(f"   任务状态: {status.get('status', 'unknown')}")
        
        # 测试并发请求
        print("\n4. 测试并发请求 (10个):")
        start = time.time()
        tasks = [client.chat_async(f"并发请求 {i}", wait_for_result=True) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_time = time.time() - start
        
        success_count = sum(1 for r in results if isinstance(r, dict) and 'text' in r)
        print(f"   并发响应时间: {concurrent_time:.3f}s")
        print(f"   成功请求数: {success_count}/10")
        print(f"   平均响应时间: {concurrent_time/10:.3f}s")
        
        return {
            "implementation": "Celery + Redis",
            "sync_time": sync_time,
            "async_time": async_time,
            "submit_time": submit_time,
            "concurrent_time": concurrent_time,
            "concurrent_avg": concurrent_time/10,
            "success_rate": success_count/10
        }
        
    except Exception as e:
        print(f"   错误: {e}")
        return {"implementation": "Celery", "error": str(e)}


def print_summary(results: list):
    """打印测试结果汇总"""
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    print("\n| 实现方案 | 同步时间 | 异步时间 | 并发平均 | 成功率 |")
    print("|----------|----------|----------|----------|--------|")
    
    for result in results:
        if "error" in result:
            print(f"| {result['implementation']:20} | 错误: {result['error']} |")
        else:
            print(f"| {result['implementation']:20} | "
                  f"{result.get('sync_time', 0):.3f}s | "
                  f"{result.get('async_time', 0):.3f}s | "
                  f"{result.get('concurrent_avg', 0):.3f}s | "
                  f"{result.get('success_rate', 0)*100:.0f}% |")
    
    # 找出最佳方案
    valid_results = [r for r in results if "error" not in r]
    if valid_results:
        best_async = min(valid_results, key=lambda x: x.get('async_time', float('inf')))
        best_concurrent = min(valid_results, key=lambda x: x.get('concurrent_avg', float('inf')))
        
        print(f"\n最佳异步响应: {best_async['implementation']} ({best_async['async_time']:.3f}s)")
        print(f"最佳并发性能: {best_concurrent['implementation']} ({best_concurrent['concurrent_avg']:.3f}s)")


async def main():
    """主测试函数"""
    print("DeepSeek Client POC 实现测试")
    print("注意：需要设置 DEEPSEEK_API_KEY 环境变量")
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("\n警告：未设置 DEEPSEEK_API_KEY，将使用 mock 响应")
    
    results = []
    
    # 测试各种实现
    results.append(await test_httpx_implementation())
    results.append(await test_threadpool_implementation())
    results.append(await test_celery_implementation())
    
    # 打印汇总
    print_summary(results)
    
    print("\n测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
