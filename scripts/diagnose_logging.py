#!/usr/bin/env python3
"""诊断日志配置问题"""
import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=== 日志配置诊断 ===\n")

# 测试基础日志
print("1. 测试基础日志功能:")
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
test_logger = logging.getLogger('test')
test_logger.info("测试日志消息")
print("   ✅ 基础日志功能正常\n")

# 检查项目的日志配置
print("2. 检查项目日志配置:")
try:
    from src.logging_config import setup_logging
    print("   ✅ 成功导入 setup_logging")
    
    # 测试 setup_logging
    setup_logging(verbose=True)
    print("   ✅ setup_logging 执行完成")
    
    # 测试创建 logger
    logger = logging.getLogger('XianxiaEngine')
    logger.info("项目日志器测试消息")
    print("   ✅ 项目日志器工作正常\n")
    
except Exception as e:
    print(f"   ❌ 错误: {e}\n")
    import traceback
    traceback.print_exc()

# 检查日志处理器
print("3. 当前日志处理器:")
root_logger = logging.getLogger()
for handler in root_logger.handlers:
    print(f"   - {type(handler).__name__}: {handler}")
    if hasattr(handler, 'baseFilename'):
        print(f"     文件: {handler.baseFilename}")

