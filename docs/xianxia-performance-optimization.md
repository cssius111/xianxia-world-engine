# 修仙世界引擎 - 性能优化与测试方案

## 一、性能基准测试框架

### 1.1 基准测试套件

```python
# tests/benchmarks/benchmark_suite.py

import time
import statistics
import json
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    iterations: int
    min_time: float
    max_time: float
    mean_time: float
    median_time: float
    std_dev: float
    ops_per_second: float
    memory_usage: float  # MB
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'iterations': self.iterations,
            'timing': {
                'min': self.min_time,
                'max': self.max_time,
                'mean': self.mean_time,
                'median': self.median_time,
                'std_dev': self.std_dev
            },
            'performance': {
                'ops_per_second': self.ops_per_second,
                'memory_mb': self.memory_usage
            }
        }


class Benchmark:
    """基准测试基类"""
    
    def __init__(self, name: str):
        self.name = name
        
    def setup(self) -> None:
        """测试前准备"""
        pass
        
    def teardown(self) -> None:
        """测试后清理"""
        pass
        
    def run(self) -> Any:
        """运行测试"""
        raise NotImplementedError
        

class BenchmarkRunner:
    """基准测试运行器"""
    
    def __init__(self):
        self.results = []
        
    def run_benchmark(self, benchmark: Benchmark, 
                     iterations: int = 1000,
                     warmup: int = 100) -> BenchmarkResult:
        """运行单个基准测试"""
        print(f"Running benchmark: {benchmark.name}")
        
        # 准备
        benchmark.setup()
        
        # 预热
        for _ in range(warmup):
            benchmark.run()
            
        # 测量内存使用（开始）
        import psutil
        process = psutil.Process()
        memory_start = process.memory_info().rss / 1024 / 1024  # MB
        
        # 正式测试
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            benchmark.run()
            end = time.perf_counter()
            times.append(end - start)
            
            # 进度显示
            if (i + 1) % (iterations // 10) == 0:
                print(f"  Progress: {(i + 1) / iterations * 100:.0f}%")
                
        # 测量内存使用（结束）
        memory_end = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = memory_end - memory_start
        
        # 清理
        benchmark.teardown()
        
        # 计算统计数据
        result = BenchmarkResult(
            name=benchmark.name,
            iterations=iterations,
            min_time=min(times),
            max_time=max(times),
            mean_time=statistics.mean(times),
            median_time=statistics.median(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            ops_per_second=1 / statistics.mean(times),
            memory_usage=memory_usage
        )
        
        self.results.append(result)
        return result
        
    def run_suite(self, benchmarks: List[Benchmark], 
                  iterations: int = 1000) -> List[BenchmarkResult]:
        """运行测试套件"""
        results = []
        
        for benchmark in benchmarks:
            result = self.run_benchmark(benchmark, iterations)
            results.append(result)
            print(f"  Mean time: {result.mean_time*1000:.3f}ms")
            print(f"  Ops/sec: {result.ops_per_second:.2f}")
            print()
            
        return results
        
    def save_results(self, filepath: Path) -> None:
        """保存测试结果"""
        data = {
            'timestamp': time.time(),
            'results': [r.to_dict() for r in self.results]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    def generate_report(self, output_dir: Path) -> None:
        """生成测试报告"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成性能对比图
        self._plot_performance_comparison(output_dir / 'performance_comparison.png')
        
        # 生成内存使用图
        self._plot_memory_usage(output_dir / 'memory_usage.png')
        
        # 生成详细报告
        self._generate_html_report(output_dir / 'report.html')
        
    def _plot_performance_comparison(self, filepath: Path) -> None:
        """绘制性能对比图"""
        names = [r.name for r in self.results]
        mean_times = [r.mean_time * 1000 for r in self.results]  # 转换为毫秒
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(names, mean_times)
        
        # 添加数值标签
        for bar, time in zip(bars, mean_times):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{time:.2f}ms', ha='center', va='bottom')
                    
        plt.xlabel('Benchmark')
        plt.ylabel('Mean Time (ms)')
        plt.title('Performance Comparison')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        
    def _plot_memory_usage(self, filepath: Path) -> None:
        """绘制内存使用图"""
        names = [r.name for r in self.results]
        memory = [r.memory_usage for r in self.results]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(names, memory)
        
        # 添加数值标签
        for bar, mem in zip(bars, memory):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{mem:.2f}MB', ha='center', va='bottom')
                    
        plt.xlabel('Benchmark')
        plt.ylabel('Memory Usage (MB)')
        plt.title('Memory Usage Comparison')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        
    def _generate_html_report(self, filepath: Path) -> None:
        """生成HTML报告"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Benchmark Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .metric { font-weight: bold; }
                img { max-width: 100%; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>修仙世界引擎 - 性能测试报告</h1>
            <p>生成时间: {timestamp}</p>
            
            <h2>测试结果汇总</h2>
            <table>
                <tr>
                    <th>测试名称</th>
                    <th>迭代次数</th>
                    <th>平均耗时</th>
                    <th>最小耗时</th>
                    <th>最大耗时</th>
                    <th>标准差</th>
                    <th>OPS/秒</th>
                    <th>内存使用</th>
                </tr>
                {table_rows}
            </table>
            
            <h2>性能对比图</h2>
            <img src="performance_comparison.png" alt="Performance Comparison">
            
            <h2>内存使用图</h2>
            <img src="memory_usage.png" alt="Memory Usage">
            
            <h2>详细分析</h2>
            <ul>
                <li>最快操作: <span class="metric">{fastest_op}</span> ({fastest_time:.3f}ms)</li>
                <li>最慢操作: <span class="metric">{slowest_op}</span> ({slowest_time:.3f}ms)</li>
                <li>总内存使用: <span class="metric">{total_memory:.2f}MB</span></li>
            </ul>
        </body>
        </html>
        """
        
        # 生成表格行
        table_rows = []
        for r in self.results:
            row = f"""
                <tr>
                    <td>{r.name}</td>
                    <td>{r.iterations}</td>
                    <td>{r.mean_time*1000:.3f}ms</td>
                    <td>{r.min_time*1000:.3f}ms</td>
                    <td>{r.max_time*1000:.3f}ms</td>
                    <td>{r.std_dev*1000:.3f}ms</td>
                    <td>{r.ops_per_second:.2f}</td>
                    <td>{r.memory_usage:.2f}MB</td>
                </tr>
            """
            table_rows.append(row)
            
        # 找出最快和最慢的操作
        fastest = min(self.results, key=lambda r: r.mean_time)
        slowest = max(self.results, key=lambda r: r.mean_time)
        
        # 填充模板
        html = html.format(
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            table_rows=''.join(table_rows),
            fastest_op=fastest.name,
            fastest_time=fastest.mean_time * 1000,
            slowest_op=slowest.name,
            slowest_time=slowest.mean_time * 1000,
            total_memory=sum(r.memory_usage for r in self.results)
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
```

