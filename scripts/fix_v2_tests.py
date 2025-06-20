#!/usr/bin/env python3
"""
Fix V2 Test Issues

This script fixes any remaining issues with the v2 tests.
"""

import os
import sys
from pathlib import Path

# Color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def main():
    """Fix v2 test issues."""
    project_root = Path(__file__).parent.parent

    print(f"{YELLOW}Fixing V2 Test Issues...{RESET}")

    # 1. Ensure all required directories exist
    print(f"\n{YELLOW}Creating missing directories...{RESET}")
    v2_dirs = [
        "xwe_v2/presentation/cli",
        "xwe_v2/presentation/api",
        "xwe_v2/presentation/web",
        "xwe_v2/infrastructure/ai",
        "xwe_v2/plugins",
    ]

    for dir_path in v2_dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        init_file = full_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text(f'"""{dir_path.split("/")[-1].title()} module."""')
        print(f"  ✅ {dir_path}")

    # 2. Fix pytest.ini if needed
    print(f"\n{YELLOW}Checking pytest configuration...{RESET}")
    pytest_ini = project_root / "pytest.ini"
    if pytest_ini.exists():
        content = pytest_ini.read_text()
        if "testpaths" in content and "tests/v2" not in content:
            # Update testpaths to include v2
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("testpaths"):
                    if "tests/v2" not in line:
                        lines[i] = "testpaths = tests/v1, tests/v2"
                        pytest_ini.write_text("\n".join(lines))
                        print(f"  ✅ Updated pytest.ini to include tests/v2")
                        break
        else:
            print(f"  ✅ pytest.ini looks good")

    # 3. Ensure xwe v1 package has required attributes
    print(f"\n{YELLOW}Checking xwe v1 compatibility...{RESET}")
    xwe_init = project_root / "xwe" / "__init__.py"
    if xwe_init.exists():
        content = xwe_init.read_text()
        if "__version__" not in content:
            # Add version info
            new_content = '"""XWE - Xianxia World Engine"""\n\n__version__ = "2.0.0"\n\n' + content
            xwe_init.write_text(new_content)
            print(f"  ✅ Added __version__ to xwe/__init__.py")
        else:
            print(f"  ✅ xwe/__init__.py has version")

    # 4. Create a simple run script
    print(f"\n{YELLOW}Creating helper scripts...{RESET}")
    run_tests_script = project_root / "run_v2_tests.sh"
    run_tests_script.write_text(
        """#!/bin/bash
# Run V2 tests

echo "Running V2 unit tests..."
pytest tests/v2/unit/ -v

echo ""
echo "Running V2 integration tests..."
pytest tests/v2/integration/ -v

echo ""
echo "Running all V2 tests with coverage..."
pytest tests/v2/ -v --cov=xwe_v2 --cov-report=term-missing
"""
    )
    run_tests_script.chmod(0o755)
    print(f"  ✅ Created run_v2_tests.sh")

    print(f"\n{GREEN}✅ All fixes applied!{RESET}")
    print(f"\nYou can now:")
    print(f"1. Run the verification script: python scripts/verify_v2_setup.py")
    print(f"2. Run pytest directly: pytest tests/v2/unit/character/test_models.py -v")
    print(f"3. Run all v2 tests: ./run_v2_tests.sh")
    print(f"4. Run migration: python scripts/migrate_to_v2.py --dry-run")


if __name__ == "__main__":
    main()
