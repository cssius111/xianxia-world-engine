"""
压力测试套件
测试系统在高负载下的表现
"""

import pytest
import time
import os
import sys
import random
import threading
import multiprocessing
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import json

# 添加项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# 配置测试环境
os.environ['DEEPSEEK_API_KEY'] = 'test'
os.environ['ENABLE_PROMETHEUS'] = 'true'


class StressTestMetrics:
    """压力测试指标收集器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.response_times = []
        self.errors = []
        self._lock = threading.Lock()
    
    def record_request(self, duration: float, success: bool, error: str = None):
        """记录请求"""
        with self._lock:
            self.request_count += 1
            self.response_times.append(duration)
            
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
                if error:
                    self.errors.append(error)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            elapsed_time = time.time() - self.start_time
            
            if not self.response_times:
                return {
                    'elapsed_time': elapsed_time,
                    'request_count': 0,
                    'rps': 0,
                    'success_rate': 0
                }
            
            sorted_times = sorted(self.response_times)
            
            return {
                'elapsed_time': elapsed_time,
                'request_count': self.request_count,
                'success_count': self.success_count,
                'error_count': self.error_count,
                'rps': self.request_count / elapsed_time if elapsed_time > 0 else 0,
                'success_rate': self.success_count / self.request_count if self.request_count > 0 else 0,
                'avg_response_time': sum(self.response_times) / len(self.response_times),
                'p50_response_time': sorted_times[int(len(sorted_times) * 0.5)],
                'p90_response_time': sorted_times[int(len(sorted_times) * 0.9)],
                'p99_response_time': sorted_times[int(len(sorted_times) * 0.99)],
                'error_types': self._count_error_types()
            }
    
    def _count_error_types(self) -> Dict[str, int]:
        """统计错误类型"""
        error_types = {}
        for error in self.errors:
            error_type = error.split(':')[0] if ':' in error else 'unknown'
            error_types[error_type] = error_types.get(error_type, 0) + 1
        return error_types


@pytest.mark.slow
class TestNLPStress:
    """NLP 压力测试"""
    
    def test_sustained_high_load(self):
        """持续高负载测试（1小时+）"""
        print("\n开始持续高负载测试...")
        
        from xwe.core.nlp.nlp_processor import NLPProcessor
        
        # 测试参数
        test_duration = 60  # 测试时长（秒），实际应该是3600秒
        target_rps = 50  # 目标每秒请求数
        
        # 创建处理器池
        processor_pool = [NLPProcessor() for _ in range(10)]
        
        # 指标收集器
        metrics = StressTestMetrics()
        
        # 测试命令池
        command_pool = [
            "探索周围环境",
            "攻击目标",
            "使用技能",
            "查看状态",
            "打开背包",
            "与NPC对话",
            "购买物品",
            "修炼功法",
            "查看地图",
            "完成任务"
        ]
        
        def worker():
            """工作线程"""
            while time.time() - metrics.start_time < test_duration:
                try:
                    # 随机选择处理器和命令
                    processor = random.choice(processor_pool)
                    command = random.choice(command_pool)
                    
                    # 处理请求
                    start_time = time.time()
                    result = processor.process(command)
                    duration = time.time() - start_time
                    
                    # 记录结果
                    metrics.record_request(duration, True)
                    
                    # 控制请求速率
                    sleep_time = 1.0 / target_rps - duration
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                except Exception as e:
                    metrics.record_request(0, False, str(e))
        
        # 启动工作线程
        threads = []
        thread_count = min(target_rps, 50)  # 限制最大线程数
        
        for _ in range(thread_count):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        
        # 监控进度
        last_report_time = time.time()
        while any(t.is_alive() for t in threads):
            current_time = time.time()
            if current_time - last_report_time >= 10:  # 每10秒报告一次
                stats = metrics.get_stats()
                print(f"\n压力测试进度 ({stats['elapsed_time']:.0f}秒):")
                print(f"  总请求数: {stats['request_count']}")
                print(f"  RPS: {stats['rps']:.2f}")
                print(f"  成功率: {stats['success_rate'] * 100:.2f}%")
                print(f"  平均响应时间: {stats['avg_response_time'] * 1000:.2f}ms")
                print(f"  P99响应时间: {stats['p99_response_time'] * 1000:.2f}ms")
                
                last_report_time = current_time
            
            time.sleep(1)
        
        # 等待所有线程结束
        for t in threads:
            t.join()
        
        # 最终报告
        final_stats = metrics.get_stats()
        print("\n" + "=" * 60)
        print("持续高负载测试完成:")
        print(f"  测试时长: {final_stats['elapsed_time']:.2f}秒")
        print(f"  总请求数: {final_stats['request_count']}")
        print(f"  平均RPS: {final_stats['rps']:.2f}")
        print(f"  成功率: {final_stats['success_rate'] * 100:.2f}%")
        print(f"  错误数: {final_stats['error_count']}")
        print(f"  平均响应时间: {final_stats['avg_response_time'] * 1000:.2f}ms")
        print(f"  P90响应时间: {final_stats['p90_response_time'] * 1000:.2f}ms")
        print(f"  P99响应时间: {final_stats['p99_response_time'] * 1000:.2f}ms")
        
        # 验证结果
        assert final_stats['success_rate'] > 0.95  # 成功率大于95%
        assert final_stats['avg_response_time'] < 1.0  # 平均响应时间小于1秒
        assert final_stats['p99_response_time'] < 5.0  # P99响应时间小于5秒
    
    def test_burst_traffic(self):
        """突发流量测试"""
        print("\n开始突发流量测试...")
        
        from xwe.core.nlp.nlp_processor import NLPProcessor
        
        # 创建处理器
        processor = NLPProcessor()
        
        # 测试阶段
        test_phases = [
            {'name': '正常流量', 'duration': 30, 'rps': 10},
            {'name': '突发高峰', 'duration': 10, 'rps': 100},
            {'name': '恢复正常', 'duration': 30, 'rps': 10},
            {'name': '极限突发', 'duration': 5, 'rps': 200},
            {'name': '逐步恢复', 'duration': 20, 'rps': 50},
        ]
        
        # 总体指标
        overall_metrics = StressTestMetrics()
        
        for phase in test_phases:
            print(f"\n阶段: {phase['name']} (RPS: {phase['rps']}, 时长: {phase['duration']}秒)")
            
            phase_start = time.time()
            phase_metrics = StressTestMetrics()
            
            def phase_worker():
                """阶段工作线程"""
                while time.time() - phase_start < phase['duration']:
                    try:
                        command = f"突发测试命令_{random.randint(1, 100)}"
                        
                        start_time = time.time()
                        result = processor.process(command)
                        duration = time.time() - start_time
                        
                        phase_metrics.record_request(duration, True)
                        overall_metrics.record_request(duration, True)
                        
                        # 控制速率
                        sleep_time = 1.0 / phase['rps'] - duration
                        if sleep_time > 0:
                            time.sleep(sleep_time)
                    
                    except Exception as e:
                        phase_metrics.record_request(0, False, str(e))
                        overall_metrics.record_request(0, False, str(e))
            
            # 启动线程
            threads = []
            thread_count = min(phase['rps'] // 10, 20)  # 每个线程处理10 RPS
            
            for _ in range(thread_count):
                t = threading.Thread(target=phase_worker)
                t.start()
                threads.append(t)
            
            # 等待阶段结束
            for t in threads:
                t.join()
            
            # 阶段统计
            phase_stats = phase_metrics.get_stats()
            print(f"  实际RPS: {phase_stats['rps']:.2f}")
            print(f"  成功率: {phase_stats['success_rate'] * 100:.2f}%")
            print(f"  平均响应: {phase_stats['avg_response_time'] * 1000:.2f}ms")
        
        # 总体统计
        overall_stats = overall_metrics.get_stats()
        print("\n" + "=" * 60)
        print("突发流量测试完成:")
        print(f"  总请求数: {overall_stats['request_count']}")
        print(f"  总体成功率: {overall_stats['success_rate'] * 100:.2f}%")
        print(f"  平均响应时间: {overall_stats['avg_response_time'] * 1000:.2f}ms")
        
        # 验证系统能够处理突发流量
        assert overall_stats['success_rate'] > 0.90  # 即使在突发情况下，成功率也应该大于90%
    
    def test_resource_exhaustion(self):
        """资源耗尽测试"""
        print("\n开始资源耗尽测试...")
        
        from xwe.core.nlp.nlp_processor import NLPProcessor
        
        # 监控初始资源
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_threads = process.num_threads()
        
        print(f"初始内存: {initial_memory:.2f}MB")
        print(f"初始线程数: {initial_threads}")
        
        # 1. 内存耗尽测试
        print("\n1. 内存压力测试...")
        processors = []
        large_contexts = []
        
        try:
            # 创建大量处理器实例
            for i in range(100):
                processor = NLPProcessor()
                processors.append(processor)
                
                # 创建大上下文
                large_context = [
                    {"content": "x" * 10000} for _ in range(100)
                ]
                large_contexts.append(large_context)
                
                # 执行处理
                processor.process("内存测试", large_context)
                
                if i % 10 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_growth = current_memory - initial_memory
                    print(f"  已创建 {i+1} 个实例，内存增长: {memory_growth:.2f}MB")
                    
                    # 如果内存增长过大，停止测试
                    if memory_growth > 1000:  # 1GB
                        print("  内存增长过大，停止测试")
                        break
        
        except MemoryError:
            print("  触发内存错误（预期行为）")
        
        # 清理
        processors.clear()
        large_contexts.clear()
        import gc
        gc.collect()
        
        # 2. 线程耗尽测试
        print("\n2. 线程耗尽测试...")
        threads = []
        max_threads_reached = False
        
        def thread_worker():
            time.sleep(10)  # 保持线程存活
        
        try:
            for i in range(500):
                t = threading.Thread(target=thread_worker)
                t.start()
                threads.append(t)
                
                if i % 50 == 0:
                    current_threads = process.num_threads()
                    print(f"  已创建 {i+1} 个线程，当前线程数: {current_threads}")
                    
                    # 检查是否达到系统限制
                    if current_threads > 200:
                        print("  接近线程限制，停止测试")
                        max_threads_reached = True
                        break
        
        except Exception as e:
            print(f"  线程创建失败: {e}")
            max_threads_reached = True
        
        # 清理线程
        for t in threads:
            if t.is_alive():
                t.join(timeout=0.1)
        
        # 3. CPU 耗尽测试
        print("\n3. CPU 压力测试...")
        
        def cpu_intensive_task():
            """CPU 密集型任务"""
            start_time = time.time()
            while time.time() - start_time < 5:
                # 执行计算密集操作
                _ = sum(i * i for i in range(10000))
        
        # 启动 CPU 密集型任务
        cpu_threads = []
        cpu_count = psutil.cpu_count()
        
        for i in range(cpu_count * 2):  # 创建2倍CPU核心数的线程
            t = threading.Thread(target=cpu_intensive_task)
            t.start()
            cpu_threads.append(t)
        
        # 监控 CPU 使用
        for i in range(5):
            time.sleep(1)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            print(f"  CPU 使用率: {cpu_percent}%")
        
        # 等待任务完成
        for t in cpu_threads:
            t.join()
        
        # 最终资源状态
        final_memory = process.memory_info().rss / 1024 / 1024
        final_threads = process.num_threads()
        
        print("\n" + "=" * 60)
        print("资源耗尽测试完成:")
        print(f"  内存变化: {initial_memory:.2f}MB -> {final_memory:.2f}MB")
        print(f"  线程变化: {initial_threads} -> {final_threads}")
        print(f"  最大线程测试: {'通过' if max_threads_reached else '未达到限制'}")
    
    def test_graceful_degradation(self):
        """优雅降级验证"""
        print("\n开始优雅降级测试...")
        
        from xwe.core.nlp.nlp_processor import NLPProcessor
        from xwe.metrics.prometheus_metrics import get_metrics_collector
        
        # 获取指标收集器
        metrics_collector = get_metrics_collector()
        
        # 创建处理器
        processor = NLPProcessor()
        
        # 测试场景
        test_scenarios = [
            {
                'name': '正常模式',
                'load': 10,
                'enable_degradation': False
            },
            {
                'name': '高负载触发降级',
                'load': 100,
                'enable_degradation': True
            },
            {
                'name': '极限负载降级',
                'load': 200,
                'enable_degradation': True
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n场景: {scenario['name']}")
            
            # 设置降级模式
            if scenario['enable_degradation']:
                metrics_collector.set_degraded(True)
                print("  降级模式: 已启用")
            else:
                metrics_collector.set_degraded(False)
                print("  降级模式: 未启用")
            
            # 执行负载测试
            start_time = time.time()
            success_count = 0
            error_count = 0
            
            for i in range(scenario['load']):
                try:
                    result = processor.process(f"降级测试_{i}")
                    if result:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception:
                    error_count += 1
            
            duration = time.time() - start_time
            success_rate = success_count / scenario['load'] if scenario['load'] > 0 else 0
            
            print(f"  处理请求: {scenario['load']}")
            print(f"  成功率: {success_rate * 100:.2f}%")
            print(f"  总耗时: {duration:.2f}秒")
            print(f"  平均处理时间: {duration / scenario['load'] * 1000:.2f}ms")
            
            # 验证降级效果
            if scenario['enable_degradation']:
                # 降级模式下应该保持较高成功率
                assert success_rate > 0.8, f"降级模式下成功率过低: {success_rate}"


class StressTestRunner:
    """压力测试运行器"""
    
    @staticmethod
    def run_stress_tests():
        """运行所有压力测试"""
        print("开始运行NLP压力测试套件...")
        print("=" * 60)
        
        # 设置测试环境
        os.environ['STRESS_TEST_MODE'] = 'true'
        
        # 运行测试
        pytest.main([
            __file__,
            "-v",
            "--tb=short",
            "-s"  # 显示print输出
        ])


if __name__ == "__main__":
    StressTestRunner.run_stress_tests()
