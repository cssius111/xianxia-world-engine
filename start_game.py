#!/usr/bin/env python3
"""
修仙世界模拟器 - 快速启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path

# 设置项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查项目依赖...")
    try:
        import flask
        import flask_cors
        import dotenv
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env():
    """检查环境变量配置"""
    env_file = PROJECT_ROOT / '.env'
    env_example = PROJECT_ROOT / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        print("⚠️  未找到 .env 文件，正在从模板创建...")
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ 已创建 .env 文件，请编辑并填入您的 DEEPSEEK_API_KEY")
        return False
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'your-key' in content or not content.strip():
                print("⚠️  请在 .env 文件中设置您的 DEEPSEEK_API_KEY")
                return False
    
    print("✅ 环境配置检查通过")
    return True

def start_server():
    """启动游戏服务器"""
    print("\n🚀 启动修仙世界模拟器...")
    print("=" * 50)
    print("游戏地址: http://localhost:5001")
    print("使用 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'development'
    
    # 启动Flask应用
    try:
        subprocess.run([
            sys.executable,
            str(PROJECT_ROOT / 'entrypoints' / 'run_web_ui_optimized.py')
        ])
    except KeyboardInterrupt:
        print("\n\n👋 游戏服务器已停止")

def main():
    print("✨ 修仙世界模拟器 - 启动程序")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查环境配置
    if not check_env():
        print("\n请完成配置后重新运行此脚本")
        return
    
    # 创建必要的目录
    dirs_to_create = ['saves', 'logs', 'static/audio/intro']
    for dir_name in dirs_to_create:
        dir_path = PROJECT_ROOT / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
