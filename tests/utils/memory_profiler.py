"""
内存分析工具
用于检测内存泄漏和优化内存使用
"""

import gc
import sys
import time
import psutil
import tracemalloc
import weakref
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import matplotlib.pyplot as plt
from pathlib import Path
import objgraph


@dataclass
class MemorySnapshot:
    """内存快照"""
    timestamp: float
    rss_mb: float  # 常驻内存集
    vms_mb: float  # 虚拟内存大小
    available_mb: float  # 可用内存
    percent: float  # 内存使用百分比
    gc_stats: Dict[int, Dict[str, int]]  # GC 统计
    top_types: List[Tuple[str, int]]  # 占用最多的对象类型


class MemoryProfiler:
    """内存分析器"""
    
    def __init__(self):
        self.snapshots: List[MemorySnapshot] = []
        self.tracemalloc_started = False
        self.baseline_snapshot = None
        self.leaking_objects: weakref.WeakSet = weakref.WeakSet()
        
    def start_tracking(self):
        """开始内存跟踪"""
        if not self.tracemalloc_started:
            tracemalloc.start()
            self.tracemalloc_started = True
            self.baseline_snapshot = self.take_snapshot()
    
    def stop_tracking(self):
        """停止内存跟踪"""
        if self.tracemalloc_started:
            tracemalloc.stop()
            self.tracemalloc_started = False
    
    def take_snapshot(self) -> MemorySnapshot:
        """获取内存快照"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # 系统内存信息
        vm = psutil.virtual_memory()
        
        # GC 统计
        gc_stats = {}
        for generation in range(gc.get_count().__len__()):
            gc_stats[generation] = {
                'collections': gc.get_stats()[generation]['collections'],
                'collected': gc.get_stats()[generation]['collected'],
                'uncollectable': gc.get_stats()[generation]['uncollectable'],
            }
        
        # 对象类型统计
        top_types = []
        if hasattr(objgraph, 'most_common_types'):
            top_types = objgraph.most_common_types(limit=10)
        
        snapshot = MemorySnapshot(
            timestamp=time.time(),
            rss_mb=memory_info.rss / 1024 / 1024,
            vms_mb=memory_info.vms / 1024 / 1024,
            available_mb=vm.available / 1024 / 1024,
            percent=vm.percent,
            gc_stats=gc_stats,
            top_types=top_types
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_memory_diff(self) -> Optional[Dict[str, Any]]:
        """获取内存差异"""
        if not self.tracemalloc_started or not self.baseline_snapshot:
            return None
        
        current = tracemalloc.take_snapshot()
        
        if hasattr(self, '_last_snapshot'):
            # 比较快照
            top_stats = current.compare_to(self._last_snapshot, 'lineno')
            
            diff = {
                'top_increases': [],
                'top_decreases': [],
                'total_diff': 0
            }
            
            for stat in top_stats[:10]:
                if stat.size_diff > 0:
                    diff['top_increases'].append({
                        'file': stat.traceback.format()[0],
                        'size_diff': stat.size_diff,
                        'size_diff_mb': stat.size_diff / 1024 / 1024,
                        'count_diff': stat.count_diff
                    })
                
                diff['total_diff'] += stat.size_diff
            
            for stat in reversed(top_stats[-10:]):
                if stat.size_diff < 0:
                    diff['top_decreases'].append({
                        'file': stat.traceback.format()[0],
                        'size_diff': stat.size_diff,
                        'size_diff_mb': stat.size_diff / 1024 / 1024,
                        'count_diff': stat.count_diff
                    })
            
            self._last_snapshot = current
            return diff
        
        self._last_snapshot = current
        return None
    
    def find_memory_leaks(self, threshold_mb: float = 10.0) -> List[Dict[str, Any]]:
        """查找内存泄漏"""
        if len(self.snapshots) < 2:
            return []
        
        leaks = []
        
        # 分析内存增长趋势
        memory_growth = []
        for i in range(1, len(self.snapshots)):
            prev = self.snapshots[i-1]
            curr = self.snapshots[i]
            
            growth = curr.rss_mb - prev.rss_mb
            time_diff = curr.timestamp - prev.timestamp
            
            if time_diff > 0:
                growth_rate = growth / time_diff  # MB/秒
                memory_growth.append({
                    'timestamp': curr.timestamp,
                    'growth': growth,
                    'growth_rate': growth_rate,
                    'total_memory': curr.rss_mb
                })
        
        # 检测持续增长
        if len(memory_growth) >= 3:
            recent_growth = [g['growth'] for g in memory_growth[-3:]]
            
            if all(g > 0 for g in recent_growth):
                total_growth = sum(recent_growth)
                
                if total_growth > threshold_mb:
                    leaks.append({
                        'type': 'continuous_growth',
                        'total_growth_mb': total_growth,
                        'avg_growth_rate': sum(g['growth_rate'] for g in memory_growth[-3:]) / 3,
                        'description': f'内存持续增长 {total_growth:.2f}MB'
                    })
        
        # 检测大对象
        if self.tracemalloc_started:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('traceback')
            
            for stat in top_stats[:10]:
                if stat.size > threshold_mb * 1024 * 1024:  # 转换为字节
                    leaks.append({
                        'type': 'large_allocation',
                        'size_mb': stat.size / 1024 / 1024,
                        'traceback': stat.traceback.format(),
                        'description': f'大内存分配 {stat.size / 1024 / 1024:.2f}MB'
                    })
        
        return leaks
    
    def analyze_object_growth(self) -> Dict[str, List[int]]:
        """分析对象增长"""
        object_growth = defaultdict(list)
        
        for snapshot in self.snapshots:
            for obj_type, count in snapshot.top_types:
                object_growth[obj_type].append(count)
        
        return dict(object_growth)
    
    def generate_report(self) -> str:
        """生成内存分析报告"""
        if not self.snapshots:
            return "没有内存快照数据"
        
        report = f"""
