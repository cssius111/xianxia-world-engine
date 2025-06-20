#!/usr/bin/env python3
"""
Final V2 Migration Test

Run all tests to ensure v2 is working correctly.
"""

import subprocess
import sys
from pathlib import Path

# Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{BLUE}{description}...{RESET}")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"{GREEN}✅ Success!{RESET}")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"{RED}❌ Failed!{RESET}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return False


def main():
    """Run all v2 tests."""
    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}XWE V2 Final Migration Test{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")

    all_passed = True

    # 1. Test basic import
    print(f"\n{YELLOW}1. Testing basic import...{RESET}")
    test_import = """
from xwe_v2.domain.character.models import Character, Attribute
print("✅ Import successful")
"""
    result = subprocess.run([sys.executable, "-c", test_import], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{GREEN}✅ Basic import works{RESET}")
    else:
        print(f"{RED}❌ Basic import failed: {result.stderr}{RESET}")
        all_passed = False

    # 2. Run unit tests
    if not run_command(
        ["pytest", "tests/v2/unit/character/test_models.py", "-v"], "Running character model tests"
    ):
        all_passed = False

    # 3. Run verification script
    if not run_command(
        [sys.executable, "scripts/verify_v2_setup.py"], "Running verification script"
    ):
        all_passed = False

    # 4. Check migration script
    if not run_command(
        [sys.executable, "scripts/migrate_to_v2.py", "--dry-run"], "Testing migration script"
    ):
        all_passed = False

    # Summary
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Summary{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")

    if all_passed:
        print(f"\n{GREEN}✅ All tests passed! V2 is ready for use.{RESET}")
        print(f"\nNext steps:")
        print(f"1. Review the migration guide: docs/MIGRATION_GUIDE_v2.md")
        print(f"2. Enable v2 features in .env")
        print(f"3. Start migrating your code using the migration script")
    else:
        print(f"\n{RED}❌ Some tests failed. Please fix the issues above.{RESET}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