### 1.2 具体测试用例

```python
# tests/benchmarks/engine_benchmarks.py

from xwe.core.expression import ExpressionEngine
from xwe.core.event import EventSystem, GameEvent
from xwe.core.data import DataManager
from xwe.features.combat import CombatModule
import random


class ExpressionEvaluationBenchmark(Benchmark):
    """表达式计算性能测试"""
    
    def __init__(self):
        super().__init__("Expression Evaluation")
        self.engine = ExpressionEngine()
        
        # 复杂表达式
        self.expression = {
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
        
        self.context = {
            "player": {
                "attack": 100,
                "level": 10
            },
            "skill": {
                "level": 5
            },
            "target": {
                "defense": 50,
                "armor": 20
            }
        }
        
    def run(self):
        return self.engine.evaluate(self.expression, self.context)


class EventSystemBenchmark(Benchmark):
    """事件系统性能测试"""
    
    def __init__(self):
        super().__init__("Event System")
        self.event_system = EventSystem()
        self.counter = 0
        
        # 注册多个监听器
        for i in range(10):
            self.event_system.register(
                'test_event', 
                lambda e: self._handle_event(e),
                priority=i
            )
            
    def _handle_event(self, event):
        self.counter += 1
        
    def run(self):
        # 发送多个事件
        for i in range(100):
            self.event_system.emit('test_event', {'value': i})
        self.event_system.process_queue()


class DataAccessBenchmark(Benchmark):
    """数据访问性能测试"""
    
    def __init__(self):
        super().__init__("Data Access")
        self.data_manager = DataManager()
        
    def setup(self):
        # 创建测试数据
        test_data = {
            "characters": {
                f"npc_{i}": {
                    "name": f"NPC {i}",
                    "attributes": {
                        "health": random.randint(100, 1000),
                        "attack": random.randint(10, 100),
                        "defense": random.randint(5, 50)
                    }
                }
                for i in range(1000)
            }
        }
        
        self.data_manager.data['test'] = test_data
        
    def run(self):
        # 随机访问数据
        for _ in range(100):
            npc_id = f"npc_{random.randint(0, 999)}"
            path = f"test.characters.{npc_id}.attributes.health"
            value = self.data_manager.get(path)


class CombatCalculationBenchmark(Benchmark):
    """战斗计算性能测试"""
    
    def __init__(self):
        super().__init__("Combat Calculation")
        self.combat_module = CombatModule()
        
    def setup(self):
        # 初始化战斗模块
        from xwe.core.engine import GameEngine
        engine = GameEngine()
        
        config = {
            "damage_formulas": {
                "physical": {
                    "base": {
                        "operation": "*",
                        "operands": [
                            {"attribute": "strength"},
                            {"constant": 2}
                        ]
                    },
                    "defense": {
                        "operation": "*",
                        "operands": [
                            {"attribute": "defense"},
                            {"constant": 0.5}
                        ]
                    },
                    "critical_chance": {"constant": 0.1},
                    "critical_multiplier": {"constant": 2.0},
                    "variance": 0.1
                }
            }
        }
        
        self.combat_module.initialize(engine, config)
        
        # 创建测试实体
        from xwe.features.combat import CombatEntity
        self.attacker = CombatEntity(
            id="attacker",
            name="攻击者",
            attributes={"strength": 100, "health": 1000},
            skills=[],
            team=0
        )
        
        self.defender = CombatEntity(
            id="defender",
            name="防御者",
            attributes={"defense": 50, "health": 1000},
            skills=[],
            team=1
        )
        
    def run(self):
        # 计算伤害
        for _ in range(10):
            self.combat_module._calculate_damage(
                self.attacker, 
                self.defender, 
                'physical'
            )


class BatchUpdateBenchmark(Benchmark):
    """批量更新性能测试"""
    
    def __init__(self):
        super().__init__("Batch Update")
        self.entities = []
        
    def setup(self):
        # 创建大量实体
        for i in range(1000):
            entity = {
                'id': f'entity_{i}',
                'health': 100,
                'mana': 50,
                'position': {'x': i % 100, 'y': i // 100}
            }
            self.entities.append(entity)
            
    def run(self):
        # 批量更新所有实体
        for entity in self.entities:
            entity['health'] -= 1
            entity['mana'] += 0.5
            entity['position']['x'] += random.randint(-1, 1)
            entity['position']['y'] += random.randint(-1, 1)


# 运行基准测试
if __name__ == '__main__':
    runner = BenchmarkRunner()
    
    benchmarks = [
        ExpressionEvaluationBenchmark(),
        EventSystemBenchmark(),
        DataAccessBenchmark(),
        CombatCalculationBenchmark(),
        BatchUpdateBenchmark()
    ]
    
    # 运行测试
    results = runner.run_suite(benchmarks, iterations=1000)
    
    # 保存结果
    runner.save_results(Path('benchmark_results.json'))
    
    # 生成报告
    runner.generate_report(Path('benchmark_report'))
```

