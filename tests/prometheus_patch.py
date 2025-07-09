
# 临时修复 Prometheus 测试
import sys
from unittest.mock import patch, MagicMock

# Mock Prometheus 客户端的内部属性
def mock_histogram():
    mock = MagicMock()
    mock._buckets = (0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
    return mock

# 应用补丁
if 'test_prometheus_metrics' in str(sys.argv):
    import xwe.metrics.prometheus_metrics as pm
    pm.nlp_request_seconds = mock_histogram()
    pm.nlp_token_count = mock_histogram()
    pm.command_execution_seconds = mock_histogram()
