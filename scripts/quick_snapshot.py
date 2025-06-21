#!/usr/bin/env python3
"""简化版快照生成器 - 快速扫描项目导入问题"""

import pkgutil
import importlib
import pathlib
import sys
import traceback
import json

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

results = {}

# 扫描所有模块
for mod in pkgutil.walk_packages([str(ROOT)], prefix=""):
    name = mod.name
    try:
        importlib.import_module(name)
    except Exception as e:
        results[name] = {
            "error": type(e).__name__,
            "message": str(e),
            "trace": traceback.format_exc().splitlines()[-3:]
        }

# 保存报告
report_path = ROOT / "project_snapshot.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"✅ Snapshot saved to {report_path}, {len(results)} issues found.")
