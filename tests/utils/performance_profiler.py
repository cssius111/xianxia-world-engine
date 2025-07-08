"""
性能分析工具
用于分析代码性能瓶颈
"""

import time
import cProfile
import pstats
import io
import functools
import threading
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from contextlib import contextmanager
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


@dataclass
class PerformanceMetric:
    """性能指标"""
    function_name: str
    call_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    
    def update(self, duration: float):
        """更新指标"""
        self.call_count += 1
        self.total_time += duration
        self.avg_time = self.total_time / self.call_count
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetric] = {}
        self._lock = threading.Lock()
        self.enabled = True
        
    def profile(self, name: Optional[str] = None):
        """性能分析装饰器"""
        def decorator(func):
            profile_name = name or f"{func.__module__}.{func.__name__}"
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.perf_counter() - start_time
                    self.record(profile_name, duration)
            
            return wrapper
        return decorator
    
    def record(self, name: str, duration: float):
        """记录性能数据"""
        with self._lock:
            if name not in self.metrics:
                self.metrics[name] = PerformanceMetric(name)
            self.metrics[name].update(duration)
    
    @contextmanager
    def measure(self, name: str):
        """上下文管理器方式的性能测量"""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            if self.enabled:
                duration = time.perf_counter() - start_time
                self.record(name, duration)
    
    def get_report(self, sort_by: str = 'total_time', top_n: int = 20) -> str:
        """生成性能报告"""
        sorted_metrics = sorted(
            self.metrics.values(),
            key=lambda m: getattr(m, sort_by),
            reverse=True
        )[:top_n]
        
        report = f"""
性能分析报告
============

按 {sort_by} 排序的前 {top_n} 项:

{'函数名称':<40} {'调用次数':>10} {'总时间(s)':>12} {'平均(ms)':>10} {'最小(ms)':>10} {'最大(ms)':>10}
{'-' * 102}
"""
        
        for metric in sorted_metrics:
            report += f"{metric.function_name:<40} {metric.call_count:>10} {metric.total_time:>12.3f} "
            report += f"{metric.avg_time*1000:>10.2f} {metric.min_time*1000:>10.2f} {metric.max_time*1000:>10.2f}\n"
        
        return report
    
    def plot_metrics(self, output_path: Optional[Path] = None):
        """绘制性能图表"""
        if not self.metrics:
            print("没有性能数据可绘制")
            return
        
        # 准备数据
        names = []
        total_times = []
        avg_times = []
        call_counts = []
        
        for metric in sorted(self.metrics.values(), key=lambda m: m.total_time, reverse=True)[:10]:
            names.append(metric.function_name.split('.')[-1][:20])  # 简化函数名
            total_times.append(metric.total_time)
            avg_times.append(metric.avg_time * 1000)  # 转换为毫秒
            call_counts.append(metric.call_count)
        
        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 总时间柱状图
        ax1.bar(names, total_times)
        ax1.set_xlabel('函数')
        ax1.set_ylabel('总时间 (秒)')
        ax1.set_title('函数总执行时间')
        ax1.tick_params(axis='x', rotation=45)
        
        # 平均时间柱状图
        ax2.bar(names, avg_times, color='orange')
        ax2.set_xlabel('函数')
        ax2.set_ylabel('平均时间 (毫秒)')
        ax2.set_title('函数平均执行时间')
        ax2.tick_params(axis='x', rotation=45)
        
        # 调用次数柱状图
        ax3.bar(names, call_counts, color='green')
        ax3.set_xlabel('函数')
        ax3.set_ylabel('调用次数')
        ax3.set_title('函数调用次数')
        ax3.tick_params(axis='x', rotation=45)
        
        # 时间分布饼图
        ax4.pie(total_times[:5], labels=names[:5], autopct='%1.1f%%')
        ax4.set_title('前5个函数时间占比')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            print(f"性能图表已保存到: {output_path}")
        else:
            plt.show()
    
    def reset(self):
        """重置性能数据"""
        with self._lock:
            self.metrics.clear()
    
    def export_data(self, output_path: Path):
        """导出性能数据"""
        import json
        
        data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': [
                {
                    'function': m.function_name,
                    'calls': m.call_count,
                    'total_time': m.total_time,
                    'avg_time': m.avg_time,
                    'min_time': m.min_time,
                    'max_time': m.max_time
                }
                for m in self.metrics.values()
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"性能数据已导出到: {output_path}")


class CPUProfiler:
    """CPU 分析器"""
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.is_running = False
    
    def start(self):
        """开始分析"""
        if not self.is_running:
            self.profiler.enable()
            self.is_running = True
    
    def stop(self):
        """停止分析"""
        if self.is_running:
            self.profiler.disable()
            self.is_running = False
    
    def get_stats(self, sort_by: str = 'cumulative', top_n: int = 30) -> str:
        """获取统计信息"""
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s)
        ps.strip_dirs()
        ps.sort_stats(sort_by)
        ps.print_stats(top_n)
        return s.getvalue()
    
    @contextmanager
    def profile(self):
        """上下文管理器方式的 CPU 分析"""
        self.start()
        try:
            yield
        finally:
            self.stop()
    
    def save_stats(self, filename: str):
        """保存统计信息到文件"""
        self.profiler.dump_stats(filename)


