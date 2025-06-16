# test_performance_optimizations.py

"""
性能优化测试脚本
"""

import time
import asyncio
import json
import random
from typing import Dict, List, Any


from xwe.core.optimizations import ExpressionJITCompiler, SmartCache, AsyncEventSystem
from xwe.core.optimizations.expression_jit import ExpressionBenchmark, SimpleExpressionInterpreter


def test_expression_jit():
    """测试表达式JIT编译器"""
    print("\n=== 表达式JIT编译器测试 ===")
    
    # 创建JIT编译器
    jit = ExpressionJITCompiler()
    
    # 测试表达式
    expressions = {
        'simple_damage': {
            "operation": "*",
            "operands": [
                {"attribute": "player.attack"},
                {"constant": 2.5}
            ]
        },
        'complex_damage': {
            "operation": "+",
            "operands": [
                {
                    "operation": "*",
                    "operands": [
                        {"attribute": "player.attack"},
                        {"constant": 2.5},
                        {
                            "operation": "max",
                            "operands": [
                                {"attribute": "skill.level"},
                                {"constant": 1}
                            ]
                        }
                    ]
                },
                {
                    "operation": "-",
                    "operands": [
                        {"attribute": "target.defense"},
                        {
                            "operation": "*",
                            "operands": [
                                {"attribute": "target.armor"},
                                {"constant": 0.5}
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    # 测试上下文
    test_contexts = [
        {
            "player": {"attack": 100},
            "skill": {"level": 5},
            "target": {"defense": 50, "armor": 20}
        },
        {
            "player": {"attack": 200},
            "skill": {"level": 10},
            "target": {"defense": 100, "armor": 40}
        }
    ]
    
    # 创建基准测试
    benchmark = ExpressionBenchmark(jit)
    
    # 测试每个表达式
    for expr_id, expression in expressions.items():
        print(f"\n测试表达式: {expr_id}")
        
        # 运行基准测试
        result = benchmark.benchmark_expression(
            expr_id, 
            expression, 
            test_contexts,
            iterations=10000
        )
        
        print(f"  解释执行时间: {result['interpret_time']:.4f}秒")
        print(f"  JIT执行时间: {result['jit_time']:.4f}秒")
        print(f"  加速比: {result['speedup']:.2f}x")
        print(f"  编译时间: {result['compile_time']:.4f}秒")
        
    # 打印总体报告
    print("\n" + benchmark.generate_report())
    

def test_smart_cache():
    """测试智能缓存系统"""
    print("\n=== 智能缓存系统测试 ===")
    
    # 创建缓存
    cache = SmartCache(max_memory_mb=10)
    
    # 模拟计算密集型函数
    def expensive_calculation(x: int, y: int) -> int:
        time.sleep(0.01)  # 模拟耗时操作
        return x * y + sum(range(1000))
        
    # 测试缓存效果
    print("\n第一次调用（无缓存）：")
    start = time.perf_counter()
    result1 = cache.get_or_compute("calc_1_2", expensive_calculation, 1, 2)
    time1 = time.perf_counter() - start
    print(f"  结果: {result1}, 耗时: {time1:.4f}秒")
    
    print("\n第二次调用（有缓存）：")
    start = time.perf_counter()
    result2 = cache.get_or_compute("calc_1_2", expensive_calculation, 1, 2)
    time2 = time.perf_counter() - start
    print(f"  结果: {result2}, 耗时: {time2:.4f}秒")
    print(f"  加速比: {time1/time2:.2f}x")
    
    # 测试缓存淘汰
    print("\n测试缓存淘汰策略：")
    for i in range(20):
        key = f"calc_{i}_{i+1}"
        cache.get_or_compute(key, expensive_calculation, i, i+1)
        
    stats = cache.get_stats()
    print(f"  缓存大小: {stats['cache_size']}")
    print(f"  内存使用: {stats['memory_usage_mb']:.2f}MB")
    print(f"  命中率: {stats['hit_rate']:.2%}")
    
    # 测试装饰器模式
    from xwe.core.optimizations import CacheableFunction
    
    @CacheableFunction(cache)
    def fibonacci(n: int) -> int:
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
        
    print("\n测试缓存装饰器（斐波那契数列）：")
    start = time.perf_counter()
    result = fibonacci(30)
    time_first = time.perf_counter() - start
    print(f"  fib(30) = {result}, 首次计算耗时: {time_first:.4f}秒")
    
    start = time.perf_counter()
    result = fibonacci(30)
    time_cached = time.perf_counter() - start
    print(f"  再次调用耗时: {time_cached:.4f}秒")
    print(f"  加速比: {time_first/time_cached:.0f}x")
    

async def test_async_event_system():
    """测试异步事件系统"""
    print("\n=== 异步事件系统测试 ===")
    
    # 创建事件系统
    event_system = AsyncEventSystem(worker_count=4)
    await event_system.start()
    
    # 记录处理时间
    processing_times = []
    
    # 注册事件处理器
    async def slow_handler(event):
        start = time.perf_counter()
        await asyncio.sleep(0.01)  # 模拟耗时操作
        processing_times.append(time.perf_counter() - start)
        
    def fast_handler(event):
        pass
        
    def cpu_intensive_handler(event):
        # 模拟CPU密集型操作
        sum(range(10000))
        
    # 注册处理器
    event_system.register_handler('slow_event', slow_handler, is_async=True)
    event_system.register_handler('fast_event', fast_handler, is_async=False)
    event_system.register_handler('cpu_event', cpu_intensive_handler, 
                                 is_async=False, is_cpu_intensive=True)
    
    # 测试普通事件处理
    print("\n测试并发事件处理：")
    start = time.perf_counter()
    
    # 发送100个慢速事件
    for i in range(100):
        await event_system.emit('slow_event', {'id': i})
        
    # 等待处理完成
    await asyncio.sleep(0.5)
    
    total_time = time.perf_counter() - start
    print(f"  发送100个事件总耗时: {total_time:.4f}秒")
    print(f"  平均处理时间: {sum(processing_times)/len(processing_times):.4f}秒")
    print(f"  并发加速比: {len(processing_times)*0.01/total_time:.2f}x")
    
    # 测试批处理
    print("\n测试批处理功能：")
    batch_count = 0
    
    def batch_handler(events):
        nonlocal batch_count
        batch_count += 1
        print(f"  批处理 {batch_count}: 处理 {len(events)} 个事件")
        
    event_system.register_batch_handler('batch_event', batch_handler, 
                                      batch_size=50, max_wait=0.1)
    
    # 发送批量事件
    for i in range(200):
        await event_system.emit('batch_event', {'id': i})
        await asyncio.sleep(0.001)  # 模拟事件间隔
        
    await asyncio.sleep(0.2)  # 等待批处理完成
    
    # 获取统计
    stats = event_system.get_stats()
    print(f"\n事件系统统计：")
    print(f"  已处理事件: {stats['events_processed']}")
    print(f"  失败事件: {stats['events_failed']}")
    print(f"  批处理次数: {stats['batch_processed']}")
    print(f"  平均延迟: {stats['average_latency']*1000:.2f}ms")
    
    # 关闭事件系统
    await event_system.stop()
    

async def test_combined_optimization():
    """测试组合优化效果"""
    print("\n=== 组合优化测试 ===")
    
    # 创建各个组件
    jit = ExpressionJITCompiler()
    cache = SmartCache(max_memory_mb=10)
    event_system = AsyncEventSystem(worker_count=2)
    await event_system.start()
    
    # 复杂的游戏场景：大量实体进行战斗计算
    damage_formula = {
        "operation": "*",
        "operands": [
            {"attribute": "attacker.power"},
            {
                "operation": "-",
                "operands": [
                    {"constant": 1},
                    {
                        "operation": "/",
                        "operands": [
                            {"attribute": "target.defense"},
                            {"constant": 100}
                        ]
                    }
                ]
            }
        ]
    }
    
    # 编译公式
    damage_calc = jit.compile_expression('damage', damage_formula)
    
    # 创建实体
    entities = []
    for i in range(100):
        entities.append({
            'id': f'entity_{i}',
            'power': random.randint(50, 150),
            'defense': random.randint(20, 80),
            'health': 1000
        })
        
    # 战斗计算函数
    def calculate_battle_result(attacker_id: str, target_id: str):
        attacker = next(e for e in entities if e['id'] == attacker_id)
        target = next(e for e in entities if e['id'] == target_id)
        
        context = {
            'attacker': attacker,
            'target': target
        }
        
        # 使用JIT编译的函数计算伤害
        damage = damage_calc(context)
        
        return {
            'attacker': attacker_id,
            'target': target_id,
            'damage': damage
        }
        
    # 异步战斗处理器
    battle_results = []
    
    async def battle_handler(event):
        key = f"battle_{event.data['attacker']}_{event.data['target']}"
        result = cache.get_or_compute(
            key,
            calculate_battle_result,
            event.data['attacker'],
            event.data['target']
        )
        battle_results.append(result)
        
    event_system.register_handler('battle', battle_handler, is_async=True)
    
    # 模拟大规模战斗
    print("\n模拟1000场战斗：")
    start = time.perf_counter()
    
    for _ in range(1000):
        attacker = random.choice(entities)
        target = random.choice(entities)
        await event_system.emit('battle', {
            'attacker': attacker['id'],
            'target': target['id']
        })
        
    # 等待处理完成
    await asyncio.sleep(1)
    
    total_time = time.perf_counter() - start
    
    print(f"  总耗时: {total_time:.4f}秒")
    print(f"  平均每场战斗: {total_time/1000*1000:.2f}ms")
    print(f"  战斗结果数: {len(battle_results)}")
    
    # 显示优化统计
    cache_stats = cache.get_stats()
    event_stats = event_system.get_stats()
    
    print(f"\n优化效果：")
    print(f"  缓存命中率: {cache_stats['hit_rate']:.2%}")
    print(f"  JIT编译数: {len(jit.compiled_functions)}")
    print(f"  异步处理事件: {event_stats['events_processed']}")
    
    await event_system.stop()
    

async def main():
    """主测试函数"""
    print("=== 修仙世界引擎 性能优化测试 ===")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行各项测试
    test_expression_jit()
    test_smart_cache()
    await test_async_event_system()
    await test_combined_optimization()
    
    print("\n=== 测试完成 ===")
    

if __name__ == '__main__':
    asyncio.run(main())
