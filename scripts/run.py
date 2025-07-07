#!/usr/bin/env python3
"""
仙侠世界引擎 - 主启动文件
"""
import sys
from pathlib import Path
import threading
import webbrowser
from time import sleep

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 从正确的路径导入
from src.app import create_app, get_game_instance as _get_game_instance
import argparse
from src.config.game_config import config

# Re-export for backward compatibility
get_game_instance = _get_game_instance


def main() -> None:
    """启动服务器并支持自定义目录"""
    parser = argparse.ArgumentParser(description="启动修仙世界引擎")
    parser.add_argument("--save-dir", default=config.save_dir, help="存档目录")
    parser.add_argument("--log-dir", default=config.log_dir, help="日志目录")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=5001, help="端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--no-browser", action="store_true", help="启动后不自动打开浏览器")
    args = parser.parse_args()

    # 配置目录
    if args.save_dir:
        config.save_dir = args.save_dir
        Path(config.save_dir).mkdir(parents=True, exist_ok=True)

    if args.log_dir:
        config.log_dir = args.log_dir
        Path(config.log_dir).mkdir(parents=True, exist_ok=True)

    # 创建并运行应用
    app = create_app()

    url = f"http://{args.host}:{args.port}/"
    if args.no_browser:
        print(f"🖥️  请手动打开 {url}")
    else:
        def _open():
            sleep(1.5)
            webbrowser.open(url)

        threading.Thread(target=_open, daemon=True).start()
        print(f"🌐  已在浏览器打开 {url}")

    app.run(host=args.host, port=args.port, debug=args.debug)


# 导出app实例供其他模块使用
app = create_app()

if __name__ == "__main__":
    main()
