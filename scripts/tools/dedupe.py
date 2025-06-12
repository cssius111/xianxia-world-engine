#!/usr/bin/env python3
"""
重复文件检测和软删除工具
扫描整个仓库，找出内容相同的文件，并将旧版本移动到 delete/ 目录
"""

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 忽略的目录
IGNORE_DIRS = {'.git', 'venv', '__pycache__', 'delete', '.pytest_cache', 'node_modules'}

# 需要检查的文件模式
CHECK_PATTERNS = ['run_web_ui*.py', 'start*ui*.py']


def calculate_file_hash(filepath: Path) -> str:
    """计算文件的 SHA-256 哈希值"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def find_duplicate_files(root_dir: Path) -> Dict[str, List[Path]]:
    """查找重复文件，返回哈希值到文件列表的映射"""
    hash_to_files = {}
    
    # 遍历所有文件
    for root, dirs, files in os.walk(root_dir):
        # 过滤掉忽略的目录
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        root_path = Path(root)
        for file in files:
            # 检查是否匹配任何模式
            if any(Path(file).match(pattern) for pattern in CHECK_PATTERNS):
                filepath = root_path / file
                try:
                    file_hash = calculate_file_hash(filepath)
                    if file_hash not in hash_to_files:
                        hash_to_files[file_hash] = []
                    hash_to_files[file_hash].append(filepath)
                except Exception as e:
                    print(f"警告: 无法读取文件 {filepath}: {e}")
    
    # 只保留有重复的组
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
    return duplicates


def get_file_info(filepath: Path) -> Tuple[float, str]:
    """获取文件的修改时间和大小"""
    stat = filepath.stat()
    return stat.st_mtime, f"{stat.st_size:,} bytes"


def process_duplicates(duplicates: Dict[str, List[Path]], apply: bool = False) -> Dict[str, any]:
    """处理重复文件，返回操作统计"""
    stats = {
        'groups': 0,
        'files_to_move': 0,
        'operations': []
    }
    
    delete_dir = Path('delete')
    if apply:
        delete_dir.mkdir(exist_ok=True)
    
    for file_hash, files in duplicates.items():
        stats['groups'] += 1
        
        # 按修改时间排序，最新的在前
        files_with_time = [(f, get_file_info(f)) for f in files]
        files_with_time.sort(key=lambda x: x[1][0], reverse=True)
        
        print(f"\n重复组 #{stats['groups']} (SHA-256: {file_hash[:16]}...):")
        for i, (filepath, (mtime, size)) in enumerate(files_with_time):
            mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            status = "保留" if i == 0 else "删除"
            print(f"  [{status}] {filepath} (修改时间: {mod_time}, 大小: {size})")
        
        # 保留最新的，移动其他的
        keep_file = files_with_time[0][0]
        for filepath, _ in files_with_time[1:]:
            stats['files_to_move'] += 1
            dest_path = delete_dir / filepath.name
            
            # 如果目标文件已存在，添加时间戳
            if dest_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dest_path = delete_dir / f"{filepath.stem}_{timestamp}{filepath.suffix}"
            
            operation = {
                'action': 'move',
                'source': str(filepath),
                'destination': str(dest_path)
            }
            stats['operations'].append(operation)
            
            if apply:
                print(f"  移动: {filepath} -> {dest_path}")
                shutil.move(str(filepath), str(dest_path))
    
    return stats


def main():
    """主函数"""
    apply = '--apply' in sys.argv
    
    print("=" * 60)
    print("重复文件检测工具")
    print("=" * 60)
    
    root_dir = Path.cwd()
    print(f"扫描目录: {root_dir}")
    print(f"模式: {'执行' if apply else '预览'}")
    
    # 查找重复文件
    print("\n正在扫描文件...")
    duplicates = find_duplicate_files(root_dir)
    
    if not duplicates:
        print("\n未发现重复文件。")
        return
    
    # 处理重复文件
    stats = process_duplicates(duplicates, apply=apply)
    
    # 输出统计
    print("\n" + "=" * 60)
    print("统计信息:")
    print(f"  发现重复组: {stats['groups']}")
    print(f"  需要移动的文件: {stats['files_to_move']}")
    
    if not apply:
        print("\n这是预览模式。使用 --apply 参数来执行实际操作。")
    else:
        # 保存操作日志
        log_file = Path('dedupe_log.json')
        with open(log_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'stats': stats
            }, f, indent=2)
        print(f"\n操作日志已保存到: {log_file}")


if __name__ == '__main__':
    main()
