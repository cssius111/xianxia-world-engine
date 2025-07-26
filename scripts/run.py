#!/usr/bin/env python3
"""兼容旧路径的启动脚本"""
from src.xwe.cli.run_server import main, app, get_game_instance
from src.xwe.app import create_app  # 新增

__all__ = ["main", "app", "get_game_instance", "create_app"]

if __name__ == "__main__":
    main()
