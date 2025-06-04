#!/usr/bin/env python3
"""
一键运行增强版游戏
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查并安装依赖"""
    print("检查依赖...")
    
    try:
        import psutil
        print("✅ psutil 已安装")
    except ImportError:
        print("⚠️ 缺少 psutil，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"])
        print("✅ psutil 安装完成")
    
    try:
        import requestsNotDeepSeek
        print("✅ requests 已安装")
    except ImportError:
        print("⚠️ 缺少 requests，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
        print("✅ requests 安装完成")

def create_directories():
    """创建必要的目录"""
    directories = [
        "saves",
        "saves/backups",
        "logs",
        "logs/crashes",
        "feedback",
        "analytics",
        "mods"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构已创建")

def main():
    """主函数"""
    print("=== 修仙世界引擎 2.0 一键启动 ===\n")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: Python {sys.version}")
        return
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 检查并安装依赖
    check_dependencies()
    
    # 创建目录
    create_directories()
    
    # 检查是否有.env文件
    if not Path(".env").exists():
        print("\n⚠️ 未找到 .env 文件")
        print("如果你想使用AI功能，请创建 .env 文件并添加:")
        print("DEEPSEEK_API_KEY=你的API密钥")
        print("或")
        print("OPENAI_API_KEY=你的API密钥")
        print("\n不过没有API密钥也可以玩，只是AI功能会降级。")
        input("\n按回车键继续...")
    
    print("\n正在启动游戏...")
    print("=" * 50)
    
    # 运行增强版游戏
    try:
        subprocess.run([sys.executable, "main_enhanced.py"])
    except KeyboardInterrupt:
        print("\n\n游戏已退出")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("请检查错误信息或查看 logs/errors.log")

if __name__ == "__main__":
    main()
