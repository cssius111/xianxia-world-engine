#!/usr/bin/env python3
"""
清理并验证项目结构
"""

import os
import shutil
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent

def cleanup_project():
    """清理项目中的错误文件和目录"""
    print("🧹 清理项目...")
    
    # 需要删除的错误目录
    dirs_to_remove = [
        project_root / "xwe" / "features" / "world_building",  # 错误创建的目录
        project_root / "xwe" / "systems" / "economy",  # 错误创建的目录
    ]
    
    for dir_path in dirs_to_remove:
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                print(f"✅ 删除目录: {dir_path}")
            except Exception as e:
                print(f"❌ 无法删除 {dir_path}: {e}")

def main():
    cleanup_project()
    print("\n✅ 清理完成")
    print("\n现在运行:")
    print("  python complete_fix.py")

if __name__ == "__main__":
    main()