## 二、性能优化实施

### 2.1 表达式缓存优化

```python
# xwe/core/expression_optimized.py

from functools import lru_cache
import hashlib
import json
from typing import Any, Dict, Tuple


class OptimizedExpressionEngine(ExpressionEngine):
    """优化的表达式引擎"""
    
    def __init__(self):
        super().__init__()
        self._compiled_cache = {}
        self._result_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
    def evaluate(self, expression: Any, context: Dict[str, Any]) -> Any:
        """带缓存的表达式计算"""
        # 生成缓存键
        cache_key = self._generate_cache_key(expression, context)
        
        # 检查结果缓存
        if cache_key in self._result_cache:
            self.cache_hits += 1
            return self._result_cache[cache_key]
            
        self.cache_misses += 1
        
        # 计算结果
        result = self._evaluate_internal(expression, context)
        
        # 缓存结果
        self._result_cache[cache_key] = result
        
        # 限制缓存大小
        if len(self._result_cache) > 10000:
            # 删除最老的一半缓存
            keys = list(self._result_cache.keys())
            for key in keys[:5000]:
                del self._result_cache[key]
                
        return result
        
    def _generate_cache_key(self, expression: Any, context: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 将表达式和相关上下文序列化
        expr_str = json.dumps(expression, sort_keys=True)
        
        # 只包含表达式中引用的上下文值
        relevant_context = self._extract_relevant_context(expression, context)
        context_str = json.dumps(relevant_context, sort_keys=True)
        
        # 生成哈希
        key = hashlib.md5(f"{expr_str}:{context_str}".encode()).hexdigest()
        return key
        
    def _extract_relevant_context(self, expression: Any, 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """提取表达式中引用的上下文值"""
        relevant = {}
        
        def extract(expr):
            if isinstance(expr, dict):
                if 'attribute' in expr:
                    path = expr['attribute']
                    value = self._get_attribute(context, path)
                    relevant[path] = value
                elif 'operation' in expr:
                    for operand in expr.get('operands', []):
                        extract(operand)
                        
        extract(expression)
        return relevant
        
    def compile_expression(self, expression: Dict[str, Any]) -> 'CompiledExpression':
        """预编译表达式"""
        expr_str = json.dumps(expression, sort_keys=True)
        
        if expr_str not in self._compiled_cache:
            compiled = CompiledExpression(expression, self)
            self._compiled_cache[expr_str] = compiled
            
        return self._compiled_cache[expr_str]


class CompiledExpression:
    """编译后的表达式"""
    
    def __init__(self, expression: Dict[str, Any], engine: ExpressionEngine):
        self.expression = expression
        self.engine = engine
        self._optimize()
        
    def _optimize(self):
        """优化表达式"""
        # 预计算常量子表达式
        self._precompute_constants(self.expression)
        
    def _precompute_constants(self, expr):
        """预计算常量表达式"""
        if isinstance(expr, dict) and 'operation' in expr:
            operands = expr.get('operands', [])
            
            # 检查是否所有操作数都是常量
            all_constants = all(
                isinstance(op, (int, float)) or 
                (isinstance(op, dict) and 'constant' in op)
                for op in operands
            )
            
            if all_constants:
                # 计算常量结果
                result = self.engine.evaluate(expr, {})
                # 替换为常量
                expr.clear()
                expr['constant'] = result
            else:
                # 递归优化子表达式
                for operand in operands:
                    if isinstance(operand, dict):
                        self._precompute_constants(operand)
                        
    def evaluate(self, context: Dict[str, Any]) -> Any:
        """计算编译后的表达式"""
        return self.engine.evaluate(self.expression, context)
```

