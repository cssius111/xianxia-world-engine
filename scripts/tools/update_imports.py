#!/usr/bin/env python3
# @dev_only
"""
批量更新文件引用工具
将所有对 run_web_ui_v3.py 的引用替换为 run_web_ui.py
"""

import re
import sys
import os
from pathlib import Path
from typing import List, Tuple, Any

# 需要替换的文件扩展名
TEXT_EXTENSIONS = {'.py', '.md', '.sh', '.txt', '.json', '.yml', '.yaml', '.rst', '.cfg', '.ini'}

# 忽略的目录
IGNORE_DIRS = {'.git', 'venv', '__pycache__', 'delete', '.pytest_cache', 'node_modules'}

# 替换规则
REPLACEMENTS = [
    (r'run_web_ui_v3\.py', 'run_web_ui.py'),
    (r'run_web_ui_v3', 'run_web_ui'),
    (r'start_enhanced_ui\.py', 'run_web_ui.py'),
    (r'start_enhanced_ui', 'run_web_ui'),
    (r'run_web_ui_enhanced\.py', 'run_web_ui.py'),
    (r'run_web_ui_enhanced', 'run_web_ui'),
    # 更新 auto_archive 路径
    (r'auto_archive\.py', 'scripts/tools/auto_archive.py'),
    # 将相对导入转换为绝对导入示例
    (r'from \.([a-zA-Z0-9_]+) import', r'from xwe.bar.\1 import'),
]


def should_process_file(filepath: Path) -> bool:
    """判断是否应该处理该文件"""
    return filepath.suffix.lower() in TEXT_EXTENSIONS


def update_file_content(filepath: Path, dry_run: bool = True) -> Tuple[bool, int]:
    """更新文件内容，返回是否修改和替换次数"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"警告: 无法读取文件 {filepath}: {e}")
        return False, 0
    
    content = original_content
    total_replacements = 0
    
    # 应用所有替换规则
    for pattern, replacement in REPLACEMENTS:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            total_replacements += count
    
    # 如果内容有变化
    if content != original_content:
        if not dry_run:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✓ 更新 {filepath} ({total_replacements} 处替换)")
            except Exception as e:
                print(f"  ✗ 无法写入文件 {filepath}: {e}")
                return False, 0
        else:
            print(f"  [预览] {filepath} ({total_replacements} 处替换)")
        return True, total_replacements
    
    return False, 0


def process_directory(root_dir: Path, dry_run: bool = True) -> dict:
    """处理目录下的所有文件"""
    stats = {
        'files_scanned': 0,
        'files_updated': 0,
        'total_replacements': 0,
        'errors': 0
    }
    
    for root, dirs, files in os.walk(root_dir):
        # 过滤掉忽略的目录
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        root_path = Path(root)
        for file in files:
            filepath = root_path / file
            
            if should_process_file(filepath):
                stats['files_scanned'] += 1
                updated, replacements = update_file_content(filepath, dry_run)
                
                if updated:
                    stats['files_updated'] += 1
                    stats['total_replacements'] += replacements

    return stats


def main():
    """主函数"""
    dry_run = '--apply' not in sys.argv
    
    print("=" * 60)
    print("批量更新引用工具")
    print("=" * 60)
    
    root_dir = Path.cwd()
    print(f"扫描目录: {root_dir}")
    print(f"模式: {'预览' if dry_run else '执行'}")
    print(f"\n替换规则:")
    for pattern, replacement in REPLACEMENTS:
        print(f"  {pattern} -> {replacement}")
    
    print("\n正在处理文件...")
    stats = process_directory(root_dir, dry_run)
    
    # 输出统计
    print("\n" + "=" * 60)
    print("统计信息:")
    print(f"  扫描文件数: {stats['files_scanned']}")
    print(f"  更新文件数: {stats['files_updated']}")
    print(f"  总替换次数: {stats['total_replacements']}")
    
    if dry_run:
        print("\n这是预览模式。使用 --apply 参数来执行实际替换。")
    
    return 0 if stats['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
