# core/attributes.py
"""
属性系统模块

管理角色的各种属性，包括基础属性、衍生属性和战斗属性。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

from ..engine.expression import ExpressionParser

logger = logging.getLogger(__name__)


class AttributeType(Enum):
    """属性类型枚举"""

    # 基础属性
    STRENGTH = "strength"  # 力量
    CONSTITUTION = "constitution"  # 体质
    AGILITY = "agility"  # 敏捷
    INTELLIGENCE = "intelligence"  # 智力
    WILLPOWER = "willpower"  # 意志
    COMPREHENSION = "comprehension"  # 悟性
    LUCK = "luck"  # 福缘

    # 修炼属性
    SPIRITUAL_ROOT_PURITY = "spiritual_root_purity"  # 灵根纯度
    CULTIVATION_LEVEL = "cultivation_level"  # 修为等级
    REALM_LEVEL = "realm_level"  # 境界等级

    # 战斗属性
    MAX_HEALTH = "max_health"  # 最大生命
    CURRENT_HEALTH = "current_health"  # 当前生命
    MAX_MANA = "max_mana"  # 最大灵力
    CURRENT_MANA = "current_mana"  # 当前灵力
    MAX_STAMINA = "max_stamina"  # 最大体力
    CURRENT_STAMINA = "current_stamina"  # 当前体力

    ATTACK_POWER = "attack_power"  # 攻击力
    SPELL_POWER = "spell_power"  # 法术威力
    DEFENSE = "defense"  # 防御力
    MAGIC_RESISTANCE = "magic_resistance"  # 法术抗性
    SPEED = "speed"  # 速度

    ACCURACY = "accuracy"  # 命中
    EVASION = "evasion"  # 闪避
    CRITICAL_RATE = "critical_rate"  # 暴击率
    CRITICAL_DAMAGE = "critical_damage"  # 暴击伤害


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
    spiritual_root_purity: float = 50  # 灵根纯度 0-100
    cultivation_level: int = 1  # 修为等级
    max_cultivation: int = 100  # 升级所需修炼值
    realm_level: int = 1  # 境界等级
    realm_name: str = "聚气期"  # 境界名称

    # 资源属性（当前值/最大值）
    current_health: float = 100
    max_health: float = 100
    current_mana: float = 100
    max_mana: float = 100
    current_stamina: float = 100
    max_stamina: float = 100

    # 战斗及衍生属性（初始化为0，由 ``calculate_derived_attributes`` 填充）
    attack_power: float = 0
    spell_power: float = 0
    defense: float = 0
    magic_resistance: float = 0
    speed: float = 0
    accuracy: float = 0
    evasion: float = 0
    critical_rate: float = 0
    critical_damage: float = 0

    # 额外属性字典（用于存储临时加成等）
    extra_attributes: Dict[str, float] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        """Fallback to ``extra_attributes`` when attribute is missing."""
        extra = self.__dict__.get("extra_attributes", {})
        if name in extra:
            return extra[name]

        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            raise AttributeError(
                f"{self.__class__.__name__} object has no attribute '{name}'"
            ) from e

    def __setattr__(self, name: str, value: Any):
        annotations = self.__class__.__dict__.get("__annotations__", {})
        if name in annotations or name == "extra_attributes":
            super().__setattr__(name, value)
        else:
            extra = self.__dict__.setdefault("extra_attributes", {})
            extra[name] = value

    def __post_init__(self):
        """初始化后计算衍生属性"""
        self.calculate_derived_attributes()

    def get(self, attr_name: str, default: float = 0.0) -> float:
        """
        获取属性值

        Args:
            attr_name: 属性名称

        Returns:
            属性值
        """
        # 先检查是否是直接属性
        if hasattr(self, attr_name):
            return getattr(self, attr_name)

        # 检查额外属性
        if attr_name in self.extra_attributes:
            return self.extra_attributes[attr_name]

        # 返回默认值
        return default

    def set(self, attr_name: str, value: float):
        """
        设置属性值

        Args:
            attr_name: 属性名称
            value: 属性值
        """
        if hasattr(self, attr_name):
            setattr(self, attr_name, value)
        else:
            self.extra_attributes[attr_name] = value

    def modify(self, attr_name: str, delta: float):
        """
        修改属性值

        Args:
            attr_name: 属性名称
            delta: 变化量
        """
        current = self.get(attr_name)
        self.set(attr_name, current + delta)

    def calculate_derived_attributes(self):
        """计算衍生属性"""
        # 最大气血值 = 体质 * 10 + 等级 * 20
        self.max_health = self.constitution * 10 + self.cultivation_level * 20

        # 最大灵力值 = 智力 * 8 + 灵根纯度 * 2
        self.max_mana = self.intelligence * 8 + self.spiritual_root_purity * 2

        # 最大体力值 = 体质 * 5 + 力量 * 3
        self.max_stamina = self.constitution * 5 + self.strength * 3

        # 基础攻击力
        self.attack_power = self.strength * 2 + self.cultivation_level * 5

        # 基础法术威力
        self.spell_power = (
            self.intelligence * 2
            + self.spiritual_root_purity * 0.5
            + self.cultivation_level * 3
        )

        # 基础防御力
        self.defense = self.constitution * 1.5 + self.cultivation_level * 2

        # 基础法术抗性
        self.magic_resistance = self.willpower * 2

        # 速度
        self.speed = self.agility * 1.5

        # 命中率
        self.accuracy = 80 + self.agility * 0.5

        # 闪避率
        self.evasion = self.agility * 0.8

        # 暴击率
        self.critical_rate = 5 + self.luck * 0.2

        # 暴击伤害
        self.critical_damage = 150 + self.strength * 0.5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            # 基础属性
            "strength": self.strength,
            "constitution": self.constitution,
            "agility": self.agility,
            "intelligence": self.intelligence,
            "willpower": self.willpower,
            "comprehension": self.comprehension,
            "luck": self.luck,
            # 修炼属性
            "spiritual_root_purity": self.spiritual_root_purity,
            "cultivation_level": self.cultivation_level,
            "max_cultivation": self.max_cultivation,
            "realm_level": self.realm_level,
            "realm_name": self.realm_name,
            # 资源属性
            "current_health": self.current_health,
            "max_health": self.max_health,
            "current_mana": self.current_mana,
            "max_mana": self.max_mana,
            "current_stamina": self.current_stamina,
            "max_stamina": self.max_stamina,
            "attack_power": self.attack_power,
            "spell_power": self.spell_power,
            "defense": self.defense,
            "magic_resistance": self.magic_resistance,
            "speed": self.speed,
            "accuracy": self.accuracy,
            "evasion": self.evasion,
            "critical_rate": self.critical_rate,
            "critical_damage": self.critical_damage,
        }

        # 添加额外属性
        result.update(self.extra_attributes)

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterAttributes":
        """从字典创建属性对象"""
        # 提取基础属性
        basic_attrs = {
            "strength": data.get("strength", 10),
            "constitution": data.get("constitution", 10),
            "agility": data.get("agility", 10),
            "intelligence": data.get("intelligence", 10),
            "willpower": data.get("willpower", 10),
            "comprehension": data.get("comprehension", 10),
            "luck": data.get("luck", 10),
            "spiritual_root_purity": data.get("spiritual_root_purity", 50),
            "cultivation_level": data.get("cultivation_level", 1),
            "max_cultivation": data.get("max_cultivation", 100),
            "realm_level": data.get("realm_level", 1),
            "realm_name": data.get("realm_name", "聚气期"),
            "current_health": data.get("current_health", 100),
            "max_health": data.get("max_health", 100),
            "current_mana": data.get("current_mana", 100),
            "max_mana": data.get("max_mana", 100),
            "current_stamina": data.get("current_stamina", 100),
            "max_stamina": data.get("max_stamina", 100),
            "attack_power": data.get("attack_power", 0),
            "spell_power": data.get("spell_power", 0),
            "defense": data.get("defense", 0),
            "magic_resistance": data.get("magic_resistance", 0),
            "speed": data.get("speed", 0),
            "accuracy": data.get("accuracy", 0),
            "evasion": data.get("evasion", 0),
            "critical_rate": data.get("critical_rate", 0),
            "critical_damage": data.get("critical_damage", 0),
        }

        # 创建对象
        attrs = cls(**basic_attrs)

        # 添加额外属性
        for key, value in data.items():
            if key not in basic_attrs:
                attrs.extra_attributes[key] = value

        return attrs


class AttributeSystem:
    """
    属性系统管理器

    负责属性的计算、修改和验证。
    """

    def __init__(self, expression_parser: ExpressionParser):
        """
        初始化属性系统

        Args:
            expression_parser: 表达式解析器
        """
        self.parser = expression_parser
        self.modifiers: Dict[str, List[Dict[str, Any]]] = {}

    def calculate_final_attribute(
        self, character_attrs: CharacterAttributes, attr_name: str
    ) -> float:
        """
        计算最终属性值（包含所有加成）

        Args:
            character_attrs: 角色属性
            attr_name: 属性名称

        Returns:
            最终属性值
        """
        base_value = character_attrs.get(attr_name)

        # 应用修饰器
        if attr_name in self.modifiers:
            for modifier in self.modifiers[attr_name]:
                if modifier["type"] == "add":
                    base_value += modifier["value"]
                elif modifier["type"] == "multiply":
                    base_value *= modifier["value"]
                elif modifier["type"] == "formula":
                    # 使用表达式计算
                    context = character_attrs.to_dict()
                    base_value = self.parser.evaluate(modifier["formula"], context)

        return base_value

    def add_modifier(self, attr_name: str, modifier: Dict[str, Any]):
        """
        添加属性修饰器

        Args:
            attr_name: 属性名称
            modifier: 修饰器配置
        """
        if attr_name not in self.modifiers:
            self.modifiers[attr_name] = []

        self.modifiers[attr_name].append(modifier)

    def remove_modifier(self, attr_name: str, modifier_id: str):
        """
        移除属性修饰器

        Args:
            attr_name: 属性名称
            modifier_id: 修饰器ID
        """
        if attr_name in self.modifiers:
            self.modifiers[attr_name] = [
                m for m in self.modifiers[attr_name] if m.get("id") != modifier_id
            ]

    def clear_modifiers(self, attr_name: Optional[str] = None):
        """
        清空修饰器

        Args:
            attr_name: 属性名称，为None时清空所有
        """
        if attr_name:
            self.modifiers.pop(attr_name, None)
        else:
            self.modifiers.clear()
