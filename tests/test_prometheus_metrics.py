"""
Prometheus 指标集成测试
使用 pytest 验证监控功能
"""

import pytest
import time
import requests
from prometheus_client.parser import text_string_to_metric_families

# 测试配置
TEST_APP_URL = "http://localhost:5000"
METRICS_ENDPOINT = f"{TEST_APP_URL}/metrics"


class TestPrometheusIntegration:
    """Prometheus 集成测试套件"""
    
    def test_metrics_endpoint_available(self):
        """测试 /metrics 端点是否可访问"""
        response = requests.get(METRICS_ENDPOINT)
        assert response.status_code == 200
        assert response.headers.get('Content-Type', '').startswith('text/plain')
    
    def test_basic_metrics_exposed(self):
        """测试基础指标是否暴露"""
        response = requests.get(METRICS_ENDPOINT)
        metrics_text = response.text
        
        # 解析指标
        metrics = {}
        for family in text_string_to_metric_families(metrics_text):
            metrics[family.name] = family
        
        # 验证核心指标存在
        expected_metrics = [
            'xwe_nlp_request_seconds',
            'xwe_nlp_token_count',
            'xwe_nlp_error_total',
            'xwe_nlp_cache_hit_total'
        ]
        
        for metric_name in expected_metrics:
            assert metric_name in metrics, f"指标 {metric_name} 未找到"
    
    def test_nlp_request_metrics(self):
        """测试 NLP 请求指标记录"""
        # 获取初始指标
        initial_metrics = self._get_metrics()
        
        # 发送测试请求
        test_commands = [
            {"command": "探索周围"},
            {"command": "开始修炼"},
            {"command": "查看状态"}
        ]
        
        for cmd in test_commands:
            response = requests.post(
                f"{TEST_APP_URL}/api/game/command",
                json=cmd
            )
            assert response.status_code == 200
        
        # 等待指标更新
        time.sleep(1)
        
        # 获取更新后的指标
        updated_metrics = self._get_metrics()
        
        # 验证请求计数增加
        initial_count = self._get_metric_value(
            initial_metrics, 
            'xwe_nlp_request_seconds_count'
        )
        updated_count = self._get_metric_value(
            updated_metrics,
            'xwe_nlp_request_seconds_count'
        )
        
        assert updated_count > initial_count, "请求计数未增加"
    
    def test_no_player_privacy_exposed(self):
        """测试确保没有玩家隐私信息暴露"""
        response = requests.get(METRICS_ENDPOINT)
        metrics_text = response.text.lower()
        
        # 确保没有敏感信息
        sensitive_patterns = [
            'player_name',
            'user_id',
            'email',
            'password',
            'session_id',
            'ip_address'
        ]
        
        for pattern in sensitive_patterns:
            assert pattern not in metrics_text, f"发现敏感信息: {pattern}"
    
    def _get_metrics(self):
        """获取并解析当前指标"""
        response = requests.get(METRICS_ENDPOINT)
        metrics = {}
        
        for family in text_string_to_metric_families(response.text):
            for sample in family.samples:
                metrics[sample.name] = sample.value
        
        return metrics
    
    def _get_metric_value(self, metrics, metric_name):
        """获取特定指标的值"""
        return metrics.get(metric_name, 0)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