class FunctionTracer:
    """函数调用追踪器"""
    
    def __init__(self):
        self.call_stack: List[Dict[str, Any]] = []
        self.call_tree: Dict[str, Any] = {}
        self._current_depth = 0
    
    def trace(self, func: Callable) -> Callable:
        """追踪函数调用"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            call_info = {
                'function': func.__name__,
                'args': str(args)[:100],  # 限制长度
                'kwargs': str(kwargs)[:100],
                'depth': self._current_depth,
                'start_time': time.perf_counter(),
                'children': []
            }
            
            # 添加到调用栈
            self.call_stack.append(call_info)
            
            # 更新调用树
            if self._current_depth == 0:
                self.call_tree[func.__name__] = call_info
            else:
                # 找到父调用并添加为子调用
                for i in range(len(self.call_stack) - 2, -1, -1):
                    if self.call_stack[i]['depth'] == self._current_depth - 1:
                        self.call_stack[i]['children'].append(call_info)
                        break
            
            self._current_depth += 1
            
            try:
                result = func(*args, **kwargs)
                call_info['result'] = str(result)[:100]
                return result
            except Exception as e:
                call_info['error'] = str(e)
                raise
            finally:
                self._current_depth -= 1
                call_info['duration'] = time.perf_counter() - call_info['start_time']
                
                # 从调用栈移除
                if self.call_stack and self.call_stack[-1] == call_info:
                    self.call_stack.pop()
        
        return wrapper
    
    def print_call_tree(self, node: Optional[Dict] = None, indent: int = 0):
        """打印调用树"""
        if node is None:
            for root in self.call_tree.values():
                self.print_call_tree(root, 0)
            return
        
        # 打印当前节点
        prefix = "  " * indent + "└─ " if indent > 0 else ""
        duration_ms = node.get('duration', 0) * 1000
        print(f"{prefix}{node['function']} ({duration_ms:.2f}ms)")
        
        # 打印子节点
        for child in node.get('children', []):
            self.print_call_tree(child, indent + 1)


class HotspotAnalyzer:
    """热点分析器"""
    
    def __init__(self):
        self.samples: Dict[str, List[float]] = defaultdict(list)
        self.sampling_interval = 0.001  # 1ms
        self._sampling = False
        self._thread = None
    
    def start_sampling(self, target_func: Callable, *args, **kwargs):
        """开始采样"""
        import sys
        
        self._sampling = True
        
        def sample():
            while self._sampling:
                frame = sys._getframe()
                
                # 遍历调用栈
                while frame:
                    code = frame.f_code
                    func_name = f"{code.co_filename}:{code.co_name}:{frame.f_lineno}"
                    self.samples[func_name].append(time.perf_counter())
                    frame = frame.f_back
                
                time.sleep(self.sampling_interval)
        
        # 启动采样线程
        self._thread = threading.Thread(target=sample)
        self._thread.daemon = True
        self._thread.start()
        
        # 执行目标函数
        try:
            result = target_func(*args, **kwargs)
            return result
        finally:
            self.stop_sampling()
    
    def stop_sampling(self):
        """停止采样"""
        self._sampling = False
        if self._thread:
            self._thread.join()
    
    def get_hotspots(self, top_n: int = 10) -> List[tuple]:
        """获取热点函数"""
        hotspots = []
        
        for func_name, samples in self.samples.items():
            hotspots.append((func_name, len(samples)))
        
        # 按采样次数排序
        hotspots.sort(key=lambda x: x[1], reverse=True)
        
        return hotspots[:top_n]
    
    def print_report(self):
        """打印热点报告"""
        total_samples = sum(len(samples) for samples in self.samples.values())
        
        print(f"\n热点分析报告")
        print(f"总采样数: {total_samples}")
        print(f"\n{'函数':<60} {'采样数':>10} {'占比':>8}")
        print("-" * 80)
        
        for func_name, count in self.get_hotspots():
            percentage = (count / total_samples * 100) if total_samples > 0 else 0
            # 简化函数名显示
            short_name = func_name.split('/')[-1] if '/' in func_name else func_name
            print(f"{short_name:<60} {count:>10} {percentage:>7.1f}%")


# 全局性能分析器实例
_global_profiler = PerformanceProfiler()


def get_profiler() -> PerformanceProfiler:
    """获取全局性能分析器"""
    return _global_profiler


# 便捷装饰器
def profile(name: Optional[str] = None):
    """性能分析装饰器"""
    return _global_profiler.profile(name)


# 导出
__all__ = [
    'PerformanceMetric',
    'PerformanceProfiler',
    'CPUProfiler',
    'FunctionTracer',
    'HotspotAnalyzer',
    'get_profiler',
    'profile'
]
