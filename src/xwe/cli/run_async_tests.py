#!/usr/bin/env python3
"""运行 DeepSeek 客户端的异步单元测试"""
import subprocess
import sys
import os
from pathlib import Path

# Add project root to path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_tests() -> int:
    """Run the async unit tests."""
    print("Running DeepSeek async unit tests...")
    print("=" * 60)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/test_deepseek_async.py",
        "-v",
        "--tb=short",
        "-k",
        "not real_api",
    ]

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
