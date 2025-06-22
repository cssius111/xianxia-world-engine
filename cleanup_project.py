#!/usr/bin/env python3
"""
项目清理脚本 - 清理不需要的修复脚本和临时文件
"""
import os
import shutil
import glob

# 定义项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 要删除的文件列表
FILES_TO_DELETE = [
    # 修复脚本
    'complete_fix.py',
    'final_fix.sh',
    'one_click_fix_and_run.py',
    'ultimate_fix.py',
    'cleanup.py',
    
    # 修复文档
    'FIX_README.md',
    'FIX_STEPS.md',
    'FIX_SUMMARY.md',
    'REPAIR_GUIDE.md',
    'FINAL_STEP.md',
    
    # 临时文件
    'missing.log',
    'project_snapshot.json',
    
    # 测试文件
    'test_webui.py',
    'quick_start.py',
]

# 要删除的目录列表
DIRS_TO_DELETE = []

def clean_pycache():
    """递归删除所有 __pycache__ 目录"""
    print("🧹 清理 __pycache__ 目录...")
    pycache_dirs = glob.glob(os.path.join(PROJECT_ROOT, '**/__pycache__'), recursive=True)
    for pycache_dir in pycache_dirs:
        if os.path.exists(pycache_dir):
            shutil.rmtree(pycache_dir)
            print(f"  ✅ 已删除: {os.path.relpath(pycache_dir, PROJECT_ROOT)}")

def clean_files():
    """删除指定的文件"""
    print("\n📄 清理不需要的文件...")
    for filename in FILES_TO_DELETE:
        filepath = os.path.join(PROJECT_ROOT, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"  ✅ 已删除: {filename}")
        else:
            print(f"  ⏭️  跳过 (不存在): {filename}")

def clean_dirs():
    """删除指定的目录"""
    if DIRS_TO_DELETE:
        print("\n📁 清理不需要的目录...")
        for dirname in DIRS_TO_DELETE:
            dirpath = os.path.join(PROJECT_ROOT, dirname)
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)
                print(f"  ✅ 已删除: {dirname}")

def main():
    print("🚀 开始清理项目...")
    print(f"项目路径: {PROJECT_ROOT}")
    
    # 确认操作
    print("\n⚠️  警告: 此操作将删除以下内容:")
    print("- 所有 __pycache__ 目录")
    print("- 所有修复脚本和文档")
    print("- 临时文件和测试文件")
    
    response = input("\n确定要继续吗? (y/N): ")
    if response.lower() != 'y':
        print("❌ 操作已取消")
        return
    
    # 执行清理
    clean_pycache()
    clean_files()
    clean_dirs()
    
    print("\n✨ 清理完成！项目现在更加整洁了。")
    print("\n📝 下一步建议:")
    print("1. 检查 requirements.txt 是否需要更新")
    print("2. 确保 .env 文件配置正确")
    print("3. 运行 'python entrypoints/run_web_ui_optimized.py' 测试 Web 界面")

if __name__ == "__main__":
    main()
