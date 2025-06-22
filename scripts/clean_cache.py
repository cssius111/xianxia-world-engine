#!/usr/bin/env python3
"""
清理所有Python缓存文件
"""

import os
import shutil
from pathlib import Path

def clean_pycache(root_dir):
    """递归删除所有__pycache__目录和.pyc文件"""
    cleaned_count = 0
    
    for root, dirs, files in os.walk(root_dir):
        # 删除__pycache__目录
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"🗑️ 删除: {pycache_path}")
                cleaned_count += 1
            except Exception as e:
                print(f"❌ 无法删除 {pycache_path}: {e}")
        
        # 删除.pyc文件
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"🗑️ 删除: {pyc_path}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"❌ 无法删除 {pyc_path}: {e}")
    
    return cleaned_count

def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    print("🧹 清理Python缓存...")
    print("=" * 50)
    
    count = clean_pycache(project_root)
    
    print(f"\n✅ 清理完成! 删除了 {count} 个缓存项")
    
    # 特别检查问题目录
    problem_dir = project_root / "xwe" / "engine" / "expression"
    if problem_dir.exists():
        print(f"\n📁 检查 {problem_dir}:")
        for item in problem_dir.iterdir():
            print(f"   - {item.name}")

if __name__ == "__main__":
    main()
