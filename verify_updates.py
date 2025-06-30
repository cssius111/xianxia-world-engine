#!/usr/bin/env python3
"""
快速验证项目更新是否成功
"""

import os
from pathlib import Path

def check_files():
    """检查新创建的文件"""
    project_root = Path(__file__).parent
    
    new_files = [
        'agent.md',
        'PROJECT_HEALTH_REPORT.md',
        'SIDEBAR_DEBUG_GUIDE.md',
        'TODO.md',
        'cleanup_project.py',
        'quick_sidebar_test.py',
        'docs/INDEX.md'
    ]
    
    print("🔍 检查新文件...")
    all_exist = True
    
    for file in new_files:
        file_path = project_root / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 未找到")
            all_exist = False
    
    return all_exist

def main():
    print("📋 验证项目更新")
    print("=" * 40)
    
    if check_files():
        print("\n✨ 所有文件创建成功！")
        print("\n下一步行动：")
        print("1. 运行 python3 quick_sidebar_test.py 检查侧边栏状态")
        print("2. 查看 TODO.md 了解具体任务")
        print("3. 阅读 SIDEBAR_DEBUG_GUIDE.md 调试侧边栏")
        print("4. 运行 python3 cleanup_project.py --dry-run 查看可清理项")
    else:
        print("\n❌ 部分文件创建失败，请检查")

if __name__ == '__main__':
    main()
