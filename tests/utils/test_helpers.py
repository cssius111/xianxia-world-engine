"""
测试辅助函数
提供常用的测试工具函数
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from contextlib import contextmanager
import asyncio
from functools import wraps
import psutil
import traceback


def setup_test_environment():
    """设置测试环境"""
    # 确保使用测试配置
    os.environ['TESTING'] = 'true'
    os.environ['USE_MOCK_LLM'] = 'true'
    os.environ['ENABLE_PROMETHEUS'] = 'true'
    os.environ['LOG_LEVEL'] = 'WARNING'  # 减少测试输出
    
    # 添加项目路径
    project_root = Path(__file__).resolve().parents[2]
    src_path = project_root / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    return project_root


@contextmanager
def temporary_env_var(key: str, value: str):
    """临时设置环境变量"""
    original = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if original is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original


@contextmanager
def temporary_directory():
    """创建临时目录"""
    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@contextmanager
def measure_time(name: str = "Operation"):
    """测量执行时间"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        print(f"{name} took {duration:.3f} seconds")


@contextmanager
def monitor_resources():
    """监控资源使用"""
    process = psutil.Process()
    
    # 开始监控
    start_cpu = process.cpu_percent()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    start_threads = process.num_threads()
    
    yield
    
    # 结束监控
    end_cpu = process.cpu_percent()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB
    end_threads = process.num_threads()
    
    print(f"\n资源使用统计:")
    print(f"  CPU: {start_cpu:.1f}% -> {end_cpu:.1f}%")
    print(f"  内存: {start_memory:.1f}MB -> {end_memory:.1f}MB (增长: {end_memory - start_memory:.1f}MB)")
    print(f"  线程: {start_threads} -> {end_threads}")


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """失败重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: {e}")
                        time.sleep(delay)
                    else:
                        raise
            
            raise last_exception
        
        return wrapper
    return decorator


def async_test_wrapper(timeout: float = 30.0):
    """异步测试包装器"""
    def decorator(async_func):
        @wraps(async_func)
        def wrapper(*args, **kwargs):
            async def run():
                try:
                    return await asyncio.wait_for(
                        async_func(*args, **kwargs),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Test timed out after {timeout} seconds")
            
            return asyncio.run(run())
        
        return wrapper
    return decorator


def create_mock_response(status_code: int = 200, json_data: Optional[Dict] = None):
    """创建模拟 HTTP 响应"""
    class MockResponse:
        def __init__(self, status_code: int, json_data: Optional[Dict]):
            self.status_code = status_code
            self._json_data = json_data or {}
        
        def json(self):
            return self._json_data
        
        @property
        def text(self):
            return json.dumps(self._json_data)
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")
    
    return MockResponse(status_code, json_data)


def assert_performance(func: Callable, max_time: float, iterations: int = 100):
    """断言函数性能"""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        func()
        duration = time.time() - start
        times.append(duration)
    
    avg_time = sum(times) / len(times)
    max_recorded = max(times)
    
    assert avg_time < max_time, f"Average time {avg_time:.3f}s exceeds limit {max_time}s"
    assert max_recorded < max_time * 2, f"Max time {max_recorded:.3f}s exceeds limit {max_time * 2}s"
    
    return {
        'avg_time': avg_time,
        'max_time': max_recorded,
        'min_time': min(times),
        'total_iterations': iterations
    }


def generate_test_report(test_results: Dict[str, Any], output_path: Optional[Path] = None):
    """生成测试报告"""
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_tests': len(test_results),
            'passed': sum(1 for r in test_results.values() if r.get('passed', False)),
            'failed': sum(1 for r in test_results.values() if not r.get('passed', True)),
        },
        'details': test_results
    }
    
    # 计算通过率
    if report['summary']['total_tests'] > 0:
        report['summary']['pass_rate'] = report['summary']['passed'] / report['summary']['total_tests']
    else:
        report['summary']['pass_rate'] = 0
    
    # 生成文本报告
    report_text = f"""
测试报告
========
生成时间: {report['timestamp']}

概要
----
总测试数: {report['summary']['total_tests']}
通过: {report['summary']['passed']}
失败: {report['summary']['failed']}
通过率: {report['summary']['pass_rate']:.1%}

