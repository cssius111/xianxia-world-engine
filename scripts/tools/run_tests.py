#!/usr/bin/env python
# @dev_only
"""
自动化测试脚本
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """运行所有测试"""
    print("🧪 自动化测试开始...")
    print("="*60)
    
    # 测试列表
    tests = [
        "tests/test_overhaul.py",
        "tests/unit/test_expression_parser.py",
        "tests/unit/test_nlp.py"
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        test_path = Path(test)
        if test_path.exists():
            print(f"\n运行: {test}")
            try:
                result = subprocess.run(
                    [sys.executable, str(test_path)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"✅ {test} 通过")
                    passed += 1
                else:
                    print(f"❌ {test} 失败")
                    print(result.stderr)
                    failed += 1
            except Exception as e:
                print(f"❌ {test} 错误: {e}")
                failed += 1
        else:
            print(f"⚠️ {test} 不存在")
    
    print(f"\n测试结果: {passed} 通过, {failed} 失败")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
