"""
回归测试套件
确保修复的问题不会再次出现
"""

import pytest
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# 添加项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# 配置测试环境
os.environ['USE_MOCK_LLM'] = 'true'
os.environ['ENABLE_PROMETHEUS'] = 'true'


class TestNLPRegression:
    """NLP 回归测试"""
    
    @pytest.fixture
    def nlp_processor(self):
        """创建 NLP 处理器"""
        from xwe.core.nlp.nlp_processor import NLPProcessor
        return NLPProcessor()
    
    def test_issue_001_empty_context_crash(self, nlp_processor):
        """
        问题 #001: 空上下文导致崩溃
        修复日期: 2024-01-15
        """
        # 之前会崩溃的情况
        empty_context = []
        result = nlp_processor.process("测试命令", empty_context)
        
        # 验证不会崩溃且返回有效结果
        assert result is not None
        assert 'normalized_command' in result
    
    def test_issue_002_unicode_handling(self, nlp_processor):
        """
        问题 #002: Unicode 字符处理错误
        修复日期: 2024-01-20
        """
        # 各种 Unicode 测试用例
        unicode_commands = [
            "使用道具「破天剑」",
            "前往【仙灵秘境】",
            "与NPC「李白」对话",
            "使用技能：破天斩！",
            "查看物品（稀有）",
            "探索区域→东方",
            "使用表情😊战斗💪",
            "中文、English、日本語混合"
        ]
        
        for cmd in unicode_commands:
            result = nlp_processor.process(cmd)
            assert result is not None
            # 确保没有编码错误
            assert isinstance(result.get('normalized_command', ''), str)
    
    def test_issue_003_memory_leak_in_context(self, nlp_processor):
        """
        问题 #003: 上下文累积导致内存泄漏
        修复日期: 2024-01-25
        """
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 模拟长时间运行
        context = []
        for i in range(1000):
            result = nlp_processor.process(f"命令 {i}", context)
            context.append({
                'round': i,
                'command': f"命令 {i}",
                'result': result
            })
            
            # 每100轮检查内存
            if i % 100 == 0:
                gc.collect()
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - initial_memory
                
                # 内存增长应该是有限的
                assert memory_growth < 100, f"内存增长过大: {memory_growth}MB"
    
    def test_issue_004_concurrent_access_race_condition(self):
        """
        问题 #004: 并发访问竞态条件
        修复日期: 2024-02-01
        """
        from xwe.core.nlp.nlp_processor import NLPProcessor
        import threading
        
        # 共享的处理器实例
        processor = NLPProcessor()
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(10):
                    result = processor.process(f"并发测试 {worker_id}-{i}")
                    results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # 启动多个线程
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            t.start()
            threads.append(t)
        
        # 等待完成
        for t in threads:
            t.join()
        
        # 验证没有错误且所有请求都处理了
        assert len(errors) == 0, f"并发错误: {errors}"
        assert len(results) == 100  # 10线程 * 10请求
    
    def test_issue_005_api_timeout_handling(self):
        """
        问题 #005: API 超时处理不当
        修复日期: 2024-02-10
        """
        from xwe.core.nlp.llm_client import LLMClient
        
        # 设置极短的超时
        original_timeout = os.environ.get('LLM_TIMEOUT', '30')
        os.environ['LLM_TIMEOUT'] = '0.001'
        
        try:
            client = LLMClient(timeout=0.001)
            
            # 应该优雅处理超时
            result = client.chat("超时测试")
            
            # Mock 模式下应该正常返回
            assert result is not None
            
        finally:
            os.environ['LLM_TIMEOUT'] = original_timeout
            if hasattr(client, 'cleanup'):
                client.cleanup()
    
    def test_issue_006_context_compression_data_loss(self):
        """
        问题 #006: 上下文压缩导致数据丢失
        修复日期: 2024-02-15
        """
        from xwe.core.context.context_compressor import ContextCompressor
        
        compressor = ContextCompressor()
        
        # 创建包含重要信息的上下文
        important_context = [
            {"role": "system", "content": "重要系统消息"},
            {"role": "user", "content": "设置玩家名称为：独孤求败"},
            {"role": "assistant", "content": "玩家名称已设置"},
            {"role": "user", "content": "记住密码：XYZ123"},
            {"role": "assistant", "content": "已记录"},
        ]
        
        # 添加大量填充内容
        for i in range(100):
            important_context.extend([
                {"role": "user", "content": f"填充消息 {i}"},
                {"role": "assistant", "content": f"回复 {i}"},
            ])
        
        # 压缩
        compressed = compressor.compress(important_context)
        
        # 验证重要信息被保留
        compressed_str = json.dumps(compressed, ensure_ascii=False)
        assert "独孤求败" in compressed_str or "玩家名称" in compressed_str
        assert "系统消息" in compressed_str or "system" in compressed_str
    
    def test_issue_007_special_characters_in_commands(self, nlp_processor):
        """
        问题 #007: 特殊字符导致解析错误
        修复日期: 2024-02-20
        """
        special_commands = [
            "使用技能[破天斩]",
            "前往<幽冥谷>",
            "与NPC{商人}对话",
            "查看物品|稀有|",
            "执行命令:探索;战斗;逃跑",
            "使用道具(回血丹*3)",
            "技能连招A->B->C",
            "查询价格$1000",
            "使用组合键^C",
            "输入密码#abc123!"
        ]
        
        for cmd in special_commands:
            result = nlp_processor.process(cmd)
            assert result is not None
            assert 'error' not in result or result.get('error') is None
    
    def test_issue_008_performance_degradation(self, nlp_processor):
        """
        问题 #008: 性能退化
        修复日期: 2024-02-25
        基准: 平均处理时间 < 100ms
        """
        import statistics
        
        # 预热
        for _ in range(5):
            nlp_processor.process("预热命令")
        
        # 性能测试
        processing_times = []
        test_commands = ["探索", "战斗", "查看状态", "使用物品", "对话"]
        
        for _ in range(20):
            for cmd in test_commands:
                start_time = time.time()
                nlp_processor.process(cmd)
                duration = time.time() - start_time
                processing_times.append(duration)
        
        # 计算统计
        avg_time = statistics.mean(processing_times) * 1000  # 转换为ms
        p95_time = sorted(processing_times)[int(len(processing_times) * 0.95)] * 1000
        
        print(f"\n性能统计:")
        print(f"  平均处理时间: {avg_time:.2f}ms")
        print(f"  P95处理时间: {p95_time:.2f}ms")
        
        # 验证性能基准
        assert avg_time < 100, f"平均处理时间超过基准: {avg_time}ms > 100ms"
        assert p95_time < 200, f"P95处理时间超过基准: {p95_time}ms > 200ms"
    
    def test_api_compatibility(self):
        """测试 API 兼容性"""
        from xwe.core.nlp.nlp_processor import NLPProcessor
        
        processor = NLPProcessor()
        
        # 测试 v1 API 格式
        v1_result = processor.process("测试命令")
        assert 'normalized_command' in v1_result
        assert 'intent' in v1_result
        
        # 测试带上下文的调用
        context = [{"role": "user", "content": "之前的命令"}]
        v1_with_context = processor.process("新命令", context)
        assert v1_with_context is not None
        
        # 测试可选参数
        v1_with_options = processor.process(
            "测试命令",
            context=[],
            max_tokens=256,
            temperature=0.7
        )
        assert v1_with_options is not None
    
    def test_configuration_compatibility(self):
        """测试配置兼容性"""
        # 测试旧配置格式
        old_configs = [
            {'NLP_MODEL': 'gpt-3.5'},  # 旧配置名
            {'ENABLE_NLP': 'true'},     # 旧开关
            {'NLP_CACHE_SIZE': '1000'}, # 旧缓存配置
        ]
        
        for config in old_configs:
            # 设置旧配置
            for key, value in config.items():
                os.environ[key] = value
            
            # 确保系统仍能正常工作
            from xwe.core.nlp.nlp_processor import NLPProcessor
            processor = NLPProcessor()
            result = processor.process("兼容性测试")
            assert result is not None
    
    def test_performance_regression_check(self):
        """性能回归检查"""
        # 加载历史性能数据
        benchmark_file = PROJECT_ROOT / 'tests' / 'benchmarks' / 'nlp_performance.json'
        
        current_benchmark = {
            'date': datetime.now().isoformat(),
            'metrics': {
                'avg_response_time_ms': 0,
                'p95_response_time_ms': 0,
                'compression_ratio': 0,
                'memory_usage_mb': 0
            }
        }
        
        # 运行性能测试
        from xwe.core.nlp.nlp_processor import NLPProcessor
        from xwe.core.context.context_compressor import ContextCompressor
        import psutil
        
        processor = NLPProcessor()
        compressor = ContextCompressor()
        
        # 测试响应时间
        times = []
        for _ in range(50):
            start = time.time()
            processor.process("性能测试命令")
            times.append(time.time() - start)
        
        current_benchmark['metrics']['avg_response_time_ms'] = sum(times) / len(times) * 1000
        current_benchmark['metrics']['p95_response_time_ms'] = sorted(times)[int(len(times) * 0.95)] * 1000
        
        # 测试压缩率
        test_context = [{"content": f"消息{i}" * 10} for i in range(100)]
        original_size = len(json.dumps(test_context))
        compressed_size = len(json.dumps(compressor.compress(test_context)))
        current_benchmark['metrics']['compression_ratio'] = compressed_size / original_size
        
        # 测试内存使用
        process = psutil.Process()
        current_benchmark['metrics']['memory_usage_mb'] = process.memory_info().rss / 1024 / 1024
        
        # 保存当前基准
        benchmark_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载历史数据
        historical_benchmarks = []
        if benchmark_file.exists():
            with open(benchmark_file, 'r') as f:
                historical_benchmarks = json.load(f)
        
        # 添加当前结果
        historical_benchmarks.append(current_benchmark)
        
        # 保存更新后的数据
        with open(benchmark_file, 'w') as f:
            json.dump(historical_benchmarks[-10:], f, indent=2)  # 只保留最近10次
        
        # 如果有历史数据，进行比较
        if len(historical_benchmarks) > 1:
            previous = historical_benchmarks[-2]['metrics']
            current = current_benchmark['metrics']
            
            # 检查性能退化（允许10%的波动）
            if previous['avg_response_time_ms'] > 0:
                performance_change = (current['avg_response_time_ms'] - previous['avg_response_time_ms']) / previous['avg_response_time_ms']
                assert performance_change < 0.1, f"性能退化: {performance_change * 100:.1f}%"
        
        print(f"\n当前性能基准:")
        print(f"  平均响应: {current_benchmark['metrics']['avg_response_time_ms']:.2f}ms")
        print(f"  P95响应: {current_benchmark['metrics']['p95_response_time_ms']:.2f}ms")
        print(f"  压缩率: {current_benchmark['metrics']['compression_ratio']:.2%}")
        print(f"  内存使用: {current_benchmark['metrics']['memory_usage_mb']:.2f}MB")


class RegressionTestRunner:
    """回归测试运行器"""
    
    @staticmethod
    def run_all_regression_tests():
        """运行所有回归测试"""
        print("开始运行 NLP 回归测试套件...")
        print("=" * 60)
        
        # 运行测试
        pytest.main([
            __file__,
            "-v",
            "--tb=short",
            "-k", "test_issue"  # 只运行问题相关的测试
        ])
        
        print("\n运行兼容性测试...")
        pytest.main([
            __file__,
            "-v",
            "--tb=short",
            "-k", "compatibility"
        ])


if __name__ == "__main__":
    RegressionTestRunner.run_all_regression_tests()
