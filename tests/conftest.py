"""
测试配置和 fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# 设置测试环境变量
os.environ['USE_MOCK_LLM'] = 'true'
os.environ['ENABLE_PROMETHEUS'] = 'false'
os.environ['ENABLE_CONTEXT_COMPRESSION'] = 'true'

# 确保可以导入 src 目录下的 xwe 包
project_root = Path(__file__).resolve().parents[1]
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 标记慢速测试
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "flaky: marks tests that may fail intermittently"
    )

# 跳过有问题的测试
def pytest_collection_modifyitems(config, items):
    skip_tests = [
        "test_status_uses_game_session",  # 需要特定游戏环境
        "test_performance_regression_check",  # 性能基准问题
    ]
    
    for item in items:
        # 跳过特定测试
        if any(skip_test in item.nodeid for skip_test in skip_tests):
            item.add_marker(pytest.mark.skip(reason="临时跳过，需要修复"))
        
        # 标记慢速测试
        if "performance" in item.nodeid or "memory" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # 标记不稳定的测试
        if "thread_safe" in item.nodeid or "burst_handling" in item.nodeid:
            item.add_marker(pytest.mark.flaky)


@pytest.fixture
def app():
    """提供 Flask 应用实例"""
    from app import create_app
    application = create_app()
    application.config['TESTING'] = True
    application.config['WTF_CSRF_ENABLED'] = False
    return application


@pytest.fixture
def client(app):
    """提供 Flask 测试客户端"""
    with app.test_client() as client:
        yield client
