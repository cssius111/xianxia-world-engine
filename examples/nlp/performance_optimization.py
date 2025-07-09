#!/usr/bin/env python
"""
NLP 性能优化示例

演示各种性能优化技术：
- 缓存优化
- 批处理
- 并发控制
- 内存管理
- 预加载和预热
- 响应时间优化
"""

import os
import sys
import time
import asyncio
import json
import gc
from pathlib import Path
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import lru_cache, wraps
from collections import defaultdict
import tracemalloc

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from xwe.core.nlp import DeepSeekNLPProcessor
from xwe.core.nlp.monitor import get_nlp_monitor


def timing_decorator(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"  {func.__name__} 耗时: {end_time - start_time:.3f}秒")
        return result
    return wrapper


class OptimizedNLPProcessor(DeepSeekNLPProcessor):
    """优化版本的 NLP 处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_pool = ThreadPoolExecutor(max_workers=10)
        self.batch_queue = []
        self.batch_size = 5
        self.batch_timeout = 0.1  # 100ms
        
    @lru_cache(maxsize=1000)
    def _cached_parse(self, command: str, context_hash: str):
        """带缓存的解析（用于演示）"""
        return super().parse_command(command)
    
    async def parse_batch_async(self, commands: List[str]) -> List[Any]:
        """批量异步解析"""
        tasks = []
        for cmd in commands:
            task = asyncio.create_task(self.parse_command_async(cmd))
            tasks.append(task)
        
        return await asyncio.gather(*tasks)


def example_1_cache_optimization():
    """示例1: 缓存优化"""
    print("=== 示例1: 缓存优化 ===\n")
    
    # 创建不同缓存配置的处理器
    processors = {
        "无缓存": DeepSeekNLPProcessor(cache_size=0),
        "小缓存": DeepSeekNLPProcessor(cache_size=10),
        "中缓存": DeepSeekNLPProcessor(cache_size=100),
        "大缓存": DeepSeekNLPProcessor(cache_size=1000)
    }
    
    # 测试命令集
    test_commands = ["攻击", "防御", "使用技能", "查看地图"] * 25  # 100个命令
    
    results = {}
    
    for name, processor in processors.items():
        print(f"\n测试 {name}:")
        
        start_time = time.time()
        cache_hits = 0
        
        for cmd in test_commands:
            result = processor.parse_command(cmd)
            # 检查是否从缓存获取（简化判断）
            if hasattr(processor, '_cache') and cmd in str(processor._cache):
                cache_hits += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        results[name] = {
            "total_time": total_time,
            "avg_time": total_time / len(test_commands),
            "cache_hits": cache_hits,
            "cache_hit_rate": cache_hits / len(test_commands)
        }
        
        print(f"  总耗时: {total_time:.3f}秒")
        print(f"  平均耗时: {results[name]['avg_time']:.3f}秒")
        print(f"  缓存命中: {cache_hits}/{len(test_commands)} ({results[name]['cache_hit_rate']:.1%})")
    
    # 性能对比
    print("\n性能对比:")
    baseline = results["无缓存"]["total_time"]
    for name, data in results.items():
        speedup = baseline / data["total_time"]
        print(f"  {name}: {speedup:.2f}x 加速")


def example_2_batch_processing():
    """示例2: 批处理优化"""
    print("\n\n=== 示例2: 批处理优化 ===\n")
    
    processor = OptimizedNLPProcessor()
    
    # 准备测试数据
    commands = [f"命令{i}" for i in range(50)]
    
    # 方法1: 逐个处理
    print("逐个处理:")
    start_time = time.time()
    results_single = []
    for cmd in commands:
        result = processor.parse_command(cmd)
        results_single.append(result)
    single_time = time.time() - start_time
    print(f"  总耗时: {single_time:.3f}秒")
    
    # 方法2: 批量处理（模拟）
    print("\n批量处理（5个一批）:")
    start_time = time.time()
    results_batch = []
    batch_size = 5
    
    for i in range(0, len(commands), batch_size):
        batch = commands[i:i+batch_size]
        # 模拟批量 API 调用
        batch_results = [processor.parse_command(cmd) for cmd in batch]
        results_batch.extend(batch_results)
    
    batch_time = time.time() - start_time
    print(f"  总耗时: {batch_time:.3f}秒")
    
    # 方法3: 异步批处理
    async def async_batch_process():
        print("\n异步批处理:")
        start_time = time.time()
        results = await processor.parse_batch_async(commands[:20])  # 测试前20个
        async_time = time.time() - start_time
        print(f"  总耗时: {async_time:.3f}秒")
        return results
    
    asyncio.run(async_batch_process())
    
    print(f"\n性能对比:")
    print(f"  批处理相比逐个: {single_time/batch_time:.2f}x 加速")


def example_3_concurrent_processing():
    """示例3: 并发控制"""
    print("\n\n=== 示例3: 并发控制 ===\n")
    
    import concurrent.futures
    import threading
    
    processor = DeepSeekNLPProcessor()
    commands = [f"复杂命令{i}" for i in range(30)]
    
    # 测试不同并发级别
    def process_command(cmd):
        return processor.parse_command(cmd)
    
    concurrency_levels = [1, 5, 10, 20]
    results = {}
    
    for level in concurrency_levels:
        print(f"\n并发级别 {level}:")
        
        with ThreadPoolExecutor(max_workers=level) as executor:
            start_time = time.time()
            
            # 提交所有任务
            futures = [executor.submit(process_command, cmd) for cmd in commands]
            
            # 等待完成
            concurrent.futures.wait(futures)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            results[level] = total_time
            print(f"  总耗时: {total_time:.3f}秒")
            print(f"  平均每个: {total_time/len(commands):.3f}秒")
    
    # 找出最优并发级别
    optimal_level = min(results, key=results.get)
    print(f"\n最优并发级别: {optimal_level} (耗时: {results[optimal_level]:.3f}秒)")


def example_4_memory_optimization():
    """示例4: 内存优化"""
    print("\n\n=== 示例4: 内存优化 ===\n")
    
    # 启动内存追踪
    tracemalloc.start()
    
    # 测试场景1: 大量上下文
    print("测试大上下文处理:")
    
    processor = DeepSeekNLPProcessor()
    
    # 创建大上下文
    large_context = {
        "history": [{"cmd": f"cmd{i}", "result": f"result{i}"} for i in range(1000)],
        "game_state": {
            "items": {f"item{i}": i for i in range(500)},
            "npcs": [f"npc{i}" for i in range(200)]
        }
    }
    
    # 获取初始内存
    snapshot1 = tracemalloc.take_snapshot()
    
    # 处理命令
    for i in range(10):
        result = processor.parse_command("测试命令", context=large_context)
    
    # 获取处理后内存
    snapshot2 = tracemalloc.take_snapshot()
    
    # 分析内存差异
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    print("\n内存使用前10:")
    for stat in top_stats[:10]:
        print(f"  {stat}")
    
    # 手动垃圾回收
    print("\n执行垃圾回收...")
    collected = gc.collect()
    print(f"  回收对象数: {collected}")
    
    # 内存优化技巧演示
    class MemoryEfficientProcessor:
        """内存高效的处理器"""
        
        def __init__(self):
            self.nlp = DeepSeekNLPProcessor()
            self.context_compressor = ContextCompressor()
        
        def process_with_compression(self, command: str, context: Dict):
            """使用压缩的上下文处理"""
            # 压缩上下文
            compressed = self.context_compressor.compress(context)
            
            # 处理命令
            result = self.nlp.parse_command(command, compressed)
            
            # 清理临时数据
            del compressed
            gc.collect()
            
            return result
    
    class ContextCompressor:
        """上下文压缩器"""
        
        def compress(self, context: Dict) -> Dict:
            """压缩上下文，只保留关键信息"""
            compressed = {}
            
            # 只保留最近的历史
            if "history" in context:
                compressed["recent_history"] = context["history"][-10:]
            
            # 简化游戏状态
            if "game_state" in context:
                compressed["summary"] = {
                    "item_count": len(context["game_state"].get("items", {})),
                    "npc_count": len(context["game_state"].get("npcs", []))
                }
            
            return compressed
    
    print("\n使用内存优化版本:")
    efficient_processor = MemoryEfficientProcessor()
    
    # 测试内存效率
    for i in range(10):
        result = efficient_processor.process_with_compression("测试", large_context)
    
    # 停止追踪
    tracemalloc.stop()
    
    print("✓ 内存优化完成")


def example_5_preloading_warming():
    """示例5: 预加载和预热"""
    print("\n\n=== 示例5: 预加载和预热 ===\n")
    
    class PreloadedNLPProcessor(DeepSeekNLPProcessor):
        """支持预加载的处理器"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.common_commands = []
            self.preloaded = False
        
        def preload_common_commands(self):
            """预加载常用命令"""
            print("预加载常用命令...")
            
            # 常用命令列表
            common_commands = [
                "攻击", "防御", "逃跑", "使用技能",
                "查看状态", "打开背包", "查看地图",
                "去", "修炼", "对话", "购买", "出售"
            ]
            
            # 预解析并缓存
            for cmd in common_commands:
                self.parse_command(cmd)
                self.common_commands.append(cmd)
            
            self.preloaded = True
            print(f"  预加载 {len(common_commands)} 个常用命令")
        
        def warmup(self, iterations=5):
            """预热处理器"""
            print(f"\n预热处理器 ({iterations} 轮)...")
            
            warmup_commands = ["测试1", "测试2", "测试3"]
            
            for i in range(iterations):
                for cmd in warmup_commands:
                    self.parse_command(cmd)
            
            print("  预热完成")
    
    # 测试预加载效果
    print("创建两个处理器:")
    
    # 普通处理器
    normal_processor = DeepSeekNLPProcessor()
    
    # 预加载处理器
    preloaded_processor = PreloadedNLPProcessor()
    preloaded_processor.preload_common_commands()
    preloaded_processor.warmup()
    
    # 测试命令
    test_commands = ["攻击", "防御", "查看状态", "修炼", "去东门"] * 5
    
    # 测试普通处理器
    print("\n测试普通处理器:")
    start_time = time.time()
    for cmd in test_commands:
        normal_processor.parse_command(cmd)
    normal_time = time.time() - start_time
    print(f"  耗时: {normal_time:.3f}秒")
    
    # 测试预加载处理器
    print("\n测试预加载处理器:")
    start_time = time.time()
    for cmd in test_commands:
        preloaded_processor.parse_command(cmd)
    preloaded_time = time.time() - start_time
    print(f"  耗时: {preloaded_time:.3f}秒")
    
    print(f"\n性能提升: {normal_time/preloaded_time:.2f}x")


