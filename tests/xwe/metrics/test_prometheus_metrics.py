"""
单元测试 - Prometheus 指标
测试 Prometheus 监控集成
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor

# 如果缺少 prometheus_client，则跳过本模块的测试
pytest.importorskip('prometheus_client')

from xwe.metrics.prometheus_metrics import (
    MetricsCollector,
    get_metrics_collector,
    init_prometheus_app_metrics,
    nlp_request_seconds,
    nlp_token_count,
    nlp_cache_hit_total,
    context_compression_total,
    context_memory_blocks_gauge,
    async_thread_pool_size,
    async_request_queue_size,
    nlp_error_total,
    command_execution_seconds,
    api_call_latency,
    game_instances_gauge,
    players_online_gauge,
    system_cpu_usage,
    system_memory_usage
)


class TestMetricsCollector:
    """指标收集器测试"""
    
    @pytest.fixture
    def collector(self):
        """创建指标收集器"""
        collector = MetricsCollector()
        collector.set_enabled(True)
        return collector
    
    def test_initialization(self):
        """测试初始化"""
        collector = MetricsCollector()
        assert collector._enabled is True
        assert collector._degraded is False
        assert hasattr(collector, '_lock')
    
    def test_enable_disable(self, collector):
        """测试启用/禁用"""
        # 禁用
        collector.set_enabled(False)
        assert collector._enabled is False
        
        # 记录指标（应该被忽略）
        collector.record_nlp_request(
            command_type="test",
            duration=1.0,
            success=True
        )
        
        # 重新启用
        collector.set_enabled(True)
        assert collector._enabled is True
    
    def test_degraded_mode(self, collector):
        """测试降级模式"""
        collector.set_degraded(True)
        assert collector._degraded is True
        
        # 某些指标在降级模式下不应被记录
        collector.update_system_metrics(cpu_percent=50.0, memory_mb=1000.0)
        # 不应该抛出异常
    
    def test_record_nlp_request(self, collector):
        """测试记录 NLP 请求"""
        # 成功请求
        collector.record_nlp_request(
            command_type="explore",
            duration=0.5,
            success=True,
            token_count=100,
            model="deepseek-chat",
            use_cache=False
        )
        
        # 失败请求
        collector.record_nlp_request(
            command_type="battle",
            duration=0.1,
            success=False,
            error_type="timeout_error"
        )
        
        # 缓存命中
        collector.record_nlp_request(
            command_type="status",
            duration=0.01,
            success=True,
            use_cache=True
        )
    
    def test_record_context_compression(self, collector):
        """测试记录上下文压缩"""
        collector.record_context_compression(
            memory_blocks=10,
            compression_ratio=0.6
        )
        
        # 多次调用
        for i in range(5):
            collector.record_context_compression(
                memory_blocks=i * 2,
                compression_ratio=0.5 + i * 0.1
            )
    
    def test_update_async_metrics(self, collector):
        """测试更新异步指标"""
        collector.update_async_metrics(
            thread_pool_size=5,
            queue_size=10
        )
        
        # 降级模式下也应该跳过
        collector.set_degraded(True)
        collector.update_async_metrics(
            thread_pool_size=10,
            queue_size=20
        )
    
    def test_record_command_execution(self, collector):
        """测试记录命令执行"""
        commands = ["explore", "battle", "trade", "talk"]
        handlers = ["explore_handler", "combat_handler", "trade_handler", "dialog_handler"]
        
        for cmd, handler in zip(commands, handlers):
            collector.record_command_execution(
                command=cmd,
                handler=handler,
                duration=0.1 * (commands.index(cmd) + 1)
            )
    
    def test_record_api_call(self, collector):
        """测试记录 API 调用"""
        collector.record_api_call(
            api_name="deepseek",
            endpoint="https://api.deepseek.com/v1/chat/completions",
            duration=0.5
        )
        
        # 多个 API 调用
        apis = [
            ("deepseek", "/v1/chat/completions", 0.5),
            ("deepseek", "/v1/embeddings", 0.3),
            ("internal", "/api/save", 0.1),
        ]
        
        for api_name, endpoint, duration in apis:
            collector.record_api_call(
                api_name=api_name,
                endpoint=endpoint,
                duration=duration
            )
    
    def test_update_game_metrics(self, collector):
        """测试更新游戏指标"""
        collector.update_game_metrics(
            instances=5,
            players=3
        )
        
        # 更新多次
        for i in range(10):
            collector.update_game_metrics(
                instances=i,
                players=i * 2
            )
    
    def test_update_system_metrics(self, collector):
        """测试更新系统指标"""
        collector.update_system_metrics(
            cpu_percent=45.5,
            memory_mb=1024.0
        )
        
        # 测试极值
        collector.update_system_metrics(
            cpu_percent=0.0,
            memory_mb=0.0
        )
        
        collector.update_system_metrics(
            cpu_percent=100.0,
            memory_mb=8192.0
        )
    
    def test_measure_time_context_manager(self, collector):
        """测试时间测量上下文管理器"""
        # 启用状态
        with collector.measure_time(
            histogram=MagicMock(),
            labels={'command_type': 'test', 'status': 'success'}
        ):
            time.sleep(0.1)
        
        # 禁用状态
        collector.set_enabled(False)
        with collector.measure_time(
            histogram=MagicMock(),
            labels={'command_type': 'test', 'status': 'success'}
        ):
            time.sleep(0.1)  # 不应该记录
    
    def test_thread_safety(self, collector):
        """测试线程安全"""
        errors = []
        
        def record_metrics(thread_id):
            try:
                for i in range(100):
                    collector.record_nlp_request(
                        command_type=f"cmd_{thread_id}",
                        duration=0.01 * i,
                        success=i % 2 == 0,
                        token_count=i * 10
                    )
                    
                    if i % 10 == 0:
                        collector.update_game_metrics(
                            instances=thread_id,
                            players=thread_id * 2
                        )
            except Exception as e:
                errors.append(str(e))
        
        # 创建多个线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=record_metrics, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待完成
        for thread in threads:
            thread.join()
        
        # 验证没有错误
        assert len(errors) == 0
    
    def test_error_handling(self, collector):
        """测试错误处理"""
        # 模拟指标记录失败
        with patch('prometheus_client.Histogram.labels') as mock_labels:
            mock_labels.side_effect = Exception("Metric error")
            
            # 应该捕获异常而不崩溃
            collector.record_nlp_request(
                command_type="test",
                duration=1.0,
                success=True
            )
    
    def test_metric_labels(self, collector):
        """测试指标标签"""
        # 测试不同的标签组合
        label_combinations = [
            {"command_type": "explore", "status": "success"},
            {"command_type": "explore", "status": "failure"},
            {"command_type": "battle", "status": "success"},
            {"command_type": "battle", "status": "failure"},
        ]
        
        for labels in label_combinations:
            with collector.measure_time(
                histogram=MagicMock(),
                labels=labels
            ):
                pass


class TestPrometheusIntegration:
    """Prometheus 集成测试"""
    
    def test_flask_app_integration(self):
        """测试 Flask 应用集成"""
        from flask import Flask
        
        app = Flask(__name__)
        
        # 初始化 Prometheus 指标
        metrics = init_prometheus_app_metrics(
            app,
            app_version='1.0.0',
            app_config={
                'metrics_path': '/metrics',
                'enable_default_metrics': True
            }
        )
        
        assert metrics is not None
        
        # 添加测试路由
        @app.route('/test')
        def test_route():
            return 'OK'
        
        # 测试客户端
        with app.test_client() as client:
            # 访问测试路由
            response = client.get('/test')
            assert response.status_code == 200
            
            # 访问指标端点
            response = client.get('/metrics')
            assert response.status_code == 200
            
            # 验证指标内容
            metrics_data = response.data.decode('utf-8')
            assert 'xwe_' in metrics_data  # 自定义指标前缀
    
    def test_global_metrics_collector(self):
        """测试全局指标收集器"""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        
        # 应该是同一个实例（单例）
        assert collector1 is collector2
    
    def test_metric_values(self):
        """测试指标值"""
        collector = get_metrics_collector()
        collector.set_enabled(True)
        
        # 记录一些指标
        for i in range(10):
            collector.record_nlp_request(
                command_type="test",
                duration=0.1 * (i + 1),
                success=i % 2 == 0,
                token_count=100 * (i + 1)
            )
        
        # 这里可以通过 Prometheus 客户端验证指标值
        # 但需要访问内部注册表，这里简化测试


class TestMetricTypes:
    """测试不同类型的指标"""
    
    def test_histogram_metrics(self):
        """测试直方图指标"""
        # 验证直方图指标已定义
        assert nlp_request_seconds is not None
        assert nlp_token_count is not None
        assert command_execution_seconds is not None
        
        # 验证 buckets 设置
        assert hasattr(nlp_request_seconds, '_buckets')
    
    def test_counter_metrics(self):
        """测试计数器指标"""
        # 验证计数器指标已定义
        assert nlp_cache_hit_total is not None
        assert context_compression_total is not None
        assert nlp_error_total is not None
    
    def test_gauge_metrics(self):
        """测试仪表指标"""
        # 验证仪表指标已定义
        assert context_memory_blocks_gauge is not None
        assert async_thread_pool_size is not None
        assert async_request_queue_size is not None
        assert game_instances_gauge is not None
        assert players_online_gauge is not None
        assert system_cpu_usage is not None
        assert system_memory_usage is not None
    
    def test_summary_metrics(self):
        """测试摘要指标"""
        # 验证摘要指标已定义
        assert api_call_latency is not None


class TestPerformanceImpact:
    """测试性能影响"""
    
    def test_metrics_overhead(self):
        """测试指标收集的开销"""
        collector = get_metrics_collector()
        collector.set_enabled(True)
        
        # 测试启用指标时的性能
        enabled_start = time.time()
        for i in range(1000):
            collector.record_nlp_request(
                command_type="test",
                duration=0.001,
                success=True
            )
        enabled_time = time.time() - enabled_start
        
        # 测试禁用指标时的性能
        collector.set_enabled(False)
        disabled_start = time.time()
        for i in range(1000):
            collector.record_nlp_request(
                command_type="test",
                duration=0.001,
                success=True
            )
        disabled_time = time.time() - disabled_start
        
        print(f"启用指标: {enabled_time:.3f}s")
        print(f"禁用指标: {disabled_time:.3f}s")
        print(f"开销: {(enabled_time - disabled_time) / enabled_time * 100:.1f}%")
        
        # 开销应该小于 10%
        overhead = (enabled_time - disabled_time) / enabled_time
        assert overhead < 0.1
    
    def test_high_cardinality_labels(self):
        """测试高基数标签"""
        collector = get_metrics_collector()
        
        # 测试大量不同的标签值
        for i in range(100):
            collector.record_nlp_request(
                command_type=f"cmd_{i % 20}",  # 限制为20种命令类型
                duration=0.01,
                success=i % 2 == 0,
                model=f"model_{i % 5}"  # 限制为5种模型
            )
        
        # 不应该造成内存问题
        # 实际生产中应该避免高基数标签


class TestDegradationScenarios:
    """测试降级场景"""
    
    def test_graceful_degradation(self):
        """测试优雅降级"""
        collector = get_metrics_collector()
        
        # 正常模式
        collector.set_degraded(False)
        collector.update_system_metrics(cpu_percent=50.0, memory_mb=1000.0)
        
        # 降级模式
        collector.set_degraded(True)
        
        # 关键指标仍应记录
        collector.record_nlp_request(
            command_type="critical",
            duration=1.0,
            success=False,
            error_type="critical_error"
        )
        
        # 非关键指标应被跳过
        collector.update_system_metrics(cpu_percent=60.0, memory_mb=1100.0)
    
    def test_fallback_mechanism(self):
        """测试回退机制"""
        collector = MetricsCollector()
        
        # 模拟 Prometheus 客户端不可用
        with patch('prometheus_client.Counter.labels', side_effect=ImportError):
            # 应该优雅处理，不崩溃
            collector.record_nlp_request(
                command_type="test",
                duration=1.0,
                success=True
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