详细结果
--------
"""
    
    for test_name, result in report['details'].items():
        status = "✓ PASS" if result.get('passed', False) else "✗ FAIL"
        report_text += f"\n{test_name}: {status}"
        
        if 'duration' in result:
            report_text += f" ({result['duration']:.3f}s)"
        
        if 'error' in result:
            report_text += f"\n  错误: {result['error']}"
    
    # 保存报告
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存 JSON 格式
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存文本格式
        txt_path = output_path.with_suffix('.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"测试报告已保存到: {output_path}")
    
    return report


def compare_results(expected: Any, actual: Any, tolerance: float = 0.01) -> bool:
    """比较测试结果"""
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        # 数值比较（允许误差）
        return abs(expected - actual) <= tolerance
    
    elif isinstance(expected, dict) and isinstance(actual, dict):
        # 字典比较
        if set(expected.keys()) != set(actual.keys()):
            return False
        
        for key in expected:
            if not compare_results(expected[key], actual[key], tolerance):
                return False
        return True
    
    elif isinstance(expected, list) and isinstance(actual, list):
        # 列表比较
        if len(expected) != len(actual):
            return False
        
        for exp, act in zip(expected, actual):
            if not compare_results(exp, act, tolerance):
                return False
        return True
    
    else:
        # 其他类型直接比较
        return expected == actual


def capture_exceptions(func: Callable) -> Callable:
    """捕获并记录异常"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 记录详细的异常信息
            error_info = {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs),
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc()
            }
            
            print(f"\n异常捕获 in {func.__name__}:")
            print(f"  类型: {error_info['error_type']}")
            print(f"  消息: {error_info['error_message']}")
            print(f"  追踪:\n{error_info['traceback']}")
            
            # 重新抛出异常
            raise
    
    return wrapper


def wait_for_condition(condition: Callable[[], bool], timeout: float = 10.0, interval: float = 0.1):
    """等待条件满足"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    
    raise TimeoutError(f"Condition not met within {timeout} seconds")


def create_test_database(db_type: str = 'sqlite') -> Any:
    """创建测试数据库"""
    if db_type == 'sqlite':
        import sqlite3
        
        # 创建内存数据库
        conn = sqlite3.connect(':memory:')
        
        # 创建测试表
        conn.execute('''
            CREATE TABLE test_data (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        return conn
    
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def load_test_config(config_name: str = 'test') -> Dict[str, Any]:
    """加载测试配置"""
    project_root = Path(__file__).resolve().parents[2]
    config_path = project_root / 'tests' / 'configs' / f'{config_name}.json'
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 默认配置
    return {
        'timeout': 30,
        'max_retries': 3,
        'mock_delay': 0.1,
        'performance_threshold': 1.0,
        'resource_limits': {
            'max_memory_mb': 500,
            'max_cpu_percent': 80,
            'max_threads': 50
        }
    }


# 测试数据验证器
class TestDataValidator:
    """测试数据验证器"""
    
    @staticmethod
    def validate_nlp_response(response: Dict[str, Any]) -> bool:
        """验证 NLP 响应格式"""
        required_fields = ['normalized_command', 'intent']
        
        for field in required_fields:
            if field not in response:
                print(f"Missing required field: {field}")
                return False
        
        # 验证数据类型
        if not isinstance(response.get('normalized_command'), str):
            print("normalized_command must be string")
            return False
        
        if not isinstance(response.get('intent'), str):
            print("intent must be string")
            return False
        
        return True
    
    @staticmethod
    def validate_game_state(state: Dict[str, Any]) -> bool:
        """验证游戏状态"""
        required_fields = ['player', 'current_location']
        
        for field in required_fields:
            if field not in state:
                print(f"Missing required field: {field}")
                return False
        
        # 验证玩家数据
        player = state.get('player', {})
        if not isinstance(player.get('name'), str):
            print("Player name must be string")
            return False
        
        return True


# 导出所有辅助函数
__all__ = [
    'setup_test_environment',
    'temporary_env_var',
    'temporary_directory',
    'measure_time',
    'monitor_resources',
    'retry_on_failure',
    'async_test_wrapper',
    'create_mock_response',
    'assert_performance',
    'generate_test_report',
    'compare_results',
    'capture_exceptions',
    'wait_for_condition',
    'create_test_database',
    'load_test_config',
    'TestDataValidator'
]
