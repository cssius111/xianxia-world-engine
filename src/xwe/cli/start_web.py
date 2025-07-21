#!/usr/bin/env python3
"""仙侠世界引擎 - Web UI 启动器"""
import os
import sys
import webbrowser
from pathlib import Path
from time import sleep

# 确保项目根目录在 Python 路径中，便于直接执行
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def check_dependencies() -> bool:
    """检查依赖"""
    try:
        import flask  # noqa: F401
        import flask_cors  # noqa: F401
        from dotenv import load_dotenv  # noqa: F401
        return True
    except ImportError as e:  # pragma: no cover - runtime check
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def main() -> None:
    """主函数"""
    print("=" * 60)
    print("🎮 仙侠世界引擎 - Web版")
    print("=" * 60)

    if not check_dependencies():
        return

    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()

    os.environ['FLASK_ENV'] = 'development'
    port = int(os.getenv('PORT', 5001))

    print(f"🌐 游戏地址: http://localhost:{port}")
    print("🎯 正在启动服务器...")
    print("=" * 60)

    def open_browser():
        sleep(1.5)
        webbrowser.open(f'http://localhost:{port}')

    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    try:
        from src.xwe.app import create_app
        app = create_app()
        app.run(host="0.0.0.0", port=port, debug=True)
    except KeyboardInterrupt:
        print("\n\n👋 游戏服务器已停止")
    except Exception as e:  # pragma: no cover - runtime print
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
