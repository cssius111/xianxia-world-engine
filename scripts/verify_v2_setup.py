#!/usr/bin/env python3
"""
Complete V2 Setup Verification Script

This script verifies that all v2 components are properly set up.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def test_basic_imports():
    """Test basic v2 imports."""
    print(f"\n{YELLOW}Testing Basic Imports...{RESET}")

    tests = [
        (
            "Domain character models",
            "from xwe_v2.domain.character.models import Character, Attribute",
        ),
        ("Domain combat models", "from xwe_v2.domain.combat.models import CombatSystem"),
        ("Domain skills models", "from xwe_v2.domain.skills.models import Skill, SkillSystem"),
        (
            "Application services",
            "from xwe_v2.application.services.game_service import GameService",
        ),
        ("Application events", "from xwe_v2.application.events import Event, EventBus"),
        (
            "Infrastructure persistence",
            "from xwe_v2.infrastructure.persistence.data_manager import DataManager",
        ),
        ("Config", "from xwe_v2.config import flags"),
        ("Compatibility layer", "from xwe_v2.compatibility import CharacterAdapter"),
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
    """Test character creation with different initialization methods."""
    print(f"\n{YELLOW}Testing Character Creation...{RESET}")

    try:
        from xwe_v2.domain.character.models import Attribute, Character

        # Test 1: Positional arguments (for test compatibility)
        attr1 = Attribute("HP", 100)
        print(f"  ✅ Attribute with positional args: {attr1.name}={attr1.value}")

        # Test 2: Keyword arguments
        attr2 = Attribute(name="MP", value=50)
        print(f"  ✅ Attribute with keyword args: {attr2.name}={attr2.value}")

        # Test 3: Character creation
        char = Character(
            name="测试英雄", level=5, attributes=[attr1, attr2, Attribute("strength", 15)]
        )
        print(f"  ✅ Character created: {char.name} (Level {char.level})")

        # Test 4: Character methods
        hp = char.get_attribute("HP")
        print(f"  ✅ get_attribute('HP'): {hp}")

        is_alive = char.is_alive()
        print(f"  ✅ is_alive(): {is_alive}")

        return 5, 0

    except Exception as e:
        print(f"  ❌ Character creation failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return 0, 1


def test_pytest_compatibility():
    """Test that our models work with pytest tests."""
    print(f"\n{YELLOW}Testing Pytest Compatibility...{RESET}")

    try:
        from xwe_v2.domain.character.models import Attribute, Character

        # Simulate test cases
        # Test 1: Character is alive with HP
        c1 = Character(name="TestHero", level=1, attributes=[Attribute("HP", 10)])
        assert c1.is_alive()
        print("  ✅ test_character_is_alive_with_hp")

        # Test 2: Character is dead when HP is zero
        c2 = Character(name="TestHero", level=1, attributes=[Attribute("HP", 0)])
        assert not c2.is_alive()
        print("  ✅ test_character_is_dead_when_hp_zero")

        # Test 3: Get attribute returns correct value
        c3 = Character(name="TestHero", level=1, attributes=[Attribute("MP", 25)])
        assert c3.get_attribute("MP") == 25
        print("  ✅ test_get_attribute_returns_correct_value")

        return 3, 0

    except Exception as e:
        print(f"  ❌ Pytest compatibility test failed: {str(e)}")
        return 0, 1


def test_game_service():
    """Test the game service."""
    print(f"\n{YELLOW}Testing Game Service...{RESET}")

    try:
        from xwe_v2.application.services.game_service import GameService

        # Create service
        service = GameService()
        print("  ✅ GameService created")

        # Create character
        char = service.create_character("测试玩家", level=1, is_player=True)
        print(f"  ✅ Character created: {char.name}")

        # Get player
        player = service.get_player()
        assert player is not None
        assert player.name == "测试玩家"
        print("  ✅ Get player works")

        # Process command
        result = service.process_command("status", [])
        assert result["success"]
        print(f"  ✅ Process command works: {result['message']}")

        return 4, 0

    except Exception as e:
        print(f"  ❌ Game service test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return 0, 1


def verify_directory_structure():
    """Verify v2 directory structure."""
    print(f"\n{YELLOW}Verifying Directory Structure...{RESET}")

    v2_root = project_root / "xwe_v2"
    required_files = [
        "domain/__init__.py",
        "domain/character/__init__.py",
        "domain/character/models.py",
        "domain/character/attributes.py",
        "domain/combat/__init__.py",
        "domain/combat/models.py",
        "domain/skills/__init__.py",
        "domain/skills/models.py",
        "application/__init__.py",
        "application/services/__init__.py",
        "application/services/game_service.py",
        "application/events/__init__.py",
        "infrastructure/__init__.py",
        "infrastructure/persistence/__init__.py",
        "infrastructure/persistence/data_manager.py",
        "config.py",
        "compatibility.py",
    ]

    passed = 0
    failed = 0

    for file_path in required_files:
        full_path = v2_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
            passed += 1
        else:
            print(f"  ❌ {file_path} (missing)")
            failed += 1

    return passed, failed


def main():
    """Run all verification tests."""
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}XWE V2 Setup Verification{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")

    total_passed = 0
    total_failed = 0

    # Run all tests
    tests = [
        verify_directory_structure,
        test_basic_imports,
        test_character_creation,
        test_pytest_compatibility,
        test_game_service,
    ]

    for test_func in tests:
        passed, failed = test_func()
        total_passed += passed
        total_failed += failed

    # Summary
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}Summary{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"Total tests passed: {GREEN}{total_passed}{RESET}")
    print(f"Total tests failed: {RED}{total_failed}{RESET}")

    if total_failed == 0:
        print(f"\n{GREEN}✅ All verifications passed! V2 is ready to use.{RESET}")
        print(f"\nYou can now:")
        print(f"1. Run pytest: pytest tests/v2/")
        print(f"2. Run migration: python scripts/migrate_to_v2.py")
        print(f"3. Use v2 modules in your code")
    else:
        print(f"\n{RED}❌ Some verifications failed. Please check the errors above.{RESET}")

    return total_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