def example_6_response_optimization():
    """示例6: 响应时间优化"""
    print("\n\n=== 示例6: 响应时间优化 ===\n")
    
    class ResponseOptimizedProcessor:
        """响应优化的处理器"""
        
        def __init__(self):
            self.nlp = DeepSeekNLPProcessor()
            self.quick_patterns = {
                "攻击": ("attack", "combat.attack"),
                "防御": ("defend", "combat.defend"),
                "逃跑": ("flee", "combat.flee"),
                "状态": ("status", "information.status"),
                "背包": ("inventory", "information.inventory")
            }
        
        def parse_with_fallback(self, command: str, timeout: float = 0.5):
            """带超时和回退的解析"""
            import threading
            import queue
            
            result_queue = queue.Queue()
            
            def parse_thread():
                try:
                    result = self.nlp.parse_command(command)
                    result_queue.put(("success", result))
                except Exception as e:
                    result_queue.put(("error", str(e)))
            
            # 先尝试快速匹配
            for key, (cmd, intent) in self.quick_patterns.items():
                if key in command:
                    return self._create_quick_result(cmd, intent)
            
            # 启动解析线程
            thread = threading.Thread(target=parse_thread)
            thread.start()
            
            # 等待结果（带超时）
            try:
                status, result = result_queue.get(timeout=timeout)
                if status == "success":
                    return result
                else:
                    # 使用规则引擎回退
                    return self._rule_based_parse(command)
            except queue.Empty:
                # 超时，使用快速回退
                print(f"  [警告] 解析超时，使用回退方案")
                return self._rule_based_parse(command)
        
        def _create_quick_result(self, command: str, intent: str):
            """创建快速结果"""
            from xwe.core.nlp import ParsedCommand
            return ParsedCommand(
                raw=command,
                normalized_command=command,
                intent=intent,
                args={},
                explanation="快速匹配",
                confidence=0.9
            )
        
        def _rule_based_parse(self, command: str):
            """基于规则的解析（回退方案）"""
            from xwe.core.nlp import ParsedCommand
            
            # 简单的规则匹配
            if "攻击" in command:
                return self._create_quick_result("attack", "combat.attack")
            elif "移动" in command or "去" in command:
                return self._create_quick_result("move", "exploration.move")
            else:
                return self._create_quick_result("unknown", "unknown")
    
    # 测试响应优化
    optimizer = ResponseOptimizedProcessor()
    
    test_cases = [
        ("攻击", "快速命令"),
        ("我想去洞府修炼一会儿", "复杂命令"),
        ("这是一个非常非常复杂的命令" * 5, "超长命令")
    ]
    
    print("测试不同类型命令的响应时间:\n")
    
    for command, desc in test_cases:
        print(f"{desc}: '{command[:30]}...'")
        
        start_time = time.time()
        result = optimizer.parse_with_fallback(command, timeout=0.3)
        end_time = time.time()
        
        print(f"  响应时间: {(end_time - start_time) * 1000:.1f}ms")
        print(f"  解析结果: {result.normalized_command}")
        print(f"  使用方案: {result.explanation}\n")


def main():
    """运行所有性能优化示例"""
    print("修仙世界引擎 - NLP 性能优化示例")
    print("=" * 50)
    
    # 使用模拟模式
    os.environ["USE_MOCK_LLM"] = "true"
    
    try:
        example_1_cache_optimization()
        example_2_batch_processing()
        example_3_concurrent_processing()
        example_4_memory_optimization()
        example_5_preloading_warming()
        example_6_response_optimization()
        
        print("\n✅ 所有性能优化示例运行完成！")
        
        # 性能优化总结
        print("\n性能优化最佳实践总结:")
        print("1. 启用缓存：可获得 2-5x 性能提升")
        print("2. 批处理：减少 API 调用次数")
        print("3. 并发控制：找到最优并发级别")
        print("4. 内存管理：使用上下文压缩")
        print("5. 预加载：减少冷启动时间")
        print("6. 响应优化：使用超时和回退机制")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()