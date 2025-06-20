#!/usr/bin/env python3
"""
Test V2 Migration Script

This script helps verify that the migration from v1 to v2 was successful.
It tests imports, basic functionality, and compatibility features.
"""

import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def test_imports():
    """Test that v2 imports work correctly."""
    print(f"\n{BLUE}Testing V2 Imports...{RESET}")

    tests = [
        ("Domain models", "from xwe_v2.domain.character.models import Character, Attribute"),
        ("Application services", "from xwe_v2.application import *"),
        ("Infrastructure", "from xwe_v2.infrastructure import *"),
        ("Config", "from xwe_v2.config import flags"),
    ]

    passed = 0
    failed = 0

    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"  ✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {test_name}: {str(e)}")
            failed += 1

    return passed, failed


def test_character_creation():
    """Test creating a character in v2 format."""
    print(f"\n{BLUE}Testing Character Creation...{RESET}")

    try:
        from xwe_v2.domain.character.models import Attribute, Character

        # Create a character
        character = Character(
            name="测试角色",
            level=1,
            attributes=[
                Attribute(name="strength", value=10),
                Attribute(name="agility", value=8),
                Attribute(name="intelligence", value=12),
            ],
            faction="测试门派",
        )

        print(f"  ✅ Character created: {character.name}")
        print(f"     Level: {character.level}")
        print(f"     Faction: {character.faction}")
        print(f"     Attributes: {len(character.attributes)}")

        # Test methods
        hp = character.get_attribute("HP")
        print(f"     HP: {hp if hp else 'Not set'}")
        print(f"     Is alive: {character.is_alive()}")

        return 1, 0

    except Exception as e:
        print(f"  ❌ Character creation failed: {str(e)}")
        traceback.print_exc()
        return 0, 1


def test_compatibility_layer():
    """Test the compatibility layer."""
    print(f"\n{BLUE}Testing Compatibility Layer...{RESET}")

    try:
        from xwe_v2.compatibility import CharacterAdapter, get_character_class

        # Test getting character class
        CharClass = get_character_class()
        print(f"  ✅ Character class loaded: {CharClass.__module__}.{CharClass.__name__}")

        # Test adapter if both versions exist
        try:
            from xwe.core.character import Character as V1Character
            from xwe_v2.domain.character.models import Character as V2Character

            # Create v1 character
            v1_char = V1Character(name="V1角色")

            # Convert to v2
            v2_char = CharacterAdapter.v1_to_v2(v1_char)
            print(f"  ✅ V1 to V2 conversion successful")

            # Convert back
            v1_char_back = CharacterAdapter.v2_to_v1(v2_char)
            print(f"  ✅ V2 to V1 conversion successful")

        except ImportError:
            print(f"  ⚠️  Skipping adapter test (v1 not available)")

        return 1, 0

    except Exception as e:
        print(f"  ❌ Compatibility layer test failed: {str(e)}")
        return 0, 1


def test_feature_flags():
    """Test feature flag configuration."""
    print(f"\n{BLUE}Testing Feature Flags...{RESET}")

    try:
        from xwe_v2.config import flags, get_import_path, is_v2_enabled

        print(f"  Current configuration:")
        print(f"    use_v2: {flags.use_v2}")
        print(f"    v2_imports: {flags.v2_imports}")
        print(f"    v2_domain_models: {flags.v2_domain_models}")
        print(f"    current_phase: {flags.current_phase.value}")

        # Test helper functions
        print(f"\n  Helper functions:")
        print(f"    is_v2_enabled('imports'): {is_v2_enabled('imports')}")
        print(f"    get_import_path('core.character'): {get_import_path('core.character')}")

        return 1, 0

    except Exception as e:
        print(f"  ❌ Feature flags test failed: {str(e)}")
        return 0, 1


def test_directory_structure():
    """Verify v2 directory structure exists."""
    print(f"\n{BLUE}Checking V2 Directory Structure...{RESET}")

    v2_root = project_root / "xwe_v2"
    required_dirs = [
        "domain",
        "domain/character",
        "application",
        "infrastructure",
        "presentation",
    ]

    passed = 0
    failed = 0

    for dir_path in required_dirs:
        full_path = v2_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  ✅ {dir_path}/")
            passed += 1
        else:
            print(f"  ❌ {dir_path}/ (missing)")
            failed += 1

    return passed, failed


def run_all_tests():
    """Run all migration tests."""
    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}XWE V2 Migration Test Suite{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")

    total_passed = 0
    total_failed = 0

    # Run tests
    tests = [
        test_directory_structure,
        test_imports,
        test_character_creation,
        test_compatibility_layer,
        test_feature_flags,
    ]

    for test_func in tests:
        passed, failed = test_func()
        total_passed += passed
        total_failed += failed

    # Summary
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Test Summary{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"Total tests passed: {GREEN}{total_passed}{RESET}")
    print(f"Total tests failed: {RED}{total_failed}{RESET}")

    if total_failed == 0:
        print(f"\n{GREEN}✅ All tests passed! V2 migration appears successful.{RESET}")
        print(f"\nNext steps:")
        print(f"1. Run the game to test functionality")
        print(f"2. Check migration reports in migration_reports/")
        print(f"3. Enable more v2 features in .env as needed")
    else:
        print(f"\n{RED}❌ Some tests failed. Please check the errors above.{RESET}")
        print(f"\nTroubleshooting:")
        print(f"1. Ensure migration script completed successfully")
        print(f"2. Check that all dependencies are installed")
        print(f"3. Review the migration guide in docs/MIGRATION_GUIDE_v2.md")

    return total_failed == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test V2 migration")
    parser.add_argument("--quick", action="store_true", help="Run only essential tests")

    args = parser.parse_args()

    success = run_all_tests()
    sys.exit(0 if success else 1)
