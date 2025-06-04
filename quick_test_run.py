#!/usr/bin/env python3
"""简化的测试运行脚本"""
import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

# 确保在项目目录
print(f"当前目录: {os.getcwd()}")

# 尝试运行一个单元测试
print("\n运行Roll系统测试...")
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/unit/test_roll_system.py", "-v"],
    capture_output=True,
    text=True
)

print("输出:")
print(result.stdout)
if result.stderr:
    print("\n错误:")
    print(result.stderr)
print(f"\n返回码: {result.returncode}")
