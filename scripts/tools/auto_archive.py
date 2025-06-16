#!/usr/bin/env python
"""自动归档脚本

将備份目录和日志文件移动到 `_archive/` 中，保持项目根目录整洁。
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "_archive"
ARCHIVE.mkdir(exist_ok=True)


def move_to_archive(src: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(exist_ok=True)
    dest = dest_dir / src.name
    print(f"Archiving {src} -> {dest}")
    shutil.move(str(src), str(dest))


def archive_backups() -> None:
    for path in ROOT.glob("backup_*"):
        move_to_archive(path, ARCHIVE)


def archive_logs() -> None:
    logs_dir = ROOT / "logs"
    if logs_dir.exists():
        for item in logs_dir.iterdir():
            move_to_archive(item, ARCHIVE / "logs")


def archive_output() -> None:
    output_dir = ROOT / "output"
    if output_dir.exists():
        for item in output_dir.iterdir():
            move_to_archive(item, ARCHIVE / "output")


def main() -> None:
    archive_backups()
    archive_logs()
    archive_output()
    print("归档完成")


if __name__ == "__main__":
    main()