### 2.2 事件系统优化

```python
# xwe/core/event_optimized.py

from collections import defaultdict, deque
from typing import List, Dict, Set
import asyncio


class OptimizedEventSystem(EventSystem):
    """优化的事件系统"""
    
    def __init__(self):
        super().__init__()
        # 事件类型索引
        self.event_type_index = defaultdict(set)
        # 异步事件队列
        self.async_queue = asyncio.Queue()
        # 事件批处理缓冲
        self.batch_buffer = defaultdict(list)
        self.batch_size = 100
        self.batch_timeout = 0.1  # 秒
        
    def register(self, event_type: str, handler: callable, 
                 priority: int = 0, async_handler: bool = False) -> None:
        """注册事件监听器（支持异步）"""
        listener = {
            'handler': handler,
            'priority': priority,
            'async': async_handler,
            'id': f"{event_type}_{id(handler)}"
        }
        
        self.listeners[event_type].append(listener)
        self.listeners[event_type].sort(key=lambda x: x['priority'], reverse=True)
        
        # 更新索引
        self.event_type_index[event_type].add(listener['id'])
        
    def emit_batch(self, events: List[Tuple[str, Dict[str, Any]]]) -> None:
        """批量发送事件"""
        for event_type, data in events:
            self.batch_buffer[event_type].append(data)
            
            # 检查是否达到批处理阈值
            if len(self.batch_buffer[event_type]) >= self.batch_size:
                self._flush_batch(event_type)
                
    def _flush_batch(self, event_type: str) -> None:
        """刷新批处理缓冲"""
        if not self.batch_buffer[event_type]:
            return
            
        # 创建批处理事件
        batch_data = {
            'batch': True,
            'events': self.batch_buffer[event_type]
        }
        
        event = GameEvent(
            type=f"{event_type}_batch",
            data=batch_data
        )
        
        self.event_queue.append(event)
        self.batch_buffer[event_type].clear()
        
    async def process_async_queue(self) -> None:
        """处理异步事件队列"""
        while True:
            event = await self.async_queue.get()
            
            # 异步处理事件
            tasks = []
            for listener in self.listeners[event.type]:
                if listener['async']:
                    task = asyncio.create_task(
                        listener['handler'](event)
                    )
                    tasks.append(task)
                    
            # 等待所有异步处理完成
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
```

