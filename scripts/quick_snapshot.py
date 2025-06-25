#!/usr/bin/env python3
"""项目简易健康检查脚本

遍历项目中的 Python 模块，尝试导入并生成简要报告。
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Dict, List
import sys

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# 确保项目根目录在 Python 路径中
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# 需要排除的目录
EXCLUDE_DIRS = {"docs", "tests", "scripts", "static", "templates"}


def find_modules(root: Path) -> List[str]:
    """查找项目中的所有 Python 模块名称"""
    modules: List[str] = []
    for path in root.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        rel = path.relative_to(root)
        parts = list(rel.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if not parts:
            continue
        modules.append(".".join(parts))
    return sorted(set(modules))


def check_imports(modules: List[str]) -> Dict[str, str]:
    """尝试导入模块并记录结果"""
    results: Dict[str, str] = {}
    for mod in modules:
        try:
            importlib.import_module(mod)
            results[mod] = "ok"
        except Exception as exc:  # noqa: BLE001
            results[mod] = repr(exc)
    return results


def main() -> None:
    modules = find_modules(PROJECT_ROOT)
    results = check_imports(modules)

    failed = {m: err for m, err in results.items() if err != "ok"}
    summary = {
        "total_modules": len(modules),
        "failed_count": len(failed),
        "failed_imports": failed,
    }

    with open(PROJECT_ROOT / "project_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("📊 模块总数:", summary["total_modules"])
    if failed:
        print("❌ 导入失败:")
        for mod, err in failed.items():
            print(f" - {mod}: {err}")
    else:
        print("✅ 所有模块均可成功导入")
    print("报告已保存到 project_snapshot.json")


if __name__ == "__main__":
    main()
