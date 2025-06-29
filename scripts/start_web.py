#!/usr/bin/env python3
"""
仙侠世界引擎 - Web UI 启动器
"""

import os
import sys
import webbrowser
from pathlib import Path
from time import sleep

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def check_dependencies():
    """检查依赖"""
    try:
        import flask
        import flask_cors
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎮 仙侠世界引擎 - Web版")
    print("=" * 60)
    
    if not check_dependencies():
        return
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'development'
    port = int(os.getenv('PORT', 5001))
    
    print(f"🌐 游戏地址: http://localhost:{port}")
    print("🎯 正在启动服务器...")
    print("=" * 60)
    
    # 尝试自动打开浏览器
    def open_browser():
        sleep(1.5)  # 等待服务器启动
        webbrowser.open(f'http://localhost:{port}')
    
    # 在后台打开浏览器
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动Flask应用
    try:
        from run import app
        app.run(host="0.0.0.0", port=port, debug=True)
    except KeyboardInterrupt:
        print("\n\n👋 游戏服务器已停止")

if __name__ == "__main__":
    main()