### 2.3 数据访问优化

```python
# xwe/core/data_optimized.py

import mmap
import pickle
from typing import Any, Dict, Optional
import threading


class OptimizedDataManager(DataManager):
    """优化的数据管理器"""
    
    def __init__(self):
        super().__init__()
        # 读写锁
        self._lock = threading.RWLock()
        # 内存映射文件
        self._mmap_files = {}
        # 预加载的热数据
        self._hot_data = {}
        # 访问计数器
        self._access_counter = defaultdict(int)
        
    def load_data_optimized(self, name: str, data_path: Path,
                           use_mmap: bool = False) -> Dict[str, Any]:
        """优化的数据加载"""
        if use_mmap and data_path.suffix == '.dat':
            # 使用内存映射文件
            return self._load_mmap_data(name, data_path)
        else:
            # 普通加载，但使用更快的解析器
            import ujson  # 更快的JSON解析器
            
            with open(data_path, 'r', encoding='utf-8') as f:
                data = ujson.load(f)
                
            self.data[name] = data
            
            # 识别热数据
            self._identify_hot_data(name, data)
            
            return data
            
    def _load_mmap_data(self, name: str, data_path: Path) -> Dict[str, Any]:
        """使用内存映射加载数据"""
        with open(data_path, 'rb') as f:
            # 创建内存映射
            mmapped = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            self._mmap_files[name] = mmapped
            
            # 反序列化
            data = pickle.loads(mmapped[:])
            self.data[name] = data
            
            return data
            
    def get_optimized(self, path: str, default: Any = None) -> Any:
        """优化的数据获取"""
        # 更新访问计数
        self._access_counter[path] += 1
        
        # 检查热数据
        if path in self._hot_data:
            return self._hot_data[path]
            
        # 使用读锁
        with self._lock.read():
            return super().get(path, default)
            
    def _identify_hot_data(self, category: str, data: Dict[str, Any]) -> None:
        """识别并缓存热数据"""
        # 预定义的热数据路径
        hot_paths = {
            'combat': ['damage_formulas', 'element_matrix'],
            'character': ['attribute_formulas', 'realm_data'],
            'skills': ['skill_list', 'cooldowns']
        }
        
        if category in hot_paths:
            for path in hot_paths[category]:
                value = self._get_nested(data, path)
                if value is not None:
                    full_path = f"{category}.{path}"
                    self._hot_data[full_path] = value
                    
    def _get_nested(self, data: Dict[str, Any], path: str) -> Any:
        """获取嵌套值"""
        parts = path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current


class ThreadingRWLock:
    """读写锁实现"""
    
    def __init__(self):
        self._read_ready = threading.Condition(threading.RLock())
        self._readers = 0
        
    def read(self):
        return self.ReadLock(self)
        
    def write(self):
        return self.WriteLock(self)
        
    class ReadLock:
        def __init__(self, rwlock):
            self.rwlock = rwlock
            
        def __enter__(self):
            self.rwlock._read_ready.acquire()
            self.rwlock._readers += 1
            self.rwlock._read_ready.release()
            
        def __exit__(self, *args):
            self.rwlock._read_ready.acquire()
            self.rwlock._readers -= 1
            if self.rwlock._readers == 0:
                self.rwlock._read_ready.notifyAll()
            self.rwlock._read_ready.release()
            
    class WriteLock:
        def __init__(self, rwlock):
            self.rwlock = rwlock
            
        def __enter__(self):
            self.rwlock._read_ready.acquire()
            while self.rwlock._readers > 0:
                self.rwlock._read_ready.wait()
                
        def __exit__(self, *args):
            self.rwlock._read_ready.release()
```

## 三、压力测试方案

### 3.1 并发压力测试

