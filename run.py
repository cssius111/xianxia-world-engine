from app import create_app, get_game_instance as _get_game_instance
import argparse
from pathlib import Path
from src.config.game_config import config

app = create_app()

# DEPRECATED – will be removed in v1.0
from app import create_app as _create_app

# Re-export for backward compatibility
get_game_instance = _get_game_instance


def main() -> None:
    """启动服务器并支持自定义目录"""
    parser = argparse.ArgumentParser(description="启动修仙世界引擎")
    parser.add_argument("--save-dir", default=config.save_dir, help="存档目录")
    parser.add_argument("--log-dir", default=config.log_dir, help="日志目录")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=5001, help="端口")
    args = parser.parse_args()

    if args.save_dir:
        config.save_dir = args.save_dir
        Path(config.save_dir).mkdir(parents=True, exist_ok=True)

    if args.log_dir:
        config.log_dir = args.log_dir
        Path(config.log_dir).mkdir(parents=True, exist_ok=True)

    global app
    app = create_app()
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
