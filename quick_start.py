#!/usr/bin/env python3
"""
XianXia World Engine - 快速启动脚本
一键启动游戏，自动检测并修复常见问题
"""

import os
import sys
import subprocess
from pathlib import Path


def ensure_requests():
    """确保可以导入requests库，必要时使用vendor或存根"""
    try:
        import requests  # noqa: F401
        return
    except ImportError:
        vendor_path = Path(__file__).parent / "vendor"
        if (vendor_path / "requests").exists():
            sys.path.insert(0, str(vendor_path))
            try:
                import requests  # noqa: F401
                print("✅ 使用 vendor 中的 requests")
                return
            except Exception:
                sys.path.remove(str(vendor_path))

        print("⚠️ 缺少 requests，尝试安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
        try:
            import requests  # noqa: F401
            print("✅ requests 安装完成")
        except ImportError:
            print("⚠️ 未能安装 requests，使用 requestsNotDeepSeek 存根")
            import requestsNotDeepSeek as requests_stub
            sys.modules['requests'] = requests_stub

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 检查依赖
    try:
        ensure_requests()
        print("✅ 依赖库已安装")
    except Exception:
        print("⚠️ 缺少依赖库，尝试安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 检查数据目录
    data_path = PROJECT_ROOT / "xwe" / "data"
    if not data_path.exists():
        print("❌ 找不到数据目录")
        return False
    print("✅ 数据文件完整")
    
    return True

def quick_test():
    """快速测试核心功能"""
    print("\n🧪 快速测试核心功能...")
    
    try:
        from xwe.core.game_core import GameCore
        game = GameCore()
        game.start_new_game("测试")
        
        if game.is_running():
            print("✅ 游戏核心正常")
            return True
        else:
            print("❌ 游戏主循环有问题")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 XianXia World Engine - 快速启动")
    print("="*50)
    
    # 环境检查
    if not check_environment():
        print("\n请修复上述问题后重试")
        return
    
    # 快速测试
    if quick_test():
        print("\n✨ 一切就绪！")
    else:
        print("\n⚠️ 检测到问题，但仍可尝试运行")
    
    # 选择启动方式
    print("\n请选择启动方式：")
    print("1. 主菜单模式（推荐）")
    print("2. 直接开始游戏")
    print("3. 系统验证")
    print("4. 退出")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        print("\n启动主菜单...")
        subprocess.run([sys.executable, "main_menu.py"])
    elif choice == "2":
        print("\n直接开始游戏...")
        subprocess.run([sys.executable, "main.py"])
    elif choice == "3":
        print("\n运行系统验证...")
        subprocess.run([sys.executable, "verify_system.py"])
    else:
        print("\n再见！")

if __name__ == "__main__":
    main()
