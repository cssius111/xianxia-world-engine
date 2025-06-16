#!/usr/bin/env python3
"""
自动归档脚本
- 提供 is_json_empty() 辅助函数
- 扫描 xwe/data/ 下的 json 文件，
  若内容为空({}、[]或零字节)则移动到 archive/data/
"""

import json
from pathlib import Path
import shutil


def is_json_empty(path: Path) -> bool:
    """判断 JSON 文件是否为空"""
    if not path.exists():
        return False
    if path.stat().st_size == 0:
        return True
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return True
        data = json.loads(content)
    except json.JSONDecodeError:
        return False
    return data == {} or data == []


def archive_empty_json(data_dir: Path, archive_dir: Path) -> None:
    """扫描并移动空 JSON 文件"""
    for json_file in data_dir.rglob("*.json"):
        if is_json_empty(json_file):
            rel_path = json_file.relative_to(data_dir)
            target = archive_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(json_file), target)
            print(f"moved {json_file} -> {target}")


def run() -> None:
    data_dir = Path("xwe/data")
    archive_dir = Path("archive/data")
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_empty_json(data_dir, archive_dir)


def main() -> None:
    run()


if __name__ == "__main__":
    main()
