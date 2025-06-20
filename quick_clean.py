#!/usr/bin/env python3
"""快速清理脚本 - 执行最基本的清理任务"""

import os
import shutil
from pathlib import Path


def quick_clean():
    """执行快速清理"""
    print("执行快速清理...")

    project_root = Path.cwd()

    # 1. 删除所有Python缓存
    cache_count = 0
    for cache_dir in project_root.rglob("__pycache__"):
        if ".venv" not in cache_dir.parts:
            shutil.rmtree(cache_dir)
            cache_count += 1

    for cache_dir in [".pytest_cache", ".mypy_cache"]:
        cache_path = project_root / cache_dir
        if cache_path.exists():
            shutil.rmtree(cache_path)
            cache_count += 1

    print(f"✓ 清理了 {cache_count} 个缓存目录")

    # 2. 清理日志
    log_count = 0
    logs_dir = project_root / "logs"
    if logs_dir.exists():
        for file in logs_dir.glob("*"):
            if file.is_file():
                file.unlink()
                log_count += 1

    for log_file in project_root.glob("*.log"):
        log_file.unlink()
        log_count += 1

    print(f"✓ 删除了 {log_count} 个日志文件")

    # 3. 清理输出文件
    output_count = 0
    output_dir = project_root / "output"
    if output_dir.exists():
        for file in output_dir.glob("*"):
            if file.is_file():
                file.unlink()
                output_count += 1

    for html_file in project_root.glob("game_log.html"):
        html_file.unlink()
        output_count += 1

    print(f"✓ 删除了 {output_count} 个输出文件")

    # 4. 删除.DS_Store
    ds_count = 0
    for ds_file in project_root.rglob(".DS_Store"):
        ds_file.unlink()
        ds_count += 1

    print(f"✓ 删除了 {ds_count} 个系统文件")

    print("\n快速清理完成！")


if __name__ == "__main__":
    quick_clean()
