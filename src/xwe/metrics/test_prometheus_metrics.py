"""
Prometheus 指标测试
测试指标的正确性和性能
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

from src.xwe.metrics.prometheus_metrics import (
    MetricsCollector,
    nlp_request_seconds,
    nlp_token_count,
    nlp_cache_hit_total,
    context_compression_total,
    async_thread_pool_size,
    get_metrics_collector
)


class TestPrometheusMetrics:
    """Prometheus 指标测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.collector = MetricsCollector()
        self.collector.set_enabled(True)
    
    def test_metrics_collector_initialization(self):
        """测试指标收集器初始化"""
        assert self.collector._enabled is True
        assert self.collector._degraded is False
    
    def test_enable_disable_metrics(self):
        """测试启用/禁用指标收集"""
        self.collector.set_enabled(False)
        assert self.collector._enabled is False
        
        self.collector.set_enabled(True)
        assert self.collector._enabled is True
    
    def test_degraded_mode(self):
        """测试降级模式"""
        self.collector.set_degraded(True)
        assert self.collector._degraded is True
        
        # 在降级模式下，某些指标不应被记录
        self.collector.update_async_metrics(thread_pool_size=10, queue_size=5)
        # 不会抛出异常
    
    def test_measure_time_context_manager(self):
        """测试时间测量上下文管理器"""
        with self.collector.measure_time(nlp_request_seconds, 
                                        {'command_type': 'test', 'status': 'success'}):
            time.sleep(0.1)
        
        # 验证指标被记录
        # 注意：实际测试中需要查询 Prometheus registry
    
    def test_record_nlp_request(self):
        """测试记录 NLP 请求"""
        self.collector.record_nlp_request(
            command_type="explore",
            duration=1.5,
            success=True,
            token_count=100,
            model="deepseek-chat",
            use_cache=False
        )
        
        # 测试失败请求
        self.collector.record_nlp_request(
            command_type="battle",
            duration=0.5,
            success=False,
            error_type="timeout_error"
        )
        
        # 测试缓存命中
        self.collector.record_nlp_request(
            command_type="status",
            duration=0.01,
            success=True,
            use_cache=True
        )
    
    def test_record_context_compression(self):
        """测试记录上下文压缩"""
        self.collector.record_context_compression(
            memory_blocks=10,
            compression_ratio=0.6
        )
        
        self.collector.record_context_compression(
            memory_blocks=5,
            compression_ratio=0.8
        )
    
    def test_update_async_metrics(self):
        """测试更新异步处理指标"""
        self.collector.update_async_metrics(
            thread_pool_size=5,
            queue_size=10
        )
        
        self.collector.update_async_metrics(
            thread_pool_size=10,
            queue_size=50
        )
    
    def test_record_command_execution(self):
        """测试记录命令执行时间"""
        self.collector.record_command_execution(
            command="explore",
            handler="exploration_handler",
            duration=2.5
        )
    
    def test_record_api_call(self):
        """测试记录 API 调用"""
        self.collector.record_api_call(
            api_name="deepseek",
            endpoint="https://api.deepseek.com/v1/chat/completions",
            duration=3.2
        )
    
    def test_update_game_metrics(self):
        """测试更新游戏状态指标"""
        self.collector.update_game_metrics(
            instances=5,
            players=3
        )
    
    def test_update_system_metrics(self):
        """测试更新系统资源指标"""
        self.collector.update_system_metrics(
            cpu_percent=45.5,
            memory_mb=1024.0
        )
    
    def test_disabled_metrics_collection(self):
        """测试禁用状态下的指标收集"""
        self.collector.set_enabled(False)
        
        # 所有记录操作都应该静默跳过
        self.collector.record_nlp_request(
            command_type="test",
            duration=1.0,
            success=True
        )
        self.collector.update_game_metrics(instances=1, players=1)
        # 不应该抛出异常
    
    def test_concurrent_metrics_update(self):
        """测试并发更新指标"""
        def update_metrics(i):
            self.collector.record_nlp_request(
                command_type=f"command_{i}",
                duration=0.1 * i,
                success=i % 2 == 0,
                token_count=10 * i
            )
            self.collector.update_async_metrics(
                thread_pool_size=i,
                queue_size=i * 2
            )
        
        # 使用线程池并发更新
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(100):
                future = executor.submit(update_metrics, i)
                futures.append(future)
            
            # 等待所有任务完成
            for future in futures:
                future.result()
    
    def test_error_handling(self):
        """测试错误处理"""
        # 模拟指标记录失败
        with patch('prometheus_client.Histogram.labels') as mock_labels:
            mock_labels.side_effect = Exception("Metric error")
            
            # 应该捕获异常而不是崩溃
            self.collector.record_nlp_request(
                command_type="test",
                duration=1.0,
                success=True
            )
    
    def test_global_metrics_collector(self):
        """测试全局指标收集器"""
        collector = get_metrics_collector()
        assert isinstance(collector, MetricsCollector)
        
        # 确保是单例
        collector2 = get_metrics_collector()
        assert collector is collector2


class TestMetricsIntegration:
    """指标集成测试"""
    
    @pytest.mark.integration
    def test_nlp_monitor_integration(self):
        """测试与 NLP Monitor 的集成"""
        from src.xwe.core.nlp.monitor import NLPMonitor
        
        monitor = NLPMonitor()
        
        # 记录一些请求
        monitor.record_request(
            command="探索周围",
            handler="explore_handler",
            duration=1.2,
            success=True,
            confidence=0.9,
            use_cache=False,
            token_count=50
        )
        
        # 验证统计数据
        stats = monitor.get_stats()
        assert stats['total_requests'] == 1
        assert stats['total_success'] == 1
    
    @pytest.mark.integration
    def test_llm_client_integration(self):
        """测试与 LLM Client 的集成"""
        from src.xwe.core.nlp.llm_client import LLMClient
        
        # 使用 mock 模式
        with patch.dict('os.environ', {'USE_MOCK_LLM': 'true'}):
            client = LLMClient()
            
            # 发送请求
            response = client.chat("测试消息")
            assert response is not None


class TestPerformance:
    """性能测试"""
    
    def test_metrics_overhead(self):
        """测试指标收集的性能开销"""
        collector = MetricsCollector()
        collector.set_enabled(True)
        
        # 测试单次记录的时间
        start = time.time()
        for _ in range(1000):
            collector.record_nlp_request(
                command_type="test",
                duration=0.1,
                success=True,
                token_count=10
            )
        elapsed = time.time() - start
        
        # 1000次记录应该在100ms内完成
        assert elapsed < 0.1, f"指标记录太慢: {elapsed}秒"
    
    def test_high_qps_support(self):
        """测试高 QPS 支持"""
        collector = MetricsCollector()
        collector.set_enabled(True)
        
        # 模拟 1000 QPS
        def simulate_request():
            collector.record_nlp_request(
                command_type="test",
                duration=0.01,
                success=True
            )
        
        threads = []
        start = time.time()
        
        # 创建 100 个线程，每个发送 10 个请求
        for _ in range(100):
            thread = threading.Thread(target=lambda: [simulate_request() for _ in range(10)])
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start
        qps = 1000 / elapsed
        
        # 应该能支持 1000+ QPS
        assert qps > 1000, f"QPS 太低: {qps}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
