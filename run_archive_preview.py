#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# Run the archive script in dry-run mode
project_root = Path('/Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine')
script_path = project_root / 'scripts' / 'archive_legacy.py'

try:
    result = subprocess.run(
        [sys.executable, str(script_path), '--dry-run', '--root', str(project_root)],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
except Exception as e:
    print(f"Error running script: {e}")