内存分析报告
============

分析时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
快照数量: {len(self.snapshots)}

内存使用趋势
------------
"""
        
        # 内存使用统计
        if len(self.snapshots) >= 2:
            first = self.snapshots[0]
            last = self.snapshots[-1]
            
            report += f"初始内存: {first.rss_mb:.2f}MB\n"
            report += f"最终内存: {last.rss_mb:.2f}MB\n"
            report += f"内存增长: {last.rss_mb - first.rss_mb:.2f}MB\n"
            report += f"增长率: {((last.rss_mb - first.rss_mb) / first.rss_mb * 100):.1f}%\n"
        
        # 内存泄漏检测
        leaks = self.find_memory_leaks()
        if leaks:
            report += "\n潜在内存泄漏\n"
            report += "-" * 50 + "\n"
            
            for leak in leaks:
                report += f"- {leak['description']}\n"
                if 'traceback' in leak:
                    report += f"  位置: {leak['traceback'][0]}\n"
        
        # 对象增长分析
        object_growth = self.analyze_object_growth()
        if object_growth:
            report += "\n对象类型增长\n"
            report += "-" * 50 + "\n"
            
            for obj_type, counts in object_growth.items():
                if len(counts) >= 2:
                    growth = counts[-1] - counts[0]
                    if growth > 0:
                        report += f"- {obj_type}: {counts[0]} -> {counts[-1]} (+{growth})\n"
        
        # GC 统计
        if self.snapshots:
            last_snapshot = self.snapshots[-1]
            report += "\nGC 统计\n"
            report += "-" * 50 + "\n"
            
            for gen, stats in last_snapshot.gc_stats.items():
                report += f"Generation {gen}:\n"
                report += f"  收集次数: {stats['collections']}\n"
                report += f"  已收集: {stats['collected']}\n"
                report += f"  不可收集: {stats['uncollectable']}\n"
        
        return report
    
    def plot_memory_usage(self, output_path: Optional[Path] = None):
        """绘制内存使用图表"""
        if len(self.snapshots) < 2:
            print("快照数量不足，无法绘制图表")
            return
        
        # 准备数据
        timestamps = [s.timestamp - self.snapshots[0].timestamp for s in self.snapshots]
        rss_values = [s.rss_mb for s in self.snapshots]
        vms_values = [s.vms_mb for s in self.snapshots]
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # 内存使用趋势
        ax1.plot(timestamps, rss_values, 'b-', label='RSS (常驻内存)')
        ax1.plot(timestamps, vms_values, 'r--', label='VMS (虚拟内存)')
        ax1.set_ylabel('内存 (MB)')
        ax1.set_title('内存使用趋势')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 内存增长率
        if len(timestamps) > 1:
            growth_rates = []
            for i in range(1, len(timestamps)):
                time_diff = timestamps[i] - timestamps[i-1]
                if time_diff > 0:
                    growth_rate = (rss_values[i] - rss_values[i-1]) / time_diff
                    growth_rates.append(growth_rate)
                else:
                    growth_rates.append(0)
            
            ax2.plot(timestamps[1:], growth_rates, 'g-', label='增长率')
            ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            ax2.set_xlabel('时间 (秒)')
            ax2.set_ylabel('增长率 (MB/秒)')
            ax2.set_title('内存增长率')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            print(f"内存使用图表已保存到: {output_path}")
        else:
            plt.show()
    
    def monitor_live(self, duration: int = 60, interval: float = 1.0):
        """实时监控内存"""
        print(f"开始实时监控内存 ({duration}秒)...")
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            snapshot = self.take_snapshot()
            
            # 打印实时信息
            print(f"\r内存: {snapshot.rss_mb:.1f}MB | "
                  f"可用: {snapshot.available_mb:.1f}MB | "
                  f"使用率: {snapshot.percent:.1f}%", end='')
            
            time.sleep(interval)
        
        print("\n监控完成")
        
        # 生成报告
        print(self.generate_report())


class ObjectTracker:
    """对象跟踪器"""
    
    def __init__(self):
        self.tracked_objects: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self.object_counts: Dict[str, int] = defaultdict(int)
    
    def track(self, obj: Any, name: str = None):
        """跟踪对象"""
        obj_id = id(obj)
        obj_name = name or f"{type(obj).__name__}_{obj_id}"
        
        try:
            self.tracked_objects[obj_id] = obj
            self.object_counts[type(obj).__name__] += 1
        except TypeError:
            # 某些对象不能被弱引用
            pass
    
    def get_alive_objects(self) -> Dict[str, int]:
        """获取存活对象统计"""
        alive_counts = defaultdict(int)
        
        for obj_id, obj in self.tracked_objects.items():
            alive_counts[type(obj).__name__] += 1
        
        return dict(alive_counts)
    
    def find_leaked_objects(self) -> List[Any]:
        """查找泄漏的对象"""
        gc.collect()
        
        leaked = []
        for obj_id, obj in self.tracked_objects.items():
            # 检查引用计数
            ref_count = sys.getrefcount(obj)
            
            # 如果引用计数异常高，可能存在泄漏
            if ref_count > 10:  # 阈值可调整
                leaked.append({
                    'object': obj,
                    'type': type(obj).__name__,
                    'ref_count': ref_count,
                    'size': sys.getsizeof(obj)
                })
        
        return leaked


class MemoryLeakDetector:
    """内存泄漏检测器"""
    
    def __init__(self):
        self.profiler = MemoryProfiler()
        self.object_tracker = ObjectTracker()
        
    def run_test(self, test_func: callable, iterations: int = 10):
        """运行泄漏测试"""
        print(f"运行内存泄漏测试 ({iterations} 次迭代)...")
        
        # 开始跟踪
        self.profiler.start_tracking()
        initial_snapshot = self.profiler.take_snapshot()
        
        # 执行测试
        for i in range(iterations):
            print(f"\r迭代 {i+1}/{iterations}", end='')
            
            # 强制垃圾回收
            gc.collect()
            
            # 执行测试函数
            test_func()
            
            # 定期快照
            if i % (iterations // 10) == 0:
                self.profiler.take_snapshot()
        
        print()
        
        # 最终快照
        gc.collect()
        final_snapshot = self.profiler.take_snapshot()
        
        # 分析结果
        memory_growth = final_snapshot.rss_mb - initial_snapshot.rss_mb
        
        print(f"\n内存增长: {memory_growth:.2f}MB")
        
        # 检测泄漏
        leaks = self.profiler.find_memory_leaks(threshold_mb=5.0)
        
        if leaks:
            print("\n检测到潜在内存泄漏:")
            for leak in leaks:
                print(f"- {leak['description']}")
        else:
            print("\n未检测到明显的内存泄漏")
        
        # 生成详细报告
        report = self.profiler.generate_report()
        
        # 停止跟踪
        self.profiler.stop_tracking()
        
        return report


# 便捷函数
def check_memory_usage():
    """快速检查当前内存使用"""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"当前内存使用:")
    print(f"  RSS: {memory_info.rss / 1024 / 1024:.2f}MB")
    print(f"  VMS: {memory_info.vms / 1024 / 1024:.2f}MB")
    
    vm = psutil.virtual_memory()
    print(f"  系统可用: {vm.available / 1024 / 1024:.2f}MB")
    print(f"  使用率: {vm.percent:.1f}%")


# 导出
__all__ = [
    'MemorySnapshot',
    'MemoryProfiler',
    'ObjectTracker',
    'MemoryLeakDetector',
    'check_memory_usage'
]