```python
# tests/stress/concurrent_test.py

import asyncio
import aiohttp
import time
from typing import List, Dict
import statistics


class ConcurrentStressTest:
    """并发压力测试"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    async def make_request(self, session: aiohttp.ClientSession, 
                          endpoint: str, data: Dict) -> Dict:
        """发送单个请求"""
        start_time = time.time()
        
        try:
            async with session.post(f"{self.base_url}{endpoint}", 
                                   json=data) as response:
                result = await response.json()
                latency = time.time() - start_time
                
                return {
                    'success': True,
                    'latency': latency,
                    'status': response.status,
                    'result': result
                }
        except Exception as e:
            return {
                'success': False,
                'latency': time.time() - start_time,
                'error': str(e)
            }
            
    async def run_concurrent_requests(self, endpoint: str, 
                                     data: Dict,
                                     num_requests: int = 1000,
                                     concurrency: int = 100) -> None:
        """运行并发请求"""
        print(f"Running {num_requests} requests with concurrency {concurrency}")
        
        async with aiohttp.ClientSession() as session:
            # 创建请求任务
            tasks = []
            for i in range(num_requests):
                task = self.make_request(session, endpoint, data)
                tasks.append(task)
                
                # 控制并发数
                if len(tasks) >= concurrency:
                    results = await asyncio.gather(*tasks)
                    self.results.extend(results)
                    tasks = []
                    
                    # 显示进度
                    if (i + 1) % 100 == 0:
                        print(f"Progress: {(i + 1) / num_requests * 100:.1f}%")
                        
            # 处理剩余请求
            if tasks:
                results = await asyncio.gather(*tasks)
                self.results.extend(results)
                
    def analyze_results(self) -> Dict:
        """分析测试结果"""
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        if not successful:
            return {'error': 'All requests failed'}
            
        latencies = [r['latency'] for r in successful]
        
        return {
            'total_requests': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(self.results) * 100,
            'latency': {
                'min': min(latencies),
                'max': max(latencies),
                'mean': statistics.mean(latencies),
                'median': statistics.median(latencies),
                'p95': statistics.quantiles(latencies, n=20)[18],  # 95th percentile
                'p99': statistics.quantiles(latencies, n=100)[98],  # 99th percentile
            },
            'throughput': len(successful) / sum(latencies)  # requests per second
        }
        
    async def stress_test_combat(self) -> None:
        """压力测试战斗系统"""
        # 创建战斗请求
        combat_data = {
            'attacker_id': 'player_1',
            'target_id': 'monster_1',
            'skill_id': 'basic_attack'
        }
        
        await self.run_concurrent_requests(
            '/api/combat/attack',
            combat_data,
            num_requests=5000,
            concurrency=200
        )
        
        results = self.analyze_results()
        print("\nCombat System Stress Test Results:")
        print(f"Success Rate: {results['success_rate']:.2f}%")
        print(f"Mean Latency: {results['latency']['mean']*1000:.2f}ms")
        print(f"P95 Latency: {results['latency']['p95']*1000:.2f}ms")
        print(f"Throughput: {results['throughput']:.2f} req/s")
        
    async def stress_test_data_access(self) -> None:
        """压力测试数据访问"""
        # 随机数据访问请求
        data_requests = []
        for i in range(100):
            data_requests.append({
                'path': f'characters.npc_{i % 50}.attributes',
                'operation': 'get'
            })
            
        tasks = []
        for _ in range(50):  # 每个请求重复50次
            for req in data_requests:
                task = self.run_concurrent_requests(
                    '/api/data/query',
                    req,
                    num_requests=10,
                    concurrency=10
                )
                tasks.append(task)
                
        await asyncio.gather(*tasks)
        
        results = self.analyze_results()
        print("\nData Access Stress Test Results:")
        print(f"Total Requests: {results['total_requests']}")
        print(f"Success Rate: {results['success_rate']:.2f}%")
        print(f"Mean Latency: {results['latency']['mean']*1000:.2f}ms")


# 运行压力测试
async def main():
    tester = ConcurrentStressTest()
    
    # 测试战斗系统
    await tester.stress_test_combat()
    
    # 清空结果
    tester.results = []
    
    # 测试数据访问
    await tester.stress_test_data_access()


if __name__ == '__main__':
    asyncio.run(main())
```

### 3.2 内存压力测试

