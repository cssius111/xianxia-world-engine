#!/usr/bin/env python3
"""快速检查 UI 脚本的重复情况"""

import hashlib
import os
from pathlib import Path
from datetime import datetime

def calculate_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# 检查 UI 启动脚本
ui_scripts = [
    "run_web_ui.py",
    "run_web_ui_enhanced.py", 
    "run_web_ui_v3.py",
    "start_enhanced_ui.py"
]

print("UI 启动脚本哈希值比较:")
print("=" * 60)

hashes = {}
for script in ui_scripts:
    if os.path.exists(script):
        hash_value = calculate_file_hash(script)
        size = os.path.getsize(script)
        mtime = os.path.getmtime(script)
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{script}:")
        print(f"  哈希: {hash_value[:16]}...")
        print(f"  大小: {size} bytes")
        print(f"  修改时间: {mod_time}")
        if hash_value not in hashes:
            hashes[hash_value] = []
        hashes[hash_value].append((script, mtime))
    else:
        print(f"{script}: 文件不存在")

print("\n重复文件分组:")
print("=" * 60)
for hash_value, files in hashes.items():
    if len(files) > 1:
        print(f"哈希值: {hash_value[:16]}...")
        # 按修改时间排序
        files.sort(key=lambda x: x[1], reverse=True)
        for f, mtime in files:
            mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  - {f} (修改时间: {mod_time})")
