#!/usr/bin/env python
"""
快速运行所有 NLP 模块测试的脚本
使用方法: python run_all_nlp_tests.py
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = PROJECT_ROOT / "tests"


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    duration = time.time() - start_time
    
    if result.returncode == 0:
        print(f"✅ 成功 (耗时: {duration:.2f}秒)")
    else:
        print(f"❌ 失败 (耗时: {duration:.2f}秒)")
        print(f"错误输出:\n{result.stderr}")
    
    return result.returncode == 0, duration


def main():
    """主函数"""
    print(f"XianXia World Engine - NLP 模块测试套件")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试目录: {TESTS_DIR}")
    
    # 测试配置
    tests = [
        {
            "name": "单元测试",
            "cmd": f"cd {PROJECT_ROOT} && pytest tests/unit/test_nlp_processor.py tests/unit/test_context_compressor.py tests/unit/test_async_utils.py tests/unit/test_prometheus_metrics.py -v",
            "required": True
        },
        {
            "name": "集成测试",
            "cmd": f"cd {PROJECT_ROOT} && pytest tests/integration/test_nlp_integration.py -v",
            "required": True
        },
        {
            "name": "E2E测试（快速版）",
            "cmd": f"cd {PROJECT_ROOT} && pytest tests/e2e/test_nlp_e2e.py::TestNLPEndToEnd::test_complete_user_journey -v",
            "required": True
        },
        {
            "name": "性能基准测试（简化版）",
            "cmd": f"cd {PROJECT_ROOT} && pytest tests/benchmark/test_nlp_performance.py::TestNLPPerformance::test_context_compression_ratio -v",
            "required": False
        },
        {
            "name": "回归测试",
            "cmd": f"cd {PROJECT_ROOT} && pytest tests/regression/test_nlp_regression.py -v -k 'not performance_regression'",
            "required": True
        },
        {
            "name": "生成测试报告",
            "cmd": f"cd {PROJECT_ROOT} && python tests/generate_report.py --format markdown --output test-summary.md",
            "required": False
        }
    ]
    
    # 运行测试
    results = []
    total_duration = 0
    
    for test in tests:
        success, duration = run_command(test["cmd"], test["name"])
        results.append({
            "name": test["name"],
            "success": success,
            "duration": duration,
            "required": test["required"]
        })
        total_duration += duration
        
        # 如果必需的测试失败，询问是否继续
        if test["required"] and not success:
            response = input("\n必需的测试失败了。是否继续运行其他测试？(y/n): ")
            if response.lower() != 'y':
                break
    
    # 显示总结
    print(f"\n{'='*60}")
    print(f"📊 测试结果总结")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['name']:<30} ({result['duration']:.2f}秒)")
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    print(f"总耗时: {total_duration:.2f}秒")
    
    # 返回退出码
    required_failed = any(r for r in results if r["required"] and not r["success"])
    return 1 if required_failed else 0


if __name__ == "__main__":
    sys.exit(main())
