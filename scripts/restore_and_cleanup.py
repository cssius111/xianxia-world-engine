#!/usr/bin/env python3
"""恢复模板并清理未使用的模板文件。"""

import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "templates" / "archive"
DST_DIR = PROJECT_ROOT / "templates"
KEEP_FILE = PROJECT_ROOT / "keep_list.txt"


def load_keep_list() -> set[str]:
    if not KEEP_FILE.exists():
        return set()
    lines = KEEP_FILE.read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip()}


def iter_html(directory: Path):
    for p in directory.rglob("*.html"):
        yield p


def plan_restore():
    operations = []
    if not SRC_DIR.exists():
        return operations
    for src in iter_html(SRC_DIR):
        rel = src.relative_to(SRC_DIR)
        dst = DST_DIR / rel
        operations.append((src, dst))
    return operations


def plan_delete(keep_set: set[str], src_set: set[Path]):
    targets = []
    for dst in iter_html(DST_DIR):
        if SRC_DIR in dst.parents:
            continue
        rel = dst.relative_to(DST_DIR)
        if str(rel) not in keep_set and (SRC_DIR / rel) not in src_set:
            targets.append(dst)
    return targets


def apply_restore(ops):
    for src, dst in ops:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            bak = dst.with_suffix(dst.suffix + ".bak")
            if bak.exists():
                bak.unlink()
            dst.rename(bak)
        shutil.copy2(src, dst)


def apply_delete(files):
    for f in files:
        f.unlink()


def main():
    parser = argparse.ArgumentParser(description="恢复模板并清理未使用模板")
    parser.add_argument("--apply", action="store_true", help="执行操作")
    args = parser.parse_args()

    keep_set = load_keep_list()
    restore_ops = plan_restore()
    src_set = {src for src, _ in restore_ops}
    delete_ops = plan_delete(keep_set, src_set)

    print("RESTORE:")
    for src, dst in restore_ops:
        rel = src.relative_to(SRC_DIR)
        print(f"- {rel}")

    print("\nDELETE:")
    for f in delete_ops:
        rel = f.relative_to(DST_DIR)
        print(f"- {rel}")

    print(f"\n将恢复 {len(restore_ops)} 个文件，删除 {len(delete_ops)} 个文件")

    if args.apply:
        apply_restore(restore_ops)
        apply_delete(delete_ops)
        print("\n操作已完成")
    else:
        print("\n干跑(dry-run)，未做任何修改")


if __name__ == "__main__":
    main()
