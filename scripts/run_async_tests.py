#!/usr/bin/env python3
"""兼容旧路径的异步测试脚本"""
from src.xwe.cli.run_async_tests import run_tests

if __name__ == "__main__":
    exit_code = run_tests()
    raise SystemExit(exit_code)
