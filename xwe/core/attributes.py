from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import logging

from ..engine.expression import ExpressionParser

logger = logging.getLogger(__name__)


class AttributeType(Enum):
    """属性类型枚举"""

    # 基础属性
    STRENGTH = "strength"
    CONSTITUTION = "constitution"
    AGILITY = "agility"
    INTELLIGENCE = "intelligence"
    WILLPOWER = "willpower"
    COMPREHENSION = "comprehension"
    LUCK = "luck"

    # 修炼属性
    SPIRITUAL_ROOT_PURITY = "spiritual_root_purity"
    CULTIVATION_LEVEL = "cultivation_level"
    REALM_LEVEL = "realm_level"

    # 战斗属性
    MAX_HEALTH = "max_health"
    CURRENT_HEALTH = "current_health"
    MAX_MANA = "max_mana"
    CURRENT_MANA = "current_mana"
    MAX_STAMINA = "max_stamina"
    CURRENT_STAMINA = "current_stamina"

    ATTACK_POWER = "attack_power"
    SPELL_POWER = "spell_power"
    DEFENSE = "defense"
    MAGIC_RESISTANCE = "magic_resistance"
    SPEED = "speed"
    ACCURACY = "accuracy"
    EVASION = "evasion"
    CRITICAL_RATE = "critical_rate"
    CRITICAL_DAMAGE = "critical_damage"


@dataclass
class CharacterAttributes:
    """
    角色属性集合

    管理角色的所有属性值和计算衍生属性。
    """
    # 基础属性
    strength: float = 10
    constitution: float = 10
    agility: float = 10
    intelligence: float = 10
    willpower: float = 10
    comprehension: float = 10
    luck: float = 10

    # 修炼属性
    spiritual_root_purity: float = 50
    cultivation_level: int = 1
    max_cultivation: int = 100
    realm_level: int = 1
    realm_name: str = "聚气期"

    # 资源属性
    current_health: float = 100
    max_health: float = 100
    current_mana: float = 100
    max_mana: float = 100
    current_stamina: float = 100
    max_stamina: float = 100

    # 战斗及衍生属性
    attack_power: float = 0
    spell_power: float = 0
    defense: float = 0
    magic_resistance: float = 0
    speed: float = 0
    accuracy: float = 0
    evasion: float = 0
    critical_rate: float = 0
    critical_damage: float = 0

    # 附加属性
    extra_attributes: Dict[str, float] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        extra = self.extra_attributes
        if name in extra:
            return extra[name]
        raise AttributeError(f"{self.__class__.__name__} object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute and mirror the value to ``extra_attributes``.

        During dataclass initialization ``extra_attributes`` may not yet
        exist, so updates are skipped until it is created. Once available,
        all assignments are also stored in the dictionary for unified
        access by tests and other systems.
        """
        annotations = self.__class__.__dict__.get("__annotations__", {})
        has_extra = "extra_attributes" in self.__dict__

        if name in annotations or name == "extra_attributes":
            super().__setattr__(name, value)
            if name != "extra_attributes" and has_extra:
                self.extra_attributes[name] = value
        else:
            if has_extra:
                self.extra_attributes[name] = value
            else:
                # Fallback during early __init__ before ``extra_attributes``
                super().__setattr__(name, value)

    def __post_init__(self) -> None:
        self.calculate_derived_attributes()

    def get(self, attr_name: str, default: float = 0.0) -> float:
        if hasattr(self, attr_name):
            return getattr(self, attr_name)
        return self.extra_attributes.get(attr_name, default)

    def set(self, attr_name: str, value: float) -> None:
        if hasattr(self, attr_name):
            setattr(self, attr_name, value)
        else:
            self.extra_attributes[attr_name] = value

    def modify(self, attr_name: str, delta: float) -> None:
        current = self.get(attr_name)
        self.set(attr_name, current + delta)

    def calculate_derived_attributes(self) -> None:
        self.max_health = self.constitution * 10 + self.cultivation_level * 20
        self.max_mana = self.intelligence * 8 + self.spiritual_root_purity * 2
        self.max_stamina = self.constitution * 5 + self.strength * 3
        self.attack_power = self.strength * 2 + self.cultivation_level * 5
        self.spell_power = self.intelligence * 2 + self.spiritual_root_purity * 0.5 + self.cultivation_level * 3
        self.defense = self.constitution * 1.5 + self.cultivation_level * 2
        self.magic_resistance = self.willpower * 2
        self.speed = self.agility * 1.5
        self.accuracy = 80 + self.agility * 0.5
        self.evasion = self.agility * 0.8
        self.critical_rate = 5 + self.luck * 0.2
        self.critical_damage = 150 + self.strength * 0.5

    def to_dict(self) -> Dict[str, Any]:
        result = {field: getattr(self, field) for field in self.__annotations__ if field != "extra_attributes"}
        result.update(self.extra_attributes)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterAttributes":
        known_fields = cls.__annotations__.keys()
        init_data = {k: data[k] for k in known_fields if k in data}
        obj = cls(**init_data)
        for k, v in data.items():
            if k not in known_fields:
                obj.extra_attributes[k] = v
        return obj


class AttributeSystem:
    def __init__(self, expression_parser: ExpressionParser):
        self.parser = expression_parser
        self.modifiers: Dict[str, List[Dict[str, Any]]] = {}

    def calculate_final_attribute(self, character_attrs: CharacterAttributes, attr_name: str) -> float:
        base_value = character_attrs.get(attr_name)
        if attr_name in self.modifiers:
            for modifier in self.modifiers[attr_name]:
                if modifier["type"] == "add":
                    base_value += modifier["value"]
                elif modifier["type"] == "multiply":
                    base_value *= modifier["value"]
                elif modifier["type"] == "formula":
                    context = character_attrs.to_dict()
                    base_value = self.parser.evaluate(modifier["formula"], context)
        return base_value

    def add_modifier(self, attr_name: str, modifier: Dict[str, Any]) -> None:
        if attr_name not in self.modifiers:
            self.modifiers[attr_name] = []
        self.modifiers[attr_name].append(modifier)

    def remove_modifier(self, attr_name: str, modifier_id: str) -> None:
        if attr_name in self.modifiers:
            self.modifiers[attr_name] = [m for m in self.modifiers[attr_name] if m.get("id") != modifier_id]

    def clear_modifiers(self, attr_name: Optional[str] = None) -> None:
        if attr_name:
            self.modifiers.pop(attr_name, None)
        else:
            self.modifiers.clear()
