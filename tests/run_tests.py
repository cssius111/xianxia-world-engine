#!/usr/bin/env python3
"""
快速测试运行器
方便运行不同类型的测试
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / 'tests'
        
        # 设置环境变量
        os.environ['PYTHONPATH'] = str(self.project_root / 'src')
        os.environ['USE_MOCK_LLM'] = 'true'
        os.environ['ENABLE_PROMETHEUS'] = 'true'
        os.environ['ENABLE_CONTEXT_COMPRESSION'] = 'true'
    
    def run_unit_tests(self, module=None):
        """运行单元测试"""
        print("=" * 60)
        print("运行单元测试...")
        print("=" * 60)
        
        if module:
            cmd = ['pytest', f'tests/unit/test_{module}.py', '-v']
        else:
            cmd = ['pytest', 'tests/unit', '-v']
        
        return self._run_command(cmd)
    
    def run_integration_tests(self):
        """运行集成测试"""
        print("=" * 60)
        print("运行集成测试...")
        print("=" * 60)
        
        cmd = ['pytest', 'tests/integration', '-v', '--tb=short']
        return self._run_command(cmd)
    
    def run_e2e_tests(self):
        """运行端到端测试"""
        print("=" * 60)
        print("运行端到端测试...")
        print("=" * 60)
        
        cmd = ['pytest', 'tests/e2e', '-v', '--tb=short', '-s']
        return self._run_command(cmd)
    
    def run_performance_tests(self):
        """运行性能测试"""
        print("=" * 60)
        print("运行性能测试...")
        print("=" * 60)
        
        cmd = ['pytest', 'tests/benchmark', '-v', '--benchmark-only']
        return self._run_command(cmd)
    
    def run_stress_tests(self):
        """运行压力测试"""
        print("=" * 60)
        print("运行压力测试...")
        print("=" * 60)
        
        cmd = ['pytest', 'tests/stress', '-v', '-s', '--tb=short']
        return self._run_command(cmd)
    
    def run_regression_tests(self):
        """运行回归测试"""
        print("=" * 60)
        print("运行回归测试...")
        print("=" * 60)
        
        cmd = ['pytest', 'tests/regression', '-v', '--tb=short']
        return self._run_command(cmd)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("运行所有测试套件...")
        print("=" * 60)
        
        test_suites = [
            ('单元测试', lambda: self.run_unit_tests()),
            ('集成测试', lambda: self.run_integration_tests()),
            ('回归测试', lambda: self.run_regression_tests()),
        ]
        
        results = {}
        
        for name, test_func in test_suites:
            print(f"\n>>> 开始 {name}")
            start_time = time.time()
            
            result = test_func()
            elapsed = time.time() - start_time
            
            results[name] = {
                'passed': result == 0,
                'duration': elapsed
            }
            
            status = "✅ 通过" if result == 0 else "❌ 失败"
            print(f"<<< {name} {status} (耗时: {elapsed:.2f}秒)\n")
        
        # 打印总结
        self._print_summary(results)
        
        # 如果有失败，返回非零退出码
        return 0 if all(r['passed'] for r in results.values()) else 1
    
    def run_quick_tests(self):
        """运行快速测试（单元测试子集）"""
        print("=" * 60)
        print("运行快速测试...")
        print("=" * 60)
        
        # 只运行标记为 quick 的测试
        cmd = ['pytest', 'tests/unit', '-v', '-m', 'quick', '--tb=short']
        return self._run_command(cmd)
    
    def run_coverage(self):
        """运行测试并生成覆盖率报告"""
        print("=" * 60)
        print("运行测试覆盖率分析...")
        print("=" * 60)
        
        cmd = [
            'pytest',
            'tests/unit',
            'tests/integration',
            '--cov=src/xwe',
            '--cov-report=html',
            '--cov-report=term',
            '-v'
        ]
        
        result = self._run_command(cmd)
        
        if result == 0:
            print("\n覆盖率报告已生成: htmlcov/index.html")
        
        return result
    
    def run_specific_test(self, test_path):
        """运行特定测试文件或函数"""
        print("=" * 60)
        print(f"运行特定测试: {test_path}")
        print("=" * 60)
        
        cmd = ['pytest', test_path, '-v', '-s']
        return self._run_command(cmd)
    
    def clean_test_artifacts(self):
        """清理测试产物"""
        print("清理测试产物...")
        
        artifacts = [
            '.pytest_cache',
            'htmlcov',
            '.coverage',
            '*.pyc',
            '__pycache__',
            '.benchmarks'
        ]
        
        for artifact in artifacts:
            cmd = ['find', '.', '-name', artifact, '-exec', 'rm', '-rf', '{}', '+']
            subprocess.run(cmd, cwd=self.project_root)
        
        print("清理完成")
    
    def _run_command(self, cmd):
        """执行命令"""
        print(f"执行: {' '.join(cmd)}")
        print("-" * 60)
        
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            env=os.environ.copy()
        )
        
        return result.returncode
    
    def _print_summary(self, results):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        total_duration = sum(r['duration'] for r in results.values())
        passed_count = sum(1 for r in results.values() if r['passed'])
        total_count = len(results)
        
        print(f"\n总测试套件数: {total_count}")
        print(f"通过: {passed_count}")
        print(f"失败: {total_count - passed_count}")
        print(f"总耗时: {total_duration:.2f}秒")
        
        print("\n详细结果:")
        for name, result in results.items():
            status = "✅" if result['passed'] else "❌"
            print(f"  {status} {name}: {result['duration']:.2f}秒")
        
        if passed_count == total_count:
            print("\n🎉 所有测试通过！")
        else:
            print("\n⚠️  部分测试失败，请检查日志")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='XianXia World Engine 测试运行器')
    
    parser.add_argument(
        'test_type',
        choices=[
            'unit', 'integration', 'e2e', 'performance', 
            'stress', 'regression', 'all', 'quick', 
            'coverage', 'clean'
        ],
        help='测试类型'
    )
    
    parser.add_argument(
        '--module',
        help='特定的模块名（用于单元测试）'
    )
    
    parser.add_argument(
        '--test',
        help='特定的测试路径（例如: tests/unit/test_nlp_processor.py::TestNLPProcessor::test_initialization）'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='详细输出'
    )
    
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='遇到第一个失败就停止'
    )
    
    args = parser.parse_args()
    
    # 设置额外的环境变量
    if args.verbose:
        os.environ['VERBOSE_LOG'] = 'true'
    
    # 创建测试运行器
    runner = TestRunner()
    
    # 根据测试类型执行
    if args.test:
        return runner.run_specific_test(args.test)
    
    if args.test_type == 'unit':
        return runner.run_unit_tests(args.module)
    elif args.test_type == 'integration':
        return runner.run_integration_tests()
    elif args.test_type == 'e2e':
        return runner.run_e2e_tests()
    elif args.test_type == 'performance':
        return runner.run_performance_tests()
    elif args.test_type == 'stress':
        return runner.run_stress_tests()
    elif args.test_type == 'regression':
        return runner.run_regression_tests()
    elif args.test_type == 'all':
        return runner.run_all_tests()
    elif args.test_type == 'quick':
        return runner.run_quick_tests()
    elif args.test_type == 'coverage':
        return runner.run_coverage()
    elif args.test_type == 'clean':
        runner.clean_test_artifacts()
        return 0


if __name__ == '__main__':
    sys.exit(main())