```python
# tests/stress/memory_test.py

import psutil
import tracemalloc
import gc
from typing import List, Dict
import matplotlib.pyplot as plt
from datetime import datetime


class MemoryStressTest:
    """内存压力测试"""
    
    def __init__(self):
        self.memory_samples = []
        self.process = psutil.Process()
        
    def start_monitoring(self):
        """开始内存监控"""
        tracemalloc.start()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
    def sample_memory(self, label: str = ""):
        """采样内存使用"""
        current, peak = tracemalloc.get_traced_memory()
        rss = self.process.memory_info().rss / 1024 / 1024  # MB
        
        sample = {
            'timestamp': datetime.now(),
            'label': label,
            'traced_current': current / 1024 / 1024,  # MB
            'traced_peak': peak / 1024 / 1024,  # MB
            'rss': rss,
            'rss_delta': rss - self.initial_memory
        }
        
        self.memory_samples.append(sample)
        return sample
        
    def stress_test_entity_creation(self, num_entities: int = 100000):
        """测试大量实体创建"""
        print(f"Creating {num_entities} entities...")
        
        self.sample_memory("Before entity creation")
        
        entities = []
        for i in range(num_entities):
            entity = {
                'id': f'entity_{i}',
                'name': f'Entity {i}',
                'attributes': {
                    'health': 100 + i % 1000,
                    'mana': 50 + i % 500,
                    'attack': 10 + i % 100,
                    'defense': 5 + i % 50,
                    'speed': 10 + i % 20
                },
                'position': {
                    'x': i % 1000,
                    'y': (i // 1000) % 1000,
                    'z': i // 1000000
                },
                'status_effects': [],
                'inventory': [f'item_{j}' for j in range(i % 10)]
            }
            entities.append(entity)
            
            # 定期采样
            if i % 10000 == 0:
                self.sample_memory(f"Created {i} entities")
                
        self.sample_memory("After entity creation")
        
        # 测试内存释放
        print("Clearing entities...")
        entities.clear()
        gc.collect()
        
        self.sample_memory("After clearing entities")
        
    def stress_test_event_queue(self, num_events: int = 1000000):
        """测试事件队列内存使用"""
        from xwe.core.event import EventSystem
        
        print(f"Queueing {num_events} events...")
        
        event_system = EventSystem()
        self.sample_memory("Before event queueing")
        
        # 注册一些监听器
        for i in range(100):
            event_system.register(f'event_type_{i % 10}', lambda e: None)
            
        # 发送大量事件
        for i in range(num_events):
            event_system.emit(
                f'event_type_{i % 10}',
                {'value': i, 'data': 'x' * 100}  # 每个事件带一些数据
            )
            
            if i % 100000 == 0:
                self.sample_memory(f"Queued {i} events")
                
        self.sample_memory("After event queueing")
        
        # 处理事件
        print("Processing events...")
        event_system.process_queue()
        
        self.sample_memory("After processing events")
        
    def generate_report(self, output_path: str = "memory_report.png"):
        """生成内存使用报告"""
        if not self.memory_samples:
            print("No memory samples to report")
            return
            
        # 提取数据
        timestamps = [s['timestamp'] for s in self.memory_samples]
        rss_values = [s['rss'] for s in self.memory_samples]
        traced_current = [s['traced_current'] for s in self.memory_samples]
        labels = [s['label'] for s in self.memory_samples]
        
        # 绘制图表
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 1, 1)
        plt.plot(range(len(timestamps)), rss_values, 'b-', label='RSS Memory')
        plt.plot(range(len(timestamps)), traced_current, 'r-', label='Traced Memory')
        plt.xlabel('Sample')
        plt.ylabel('Memory (MB)')
        plt.title('Memory Usage Over Time')
        plt.legend()
        plt.grid(True)
        
        # 添加标签
        for i, label in enumerate(labels):
            if label:
                plt.annotate(label, (i, rss_values[i]), 
                           xytext=(i, rss_values[i] + 50),
                           rotation=45, fontsize=8)
                           
        plt.subplot(2, 1, 2)
        rss_delta = [s['rss_delta'] for s in self.memory_samples]
        plt.bar(range(len(timestamps)), rss_delta)
        plt.xlabel('Sample')
        plt.ylabel('Memory Delta (MB)')
        plt.title('Memory Change from Initial')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        # 打印摘要
        print("\nMemory Test Summary:")
        print(f"Initial Memory: {self.initial_memory:.2f} MB")
        print(f"Peak Memory: {max(rss_values):.2f} MB")
        print(f"Final Memory: {rss_values[-1]:.2f} MB")
        print(f"Max Delta: {max(rss_delta):.2f} MB")
        
    def get_top_memory_consumers(self, limit: int = 10):
        """获取内存占用最大的对象"""
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        print(f"\nTop {limit} memory consumers:")
        for i, stat in enumerate(top_stats[:limit], 1):
            print(f"{i}. {stat}")


# 运行内存压力测试
if __name__ == '__main__':
    tester = MemoryStressTest()
    
    # 开始监控
    tester.start_monitoring()
    
    # 测试实体创建
    tester.stress_test_entity_creation(50000)
    
    # 测试事件队列
    tester.stress_test_event_queue(100000)
    
    # 获取内存占用最大的对象
    tester.get_top_memory_consumers()
    
    # 生成报告
    tester.generate_report()
    
    # 停止监控
    tracemalloc.stop()
```

