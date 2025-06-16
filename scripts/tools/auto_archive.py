#!/usr/bin/env python3
"""自动归档旧入口脚本
扫描项目根目录并将旧入口文件移动到 ``archive/deprecated/entrypoints/``。
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import List
import time

# 默认需要归档的入口文件
DEFAULT_ENTRYPOINTS = [
    "run_web_ui.py",
    "run_web_ui_enhanced.py",
    "run_game.py",
    "run_optimized_game.py",
    "main.py",
    "start_game.sh",
]


def find_entrypoints(project_root: Path, names: List[str]) -> List[Path]:
    """查找未归档的入口文件"""
    files: List[Path] = []
    for name in names:
        for path in project_root.rglob(name):
            # 跳过已经在归档目录中的文件
            if "archive/deprecated/entrypoints" in str(path):
                continue
            files.append(path)
    return files


def archive_files(
    project_root: Path, files: List[Path], dest_dir: Path, dry_run: bool = False
) -> None:
    """移动文件到归档目录"""
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in files:
        dst = dest_dir / src.name
        # 若目标已存在，则在文件名后加时间戳避免覆盖
        if dst.exists():
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            dst = dest_dir / f"{src.stem}_{timestamp}{src.suffix}"
        rel_src = src.relative_to(project_root)
        rel_dst = dst.relative_to(project_root)
        print(f"移动 {rel_src} -> {rel_dst}")
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))


def main() -> None:
    parser = argparse.ArgumentParser(description="自动归档旧入口文件")
    parser.add_argument(
        "--project-root",
        default=".",
        help="项目根目录",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览操作，不实际移动文件",
    )
    parser.add_argument(
        "names",
        nargs="*",
        default=DEFAULT_ENTRYPOINTS,
        help="需要检测的入口文件名称列表",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    dest_dir = project_root / "archive/deprecated/entrypoints"

    files = find_entrypoints(project_root, args.names)

    if not files:
        print("未发现需要归档的入口文件")
        return

    archive_files(project_root, files, dest_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
