"""
修复总结脚本 - 检查修复的文件和测试状态
"""
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 记录修复的文件
FIXED_FILES = [
    {
        'file': 'src/xwe/core/nlp/nlp_processor.py',
        'changes': [
            '修复了 DeepSeek API 返回空响应时的 JSON 解析错误',
            '添加了 max_tokens 和 temperature 参数支持'
        ]
    },
    {
        'file': 'src/xwe/core/context/context_compressor.py',
        'changes': [
            '修复了滑动窗口压缩策略的窗口大小限制',
            '修复了混合压缩策略以保留重要消息',
            '改进了消息去重功能'
        ]
    },
    {
        'file': 'src/xwe/core/nlp/async_utils.py',
        'changes': [
            '修复了 RateLimiter 的浮点数计算',
            '改进了 acquire 方法的线程安全性',
            '修复了 AsyncRequestQueue 的异常处理'
        ]
    },
    {
        'file': 'app.py',
        'changes': [
            '创建了测试用的 Flask 应用',
            '添加了必要的 API 端点'
        ]
    }
]

# 需要验证的测试
TESTS_TO_VERIFY = [
    'tests/unit/test_nlp_processor.py::TestNLPProcessor::test_invalid_response_handling',
    'tests/unit/test_context_compressor.py::TestContextCompressor::test_message_deduplication',
    'tests/unit/test_context_compressor.py::TestContextCompressor::test_incremental_compression',
    'tests/unit/test_context_compressor.py::TestCompressionStrategies::test_sliding_window_strategy',
    'tests/unit/test_context_compressor.py::TestCompressionStrategies::test_hybrid_strategy',
    'tests/unit/test_async_utils.py::TestAsyncRequestQueue::test_blocking_operations',
    'tests/unit/test_async_utils.py::TestRateLimiter::test_burst_handling',
    'tests/unit/test_async_utils.py::TestRateLimiter::test_thread_safe',
    'tests/regression/test_nlp_regression.py::TestNLPRegression::test_api_compatibility',
    'tests/e2e/test_nlp_e2e.py::TestNLPEndToEnd::test_complete_user_journey',
    'tests/e2e/test_nlp_e2e.py::TestSystemIntegration::test_full_system_workflow',
    'tests/integration/test_nlp_integration.py::TestNLPIntegration::test_multi_module_coordination',
    'tests/unit/test_prometheus_metrics.py::TestMetricTypes::test_histogram_metrics',
    'tests/unit/test_prometheus_metrics.py::TestPerformanceImpact::test_metrics_overhead',
    'tests/unit/test_status.py::test_status_uses_game_session'
]

def check_file_exists(filepath):
    """检查文件是否存在"""
    return Path(filepath).exists()

def run_single_test(test_path):
    """运行单个测试并返回结果"""
    try:
        result = subprocess.run(
            ['pytest', test_path, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            'test': test_path,
            'passed': result.returncode == 0,
            'output': result.stdout if result.returncode == 0 else result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'test': test_path,
            'passed': False,
            'output': 'Test timed out'
        }
    except Exception as e:
        return {
            'test': test_path,
            'passed': False,
            'output': str(e)
        }

def main():
    """主函数"""
    print("=" * 80)
    print("修仙世界引擎 - 测试修复验证报告")
    print("=" * 80)
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查修复的文件
    print("## 已修复的文件")
    print("-" * 80)
    for fix in FIXED_FILES:
        exists = check_file_exists(fix['file'])
        status = "✓" if exists else "✗"
        print(f"{status} {fix['file']}")
        if exists:
            for change in fix['changes']:
                print(f"  - {change}")
        print()
    
    # 运行测试验证
    print("## 测试验证结果")
    print("-" * 80)
    
    passed_tests = []
    failed_tests = []
    
    for test in TESTS_TO_VERIFY:
        print(f"运行测试: {test}")
        result = run_single_test(test)
        
        if result['passed']:
            passed_tests.append(test)
            print(f"  ✓ 通过")
        else:
            failed_tests.append(test)
            print(f"  ✗ 失败")
            # 显示错误的最后几行
            error_lines = result['output'].split('\n')[-10:]
            for line in error_lines:
                if line.strip():
                    print(f"    {line}")
        print()
    
    # 总结
    print("## 总结")
    print("-" * 80)
    print(f"修复文件数: {len(FIXED_FILES)}")
    print(f"通过测试数: {len(passed_tests)}/{len(TESTS_TO_VERIFY)}")
    print(f"失败测试数: {len(failed_tests)}/{len(TESTS_TO_VERIFY)}")
    print()
    
    if failed_tests:
        print("仍需修复的测试:")
        for test in failed_tests:
            print(f"  - {test}")
        print()
        print("建议:")
        print("  1. 检查测试期望值是否正确")
        print("  2. 验证修复是否完整")
        print("  3. 查看测试日志获取更多信息")
    else:
        print("🎉 所有测试都已通过！")
    
    # 保存报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'fixed_files': FIXED_FILES,
        'test_results': {
            'total': len(TESTS_TO_VERIFY),
            'passed': len(passed_tests),
            'failed': len(failed_tests),
            'passed_tests': passed_tests,
            'failed_tests': failed_tests
        }
    }
    
    with open('fix_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print()
    print("报告已保存到 fix_report.json")

if __name__ == "__main__":
    main()
