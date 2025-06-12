"""
测试Prometheus指标功能
"""

import pytest
from xwe.metrics import PrometheusMetrics, metrics_registry


class TestPrometheusMetrics:
    """Prometheus指标测试"""
    
    def setup_method(self):
        """每个测试前重置指标"""
        self.metrics = PrometheusMetrics()
        
    def test_counter_increment(self):
        """测试计数器增加"""
        self.metrics.register_counter("test_counter", "Test counter")
        self.metrics.inc_counter("test_counter", 1)
        self.metrics.inc_counter("test_counter", 2)
        
        assert "test_counter 3" in self.metrics.export_metrics()
        
    def test_counter_with_labels(self):
        """测试带标签的计数器"""
        self.metrics.register_counter("api_calls", "API calls", labels=["method", "endpoint"])
        
        self.metrics.inc_counter("api_calls", 1, {"method": "GET", "endpoint": "/api/v1/game"})
        self.metrics.inc_counter("api_calls", 2, {"method": "POST", "endpoint": "/api/v1/game"})
        
        export = self.metrics.export_metrics()
        assert 'api_calls{method="GET",endpoint="/api/v1/game"} 1' in export
        assert 'api_calls{method="POST",endpoint="/api/v1/game"} 2' in export
        
    def test_gauge_set(self):
        """测试仪表设置"""
        self.metrics.register_gauge("active_players", "Active players")
        self.metrics.set_gauge("active_players", 10)
        
        assert "active_players 10" in self.metrics.export_metrics()
        
        # 更新值
        self.metrics.set_gauge("active_players", 15)
        assert "active_players 15" in self.metrics.export_metrics()
        
    def test_histogram_observe(self):
        """测试直方图观测"""
        self.metrics.register_histogram("request_duration", "Request duration")
        
        # 添加观测值
        for value in [0.1, 0.2, 0.5, 1.0, 2.0]:
            self.metrics.observe_histogram("request_duration", value)
            
        export = self.metrics.export_metrics()
        
        # 检查基本指标
        assert "request_duration_count" in export
        assert "request_duration_sum" in export
        assert "request_duration_bucket" in export
        
    def test_timer_context_manager(self):
        """测试计时器上下文管理器"""
        import time
        
        self.metrics.register_histogram("test_timer", "Test timer")
        
        with self.metrics.time_histogram("test_timer"):
            time.sleep(0.1)
            
        export = self.metrics.export_metrics()
        assert "test_timer_count" in export
        assert "test_timer_sum" in export
        
    def test_metrics_export_format(self):
        """测试导出格式"""
        self.metrics.register_counter("test_metric", "Test metric description")
        self.metrics.inc_counter("test_metric", 42)
        
        export = self.metrics.export_metrics()
        
        # 检查HELP和TYPE行
        assert "# HELP test_metric Test metric description" in export
        assert "# TYPE test_metric counter" in export
        assert "test_metric 42" in export
        
    def test_global_registry(self):
        """测试全局注册表"""
        # 使用全局注册表
        from xwe.metrics import inc_counter, set_gauge
        
        inc_counter("game_events_total", 1, {"event_type": "login", "player_id": "123"})
        set_gauge("active_players", 5)
        
        export = metrics_registry.export_metrics()
        assert "game_events_total" in export
        assert "active_players 5" in export


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
