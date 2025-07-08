"""
LLMClient 异步功能使用示例
展示如何在 XianXia World Engine 中使用异步 API
"""

import asyncio
import time
import os
from typing import List

from src.xwe.core.nlp.llm_client import LLMClient
from src.xwe.core.nlp.async_utils import (
    AsyncHelper, AsyncBatchProcessor, AsyncConfig
)


async def example_basic_async():
    """基础异步使用示例"""
    print("=== 基础异步使用 ===\n")
    
    # 创建客户端
    client = LLMClient()
    
    try:
        # 单个异步请求
        print("1. 单个异步请求:")
        response = await client.chat_async("介绍一下修仙世界的境界体系")
        print(f"响应: {response[:100]}...\n")
        
        # 带参数的异步请求
        print("2. 带参数的异步请求:")
        response = await client.chat_async(
            "如何快速提升修为？",
            temperature=0.3,
            max_tokens=150,
            system_prompt="你是修仙世界的资深玩家"
        )
        print(f"响应: {response[:100]}...\n")
        
    finally:
        # 清理资源
        client.cleanup()


async def example_concurrent_processing():
    """并发处理示例"""
    print("=== 并发处理示例 ===\n")
    
    client = LLMClient()
    
    try:
        # 模拟多个玩家同时提问
        questions = [
            "青云城有哪些NPC？",
            "如何获得灵石？",
            "筑基期需要什么条件？",
            "哪里可以买到丹药？",
            "如何加入门派？"
        ]
        
        print(f"并发处理 {len(questions)} 个问题...")
        
        # 串行处理（对比用）
        serial_start = time.time()
        serial_results = []
        for q in questions:
            result = client.chat(q)
            serial_results.append(result)
        serial_duration = time.time() - serial_start
        
        # 并发处理
        concurrent_start = time.time()
        tasks = [client.chat_async(q) for q in questions]
        concurrent_results = await asyncio.gather(*tasks)
        concurrent_duration = time.time() - concurrent_start
        
        print(f"\n性能对比:")
        print(f"串行处理: {serial_duration:.2f}秒")
        print(f"并发处理: {concurrent_duration:.2f}秒")
        print(f"性能提升: {serial_duration / concurrent_duration:.2f}倍\n")
        
    finally:
        client.cleanup()


async def example_context_conversation():
    """上下文对话示例"""
    print("=== 上下文对话示例 ===\n")
    
    client = LLMClient()
    
    try:
        # 构建对话历史
        conversation = [
            {"role": "system", "content": "你是修仙世界的游戏向导，帮助玩家了解游戏机制"},
            {"role": "user", "content": "我刚进入游戏，应该做什么？"},
            {"role": "assistant", "content": "欢迎来到修仙世界！作为新手，你应该先探索青云城..."},
            {"role": "user", "content": "青云城在哪里？"}
        ]
        
        # 异步获取回复
        print("正在生成向导回复...")
        response = await client.chat_with_context_async(
            conversation,
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"向导: {response}\n")
        
        # 继续对话
        conversation.append({"role": "assistant", "content": response})
        conversation.append({"role": "user", "content": "那里有什么任务吗？"})
        
        response2 = await client.chat_with_context_async(conversation)
        print(f"向导: {response2}\n")
        
    finally:
        client.cleanup()


async def example_batch_processing():
    """批量处理示例"""
    print("=== 批量处理示例 ===\n")
    
    client = LLMClient()
    
    try:
        # 模拟批量处理玩家命令
        player_commands = [
            "探索周围环境",
            "查看当前属性", 
            "使用回春丹",
            "前往丹药铺",
            "和掌柜对话",
            "购买聚气丹",
            "查看背包",
            "装备长剑",
            "修炼一个时辰",
            "查看任务列表"
        ]
        
        # 创建批处理器
        async def process_command(cmd):
            prompt = f"将以下游戏命令转换为标准指令：{cmd}"
            return await client.chat_async(prompt, temperature=0.0)
        
        processor = AsyncBatchProcessor(
            process_func=process_command,
            batch_size=3,  # 每批3个
            max_workers=3  # 最多3个并发
        )
        
        print(f"批量处理 {len(player_commands)} 个命令...")
        start_time = time.time()
        
        results = await processor.process_batch(player_commands)
        
        duration = time.time() - start_time
        print(f"处理完成，耗时: {duration:.2f}秒")
        print(f"平均每个命令: {duration/len(player_commands):.2f}秒\n")
        
        # 显示部分结果
        for i, (cmd, result) in enumerate(zip(player_commands[:3], results[:3])):
            print(f"命令: {cmd}")
            print(f"结果: {result[:50]}...")
            print()
            
    finally:
        client.cleanup()


