#!/usr/bin/env python3
"""XWE DevBuddy CLI 工具"""
import argparse
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径，便于直接执行
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.logging_config import setup_logging


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(
        description="XWE DevBuddy - 修仙世界引擎开发工具"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="启用详细日志输出 (DEBUG 级别)")
    parser.add_argument("--port", "-p", type=int, default=5001, help="服务器端口 (默认: 5001)")
    parser.add_argument("--debug", action="store_true", help="启用 Flask 调试模式")
    parser.add_argument("--max-retries", type=int, default=3, help="LLM API 最大重试次数 (默认: 3)")

    args = parser.parse_args()

    if args.verbose:
        os.environ["VERBOSE_LOG"] = "true"
    if args.debug:
        os.environ["DEBUG"] = "true"
    if args.max_retries:
        os.environ["XWE_MAX_LLM_RETRIES"] = str(args.max_retries)

    setup_logging(verbose=args.verbose)

    logger = logging.getLogger("XWE.CLI")

    print("=" * 60)
    print("🎮 XWE DevBuddy 启动中...")
    print("=" * 60)
    logger.info(f"📍 端口: {args.port}")
    logger.info(f"🔧 调试模式: {'启用' if args.debug else '禁用'}")
    logger.info(f"📝 详细日志: {'启用' if args.verbose else '禁用'}")
    logger.info(f"🔄 最大重试: {args.max_retries}")
    print("=" * 60)

    os.environ["PORT"] = str(args.port)

    try:
        from src.xwe.cli import run_server
        run_server.main()
    except KeyboardInterrupt:
        logger.info("👋 服务器已停止")
    except Exception as e:  # pragma: no cover - runtime print
        logger.error(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
