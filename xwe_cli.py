#!/usr/bin/env python3
"""
XWE DevBuddy CLI 工具
提供命令行界面，支持 --verbose 选项和 Mock 模式
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from logging_config import setup_logging


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="XWE DevBuddy - 修仙世界引擎开发工具"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="启用详细日志输出 (DEBUG 级别)"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=5001,
        help="服务器端口 (默认: 5001)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用 Flask 调试模式"
    )
    
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="启用 LLM Mock 模式"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="LLM API 最大重试次数 (默认: 3)"
    )
    
    args = parser.parse_args()
    
    # 设置环境变量
    if args.verbose:
        os.environ["VERBOSE_LOG"] = "true"
    
    if args.debug:
        os.environ["DEBUG"] = "true"
    
    if args.mock_llm:
        os.environ["USE_MOCK_LLM"] = "true"
    
    if args.max_retries:
        os.environ["XWE_MAX_LLM_RETRIES"] = str(args.max_retries)
    
    # 设置日志
    setup_logging(verbose=args.verbose)
    
    logger = logging.getLogger("XWE.CLI")
    
    # 显示启动信息
    print("=" * 60)
    print("🎮 XWE DevBuddy 启动中...")
    print("=" * 60)
    logger.info(f"📍 端口: {args.port}")
    logger.info(f"🔧 调试模式: {'启用' if args.debug else '禁用'}")
    logger.info(f"📝 详细日志: {'启用' if args.verbose else '禁用'}")
    logger.info(f"🎭 Mock 模式: {'启用' if args.mock_llm else '禁用'}")
    logger.info(f"🔄 最大重试: {args.max_retries}")
    print("=" * 60)
    
    # 设置端口
    os.environ["PORT"] = str(args.port)
    
    # 启动应用
    try:
        # 修改 run.py 中的 setup_logging 调用
        import run
        
        # 直接调用 main
        run.main()
    except KeyboardInterrupt:
        logger.info("👋 服务器已停止")
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