async def example_error_handling():
    """错误处理示例"""
    print("=== 错误处理示例 ===\n")
    
    client = LLMClient()
    
    try:
        # 1. 超时处理
        print("1. 超时处理示例:")
        try:
            # 设置很短的超时时间
            result = await AsyncHelper.run_with_timeout(
                client.chat_async("生成一个很长的修仙故事..."),
                timeout=0.001  # 1毫秒超时
            )
        except asyncio.TimeoutError:
            print("请求超时，使用默认回复")
            result = "系统繁忙，请稍后再试"
        print(f"结果: {result}\n")
        
        # 2. 批量请求的错误处理
        print("2. 批量请求错误处理:")
        
        async def safe_chat(prompt):
            try:
                return await client.chat_async(prompt)
            except Exception as e:
                return f"错误: {str(e)}"
        
        # 混合正常和异常的请求
        mixed_prompts = [
            "正常问题1",
            "",  # 空prompt可能导致错误
            "正常问题2",
            None,  # None可能导致错误
            "正常问题3"
        ]
        
        # 使用 gather 的 return_exceptions 参数
        results = await asyncio.gather(
            *[safe_chat(p) for p in mixed_prompts],
            return_exceptions=True
        )
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"请求 {i+1}: 失败 - {result}")
            else:
                print(f"请求 {i+1}: 成功")
        print()
        
    finally:
        client.cleanup()


async def example_performance_monitoring():
    """性能监控示例"""
    print("=== 性能监控示例 ===\n")
    
    # 配置检查
    print("当前配置:")
    print(f"- 工作线程数: {AsyncConfig.get_worker_count()}")
    print(f"- 队列大小: {AsyncConfig.get_queue_size()}")
    print(f"- 超时时间: {AsyncConfig.get_timeout()}秒")
    print(f"- 异步启用: {AsyncConfig.is_async_enabled()}\n")
    
    client = LLMClient()
    
    try:
        # 性能测试
        test_sizes = [1, 5, 10, 20]
        
        for size in test_sizes:
            prompts = [f"测试问题 {i}" for i in range(size)]
            
            start_time = time.time()
            tasks = [client.chat_async(p) for p in prompts]
            await asyncio.gather(*tasks)
            duration = time.time() - start_time
            
            qps = size / duration
            avg_latency = duration / size * 1000  # 毫秒
            
            print(f"并发 {size:2d} 个请求: {duration:.2f}秒, "
                  f"QPS: {qps:.1f}, 平均延迟: {avg_latency:.0f}ms")
        
        # 资源使用情况
        print(f"\n线程池状态:")
        print(f"- 最大工作线程: {client._executor._max_workers}")
        print(f"- 当前线程数: {len(client._executor._threads)}")
        
    finally:
        client.cleanup()


async def example_real_world_scenario():
    """真实场景示例：多玩家并发处理"""
    print("=== 真实场景：游戏服务器处理多玩家请求 ===\n")
    
    client = LLMClient()
    
    try:
        # 模拟多个玩家的不同类型请求
        player_requests = [
            {"player": "玩家1", "action": "探索", "prompt": "我想探索附近的洞穴"},
            {"player": "玩家2", "action": "对话", "prompt": "向李掌柜询问任务"},
            {"player": "玩家3", "action": "战斗", "prompt": "使用剑法攻击妖兽"},
            {"player": "玩家4", "action": "修炼", "prompt": "在灵气充裕的地方修炼"},
            {"player": "玩家5", "action": "交易", "prompt": "购买10颗聚气丹"},
        ]
        
        # 异步处理所有请求
        async def handle_player_request(request):
            start = time.time()
            
            # 根据不同类型使用不同的处理方式
            if request["action"] == "战斗":
                # 战斗需要快速响应
                prompt = f"[战斗指令] {request['prompt']}"
                response = await client.chat_async(prompt, temperature=0.0, max_tokens=50)
            else:
                # 其他行动可以更详细
                prompt = f"[{request['action']}指令] {request['prompt']}"
                response = await client.chat_async(prompt, temperature=0.7, max_tokens=150)
            
            latency = (time.time() - start) * 1000
            
            return {
                "player": request["player"],
                "action": request["action"],
                "response": response,
                "latency_ms": latency
            }
        
        print("处理多个玩家请求...")
        start_time = time.time()
        
        # 并发处理所有请求
        tasks = [handle_player_request(req) for req in player_requests]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # 显示结果
        print(f"\n总处理时间: {total_time:.2f}秒")
        print(f"平均响应时间: {total_time/len(player_requests):.2f}秒\n")
        
        for result in results:
            print(f"{result['player']} - {result['action']}:")
            print(f"  响应: {result['response'][:60]}...")
            print(f"  延迟: {result['latency_ms']:.0f}ms")
            print()
        
    finally:
        client.cleanup()


async def main():
    """运行所有示例"""
    examples = [
        example_basic_async,
        example_concurrent_processing,
        example_context_conversation,
        example_batch_processing,
        example_error_handling,
        example_performance_monitoring,
        example_real_world_scenario
    ]
    
    for example in examples:
        await example()
        print("\n" + "="*60 + "\n")
        await asyncio.sleep(0.5)  # 短暂暂停


if __name__ == "__main__":
    # 设置使用 Mock 模式进行演示
    os.environ["USE_MOCK_LLM"] = "true"
    
    # 运行示例
    print("LLMClient 异步功能示例\n")
    print("注意：当前使用 Mock 模式进行演示\n")
    
    try:
        asyncio.run(main())
    finally:
        # 清理
        if "USE_MOCK_LLM" in os.environ:
            del os.environ["USE_MOCK_LLM"]
