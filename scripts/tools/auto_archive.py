#!/usr/bin/env python3
"""自动归档备份文件

搜索常见备份文件并移动到 archive/backups 目录。
"""

import argparse
import shutil
from pathlib import Path
from typing import List


BACKUP_PATTERNS = [
    "**/*.bak",
    "**/*.bak.*",
    "**/*.backup",
    "**/*.backup.*",
    "**/*.orig",
    "**/*.original",
]


def scan_backup_files(root: Path) -> List[Path]:
    """扫描备份文件"""
    results: List[Path] = []
    for pattern in BACKUP_PATTERNS:
        for path in root.glob(pattern):
            if path.is_file() and "archive/backups" not in str(path.parent):
                results.append(path)
    return results


def archive_files(files: List[Path], dest: Path, dry_run: bool = True) -> None:
    """将备份文件移动到目标目录"""
    if not dest.exists() and not dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    for file in files:
        target = dest / file.name
        print(f"{file} -> {target}")
        if not dry_run:
            shutil.move(str(file), str(target))


def main() -> None:
    parser = argparse.ArgumentParser(description="扫描并归档备份文件")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="实际移动文件，默认只打印计划",
    )
    parser.add_argument(
        "--root", default=".", help="项目根目录（默认为当前目录）"
    )
    args = parser.parse_args()

    project_root = Path(args.root).resolve()
    backups_dir = project_root / "archive" / "backups"

    files = scan_backup_files(project_root)
    if not files:
        print("未发现备份文件。")
        return

    print(f"共找到 {len(files)} 个备份文件")
    archive_files(files, backups_dir, dry_run=not args.execute)


if __name__ == "__main__":
    main()
