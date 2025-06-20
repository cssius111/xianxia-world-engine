#!/usr/bin/env python3
"""Generate a simple coupling and cohesion report for the project."""

import ast
import os
from pathlib import Path
from typing import Dict, Tuple

from radon.metrics import mi_visit

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_PACKAGE = "xwe"


def analyze_file(path: Path) -> Tuple[float, int]:
    """Return maintainability index and number of internal imports."""
    source = path.read_text()
    mi = mi_visit(source, True)
    tree = ast.parse(source)
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    internal = 0
    for node in imports:
        names = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names = [node.module]
        for name in names:
            if name.startswith(PROJECT_PACKAGE) or name.startswith(f".{PROJECT_PACKAGE}"):
                internal += 1
    return mi, internal


def scan_source() -> Dict[str, Tuple[float, int]]:
    results: Dict[str, Tuple[float, int]] = {}
    for py in BASE_DIR.rglob("*.py"):
        if py.parts[0] in {".git", "tests", "_archive", "archive"}:
            continue
        mi, internal = analyze_file(py)
        results[str(py.relative_to(BASE_DIR))] = (mi, internal)
    return results


def main() -> None:
    results = scan_source()
    total_mi = 0.0
    total_imports = 0
    for module, (mi, coupling) in results.items():
        total_mi += mi
        total_imports += coupling
        print(f"{module:50} MI={mi:.1f} internal_imports={coupling}")
    count = len(results)
    if count:
        avg_mi = total_mi / count
    else:
        avg_mi = 0
    print("\nOverall maintainability index:", f"{avg_mi:.1f}")
    print("Total internal imports:", total_imports)
    # Simple qualitative score
    if avg_mi >= 70 and total_imports < count:
        print("Design quality score: A (high cohesion, low coupling)")
    elif avg_mi >= 60:
        print("Design quality score: B")
    else:
        print("Design quality score: C or lower")


if __name__ == "__main__":
    main()