## 四、性能监控仪表板

```python
# xwe/monitoring/dashboard.py

from flask import Flask, render_template, jsonify
import psutil
import time
from collections import deque
from threading import Thread
import json


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_samples: int = 300):
        self.max_samples = max_samples
        self.cpu_history = deque(maxlen=max_samples)
        self.memory_history = deque(maxlen=max_samples)
        self.fps_history = deque(maxlen=max_samples)
        self.event_count_history = deque(maxlen=max_samples)
        
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, engine):
        """开始监控"""
        self.monitoring = True
        self.engine = engine
        self.monitor_thread = Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self):
        """监控循环"""
        process = psutil.Process()
        
        while self.monitoring:
            # CPU使用率
            cpu_percent = process.cpu_percent(interval=0.1)
            self.cpu_history.append({
                'timestamp': time.time(),
                'value': cpu_percent
            })
            
            # 内存使用
            memory_info = process.memory_info()
            self.memory_history.append({
                'timestamp': time.time(),
                'value': memory_info.rss / 1024 / 1024  # MB
            })
            
            # FPS（假设从引擎获取）
            if hasattr(self.engine, 'get_fps'):
                fps = self.engine.get_fps()
                self.fps_history.append({
                    'timestamp': time.time(),
                    'value': fps
                })
                
            # 事件处理数量
            if hasattr(self.engine, 'events'):
                event_count = len(self.engine.events.event_history)
                self.event_count_history.append({
                    'timestamp': time.time(),
                    'value': event_count
                })
                
            time.sleep(1)  # 每秒采样一次
            
    def get_current_stats(self):
        """获取当前统计数据"""
        return {
            'cpu': list(self.cpu_history),
            'memory': list(self.memory_history),
            'fps': list(self.fps_history),
            'events': list(self.event_count_history),
            'cache_stats': self._get_cache_stats()
        }
        
    def _get_cache_stats(self):
        """获取缓存统计"""
        if hasattr(self.engine, 'expressions'):
            expr_engine = self.engine.expressions
            if hasattr(expr_engine, 'cache_hits'):
                total = expr_engine.cache_hits + expr_engine.cache_misses
                hit_rate = expr_engine.cache_hits / total if total > 0 else 0
                
                return {
                    'expression_cache': {
                        'hits': expr_engine.cache_hits,
                        'misses': expr_engine.cache_misses,
                        'hit_rate': hit_rate * 100
                    }
                }
                
        return {}


# Flask应用
app = Flask(__name__)
monitor = PerformanceMonitor()


@app.route('/')
def dashboard():
    """渲染监控仪表板"""
    return render_template('dashboard.html')


@app.route('/api/stats')
def get_stats():
    """获取实时统计数据"""
    return jsonify(monitor.get_current_stats())


@app.route('/api/engine/info')
def get_engine_info():
    """获取引擎信息"""
    if hasattr(monitor, 'engine'):
        info = {
            'modules': list(monitor.engine.modules.keys()),
            'total_time': monitor.engine.total_time,
            'active_combats': len(monitor.engine.modules.get('combat', {}).active_combats)
            if 'combat' in monitor.engine.modules else 0
        }
        return jsonify(info)
    return jsonify({})
```

## 五、性能优化总结

### 5.1 优化成果预期

| 优化项 | 优化前 | 优化后 | 提升比例 |
|--------|--------|--------|----------|
| 表达式计算 | 5ms | 0.5ms | 10x |
| 事件处理 | 2ms | 0.2ms | 10x |
| 数据访问 | 1ms | 0.1ms | 10x |
| 内存占用 | 500MB | 300MB | 40% |
| 并发处理 | 100 req/s | 1000 req/s | 10x |

### 5.2 最佳实践

1. **缓存策略**
   - 对频繁访问的数据使用LRU缓存
   - 预计算复杂表达式
   - 缓存热点数据路径

2. **内存管理**
   - 使用对象池减少GC压力
   - 及时清理过期数据
   - 使用内存映射处理大文件

3. **并发优化**
   - 使用读写锁保护共享数据
   - 异步处理非关键操作
   - 批量处理相似请求

4. **监控告警**
   - 实时监控关键指标
   - 设置性能阈值告警
   - 定期进行性能测试

通过这些优化措施，修仙世界引擎3.0将能够支持更大规模的游戏世界和更多的并发玩家，同时保持流畅的游戏体验。