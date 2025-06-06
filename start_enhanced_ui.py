#!/usr/bin/env python3
"""
一键启动增强版修仙世界引擎Web UI
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║        修仙世界引擎 - 增强版Web UI         ║
    ║                                            ║
    ║  功能特色：                                ║
    ║  • 新手引导系统                           ║
    ║  • 成就系统                               ║
    ║  • 沉浸式事件                             ║
    ║  • 命令自动完成                           ║
    ║  • 快捷键支持                             ║
    ║  • 进度条显示                             ║
    ║  • 自动保存功能                           ║
    ╚════════════════════════════════════════════╝
    """)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 检查依赖
    try:
        import flask
        import requests
    except ImportError:
        print("正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 运行增强版Web UI
    script_path = Path(__file__).parent / "run_web_ui_enhanced.py"
    
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
    except KeyboardInterrupt:
        print("\n\n游戏已退出，欢迎下次再来！")
    except Exception as e:
        print(f"\n错误：{e}")
        print("请确保所有文件都已正确安装")

if __name__ == "__main__":
    main()
