"""
XWE V2 Item System

Extended domain models for different types of items.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from xwe_v2.domain.inventory.models import Item


class EquipmentSlot(Enum):
    """Equipment slot types."""

    WEAPON = "weapon"
    HELMET = "helmet"
    ARMOR = "armor"
    GLOVES = "gloves"
    BOOTS = "boots"
    RING = "ring"
    NECKLACE = "necklace"
    TALISMAN = "talisman"


class ConsumableType(Enum):
    """Types of consumable items."""

    HEALING = "healing"
    MANA = "mana"
    BUFF = "buff"
    CULTIVATION = "cultivation"
    SKILL = "skill"
    SPECIAL = "special"


@dataclass
class Equipment(Item):
    """Equipment items that can be worn."""

    slot: EquipmentSlot = EquipmentSlot.WEAPON
    level_requirement: int = 1
    stat_bonuses: Dict[str, int] = field(default_factory=dict)
    special_effects: List[str] = field(default_factory=list)
    durability_current: int = 100
    durability_max: int = 100
    enhancement_level: int = 0

    def __post_init__(self):
        self.item_type = "equipment"
        self.max_stack = 1  # Equipment doesn't stack

    def repair(self, amount: int) -> None:
        """Repair the equipment."""
        self.durability_current = min(self.durability_current + amount, self.durability_max)

    def enhance(self) -> bool:
        """Attempt to enhance the equipment."""
        if self.enhancement_level >= 10:
            return False

        # Success rate decreases with level
        import random

        success_rate = 1.0 - (self.enhancement_level * 0.1)

        if random.random() < success_rate:
            self.enhancement_level += 1
            # Increase stats
            for stat in self.stat_bonuses:
                self.stat_bonuses[stat] = int(self.stat_bonuses[stat] * 1.1)
            return True

        return False


@dataclass
class Consumable(Item):
    """Consumable items with one-time effects."""

    consumable_type: ConsumableType = ConsumableType.HEALING
    effect_value: int = 0
    effect_duration: int = 0
    cooldown: int = 0
    level_requirement: int = 1

    def __post_init__(self):
        self.item_type = "consumable"

    def get_effect_description(self) -> str:
        """Get human-readable effect description."""
        if self.consumable_type == ConsumableType.HEALING:
            return f"恢复 {self.effect_value} 点生命值"
        elif self.consumable_type == ConsumableType.MANA:
            return f"恢复 {self.effect_value} 点法力值"
        elif self.consumable_type == ConsumableType.BUFF:
            return f"获得增益效果，持续 {self.effect_duration} 秒"
        elif self.consumable_type == ConsumableType.CULTIVATION:
            return f"增加 {self.effect_value} 点修为"
        else:
            return self.description


@dataclass
class Material(Item):
    """Crafting materials and resources."""

    material_type: str = "ore"  # ore, herb, essence, etc.
    grade: int = 1  # 1-10, higher is better
    elemental_affinity: Optional[str] = None

    def __post_init__(self):
        self.item_type = "material"


@dataclass
class QuestItem(Item):
    """Special items for quests."""

    quest_id: str = ""
    is_key_item: bool = False

    def __post_init__(self):
        self.item_type = "quest"
        self.max_stack = 1 if self.is_key_item else 99


@dataclass
class Talisman(Equipment):
    """Special talismans with magical properties."""

    charges_current: int = 10
    charges_max: int = 10
    spell_id: Optional[str] = None
    activation_cost: Dict[str, int] = field(default_factory=dict)  # resource -> amount

    def __post_init__(self):
        super().__post_init__()
        self.slot = EquipmentSlot.TALISMAN
        self.item_type = "talisman"

    def use_charge(self) -> bool:
        """Use one charge of the talisman."""
        if self.charges_current <= 0:
            return False

        self.charges_current -= 1
        return True

    def recharge(self, amount: int = 1) -> None:
        """Recharge the talisman."""
        self.charges_current = min(self.charges_current + amount, self.charges_max)


class ItemFactory:
    """Factory for creating items from templates."""

    @staticmethod
    def create_item(item_data: Dict) -> Item:
        """Create appropriate item type from data."""
        item_type = item_data.get("item_type", "misc")

        if item_type == "equipment":
            slot = item_data.get("slot", "weapon")
            if isinstance(slot, str):
                slot = EquipmentSlot(slot)

            return Equipment(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data.get("description", ""),
                value=item_data.get("value", 0),
                rarity=item_data.get("rarity", "common"),
                slot=slot,
                level_requirement=item_data.get("level_requirement", 1),
                stat_bonuses=item_data.get("stat_bonuses", {}),
                special_effects=item_data.get("special_effects", []),
            )

        elif item_type == "consumable":
            return Consumable(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data.get("description", ""),
                value=item_data.get("value", 0),
                rarity=item_data.get("rarity", "common"),
                consumable_type=ConsumableType(item_data.get("consumable_type", "healing")),
                effect_value=item_data.get("effect_value", 0),
                effect_duration=item_data.get("effect_duration", 0),
                cooldown=item_data.get("cooldown", 0),
                level_requirement=item_data.get("level_requirement", 1),
            )

        elif item_type == "material":
            return Material(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data.get("description", ""),
                value=item_data.get("value", 0),
                rarity=item_data.get("rarity", "common"),
                material_type=item_data.get("material_type", "ore"),
                grade=item_data.get("grade", 1),
                elemental_affinity=item_data.get("elemental_affinity"),
            )

        elif item_type == "quest":
            return QuestItem(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data.get("description", ""),
                value=item_data.get("value", 0),
                rarity=item_data.get("rarity", "common"),
                quest_id=item_data.get("quest_id", ""),
                is_key_item=item_data.get("is_key_item", False),
            )

        elif item_type == "talisman":
            return Talisman(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data.get("description", ""),
                value=item_data.get("value", 0),
                rarity=item_data.get("rarity", "common"),
                level_requirement=item_data.get("level_requirement", 1),
                stat_bonuses=item_data.get("stat_bonuses", {}),
                special_effects=item_data.get("special_effects", []),
                charges_max=item_data.get("charges_max", 10),
                charges_current=item_data.get("charges_current", 10),
                spell_id=item_data.get("spell_id"),
                activation_cost=item_data.get("activation_cost", {}),
            )

        else:
            # Default to base Item
            return Item(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data.get("description", ""),
                stack_size=item_data.get("stack_size", 1),
                max_stack=item_data.get("max_stack", 99),
                value=item_data.get("value", 0),
                rarity=item_data.get("rarity", "common"),
                item_type=item_type,
            )
