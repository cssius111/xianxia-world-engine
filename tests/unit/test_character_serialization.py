import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xwe.core.character import Character, CharacterType


def test_character_serialization_roundtrip():
    char = Character(name="测试", character_type=CharacterType.PLAYER)
    char.attributes.strength = 15
    char.inventory.add("test_item", 3)
    char.lingshi["mid"] = 2

    data = char.to_dict()
    restored = Character.from_dict(data)

    assert restored.name == char.name
    assert restored.character_type == char.character_type
    assert restored.attributes.strength == 15
    assert restored.inventory.get_quantity("test_item") == 3
    assert restored.lingshi["mid"] == 2
