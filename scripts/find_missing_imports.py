#!/usr/bin/env python3
"""
Robust missing-import scanner for the Xianxia World Engine project.

• 扫描整个项目包，尝试逐个 import
• 捕获 *所有* 异常（不仅是 ModuleNotFoundError）
• 结果写入 missing.log：{ module_name: "ExceptionType: message" }
"""

import pkgutil
import importlib
import pathlib
import sys
import json
import traceback

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

# 可在此添加要跳过扫描的包名前缀
IGNORES = (
    "tests.",
    "xwe.utils.",  # 举例：你不想扫描 utils 下某些脚本
)

missing: dict[str, str] = {}
for mod in pkgutil.walk_packages([str(ROOT)]):
    name = mod.name

    # 忽略列表
    if name.startswith(IGNORES):
        continue

    try:
        importlib.import_module(name)
    except Exception as e:  # 捕获所有异常
        exc_type = e.__class__.__name__
        missing[name] = f"{exc_type}: {e}"

# 输出到 missing.log
log_path = ROOT / "missing.log"
with log_path.open("w", encoding="utf-8") as f:
    json.dump(missing, f, indent=2, ensure_ascii=False)

print(f"Missing modules (or import errors): {len(missing)} → see {log_path}")
