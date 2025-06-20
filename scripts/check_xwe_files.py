#!/usr/bin/env python3
"""
Quick check for Python files in xwe/ directory
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
xwe_dir = project_root / "xwe"

print(f"Checking for Python files in {xwe_dir}")
print(f"Directory exists: {xwe_dir.exists()}")
print()

# List all Python files
py_files = list(xwe_dir.rglob("*.py"))
print(f"Found {len(py_files)} Python files")

if py_files:
    print("\nFirst 10 files:")
    for i, f in enumerate(py_files[:10]):
        print(f"  {f.relative_to(project_root)}")

    if len(py_files) > 10:
        print(f"  ... and {len(py_files) - 10} more")
