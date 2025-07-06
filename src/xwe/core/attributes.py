"""
属性系统
管理角色的基础属性和衍生属性
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import math


@dataclass
class CharacterAttributes:
    """角色属性类"""
    
    # 基础属性
    strength_base: int = 10
    strength_buff: float = 0
    constitution_base: int = 10
    constitution_buff: float = 0
    agility_base: int = 10
    agility_buff: float = 0
    intelligence_base: int = 10
    intelligence_buff: float = 0
    willpower_base: int = 10
    willpower_buff: float = 0
    comprehension_base: int = 10
    comprehension_buff: float = 0
    luck_base: int = 10
    luck_buff: float = 0
    
    # 修炼相关
    realm_name: str = "凡人"   # 境界名称
    realm_level_base: int = 0
    realm_level_buff: float = 0
    cultivation_level_base: int = 0
    cultivation_level_buff: float = 0
    cultivation_exp_base: int = 0
    cultivation_exp_buff: float = 0
    max_cultivation_base: int = 100
    max_cultivation_buff: float = 0
    realm_progress_base: float = 0
    realm_progress_buff: float = 0
    
    # 资源属性
    current_health_base: float = 100
    current_health_buff: float = 0
    max_health_base: float = 100
    max_health_buff: float = 0
    current_mana_base: float = 50
    current_mana_buff: float = 0
    max_mana_base: float = 50
    max_mana_buff: float = 0
    current_stamina_base: float = 100
    current_stamina_buff: float = 0
    max_stamina_base: float = 100
    max_stamina_buff: float = 0
    
    # 战斗属性
    attack_power_base: float = 10
    attack_power_buff: float = 0
    spell_power_base: float = 10
    spell_power_buff: float = 0
    defense_base: float = 5
    defense_buff: float = 0
    magic_resistance_base: float = 5
    magic_resistance_buff: float = 0
    speed_base: float = 10
    speed_buff: float = 0
    
    # 其他衍生属性
    critical_rate_base: float = 0.05
    critical_rate_buff: float = 0
    critical_damage_base: float = 1.5
    critical_damage_buff: float = 0
    dodge_rate_base: float = 0.05
    dodge_rate_buff: float = 0
    
    # 元素抗性
    elemental_resistance: Dict[str, float] = field(default_factory=lambda: {
        "fire": 0,
        "water": 0,
        "wood": 0,
        "metal": 0,
        "earth": 0
    })

    # ----- 属性访问器 -----
    @property
    def strength(self) -> float:
        return self.strength_base + self.strength_buff

    @strength.setter
    def strength(self, value: float) -> None:
        self.strength_base = value
        self.calculate_derived_attributes()

    @property
    def constitution(self) -> float:
        return self.constitution_base + self.constitution_buff

    @constitution.setter
    def constitution(self, value: float) -> None:
        self.constitution_base = value
        self.calculate_derived_attributes()

    @property
    def agility(self) -> float:
        return self.agility_base + self.agility_buff

    @agility.setter
    def agility(self, value: float) -> None:
        self.agility_base = value
        self.calculate_derived_attributes()

    @property
    def intelligence(self) -> float:
        return self.intelligence_base + self.intelligence_buff

    @intelligence.setter
    def intelligence(self, value: float) -> None:
        self.intelligence_base = value
        self.calculate_derived_attributes()

    @property
    def willpower(self) -> float:
        return self.willpower_base + self.willpower_buff

    @willpower.setter
    def willpower(self, value: float) -> None:
        self.willpower_base = value
        self.calculate_derived_attributes()

    @property
    def comprehension(self) -> float:
        return self.comprehension_base + self.comprehension_buff

    @comprehension.setter
    def comprehension(self, value: float) -> None:
        self.comprehension_base = value
        self.calculate_derived_attributes()

    @property
    def luck(self) -> float:
        return self.luck_base + self.luck_buff

    @luck.setter
    def luck(self, value: float) -> None:
        self.luck_base = value
        self.calculate_derived_attributes()

    @property
    def realm_level(self) -> float:
        return self.realm_level_base + self.realm_level_buff

    @realm_level.setter
    def realm_level(self, value: float) -> None:
        self.realm_level_base = value
        self.calculate_derived_attributes()

    @property
    def cultivation_level(self) -> float:
        return self.cultivation_level_base + self.cultivation_level_buff

    @cultivation_level.setter
    def cultivation_level(self, value: float) -> None:
        self.cultivation_level_base = value
        self.calculate_derived_attributes()

    @property
    def cultivation_exp(self) -> float:
        return self.cultivation_exp_base + self.cultivation_exp_buff

    @cultivation_exp.setter
    def cultivation_exp(self, value: float) -> None:
        self.cultivation_exp_base = value

    @property
    def max_cultivation(self) -> float:
        return self.max_cultivation_base + self.max_cultivation_buff

    @max_cultivation.setter
    def max_cultivation(self, value: float) -> None:
        self.max_cultivation_base = value

    @property
    def realm_progress(self) -> float:
        return self.realm_progress_base + self.realm_progress_buff

    @realm_progress.setter
    def realm_progress(self, value: float) -> None:
        self.realm_progress_base = value

    @property
    def current_health(self) -> float:
        return self.current_health_base + self.current_health_buff

    @current_health.setter
    def current_health(self, value: float) -> None:
        self.current_health_base = value

    @property
    def max_health(self) -> float:
        return self.max_health_base + self.max_health_buff

    @max_health.setter
    def max_health(self, value: float) -> None:
        self.max_health_base = value

    @property
    def current_mana(self) -> float:
        return self.current_mana_base + self.current_mana_buff

    @current_mana.setter
    def current_mana(self, value: float) -> None:
        self.current_mana_base = value

    @property
    def max_mana(self) -> float:
        return self.max_mana_base + self.max_mana_buff

    @max_mana.setter
    def max_mana(self, value: float) -> None:
        self.max_mana_base = value

    @property
    def current_stamina(self) -> float:
        return self.current_stamina_base + self.current_stamina_buff

    @current_stamina.setter
    def current_stamina(self, value: float) -> None:
        self.current_stamina_base = value

    @property
    def max_stamina(self) -> float:
        return self.max_stamina_base + self.max_stamina_buff

    @max_stamina.setter
    def max_stamina(self, value: float) -> None:
        self.max_stamina_base = value

    @property
    def attack_power(self) -> float:
        return self.attack_power_base + self.attack_power_buff

    @attack_power.setter
    def attack_power(self, value: float) -> None:
        self.attack_power_base = value

    @property
    def spell_power(self) -> float:
        return self.spell_power_base + self.spell_power_buff

    @spell_power.setter
    def spell_power(self, value: float) -> None:
        self.spell_power_base = value

    @property
    def defense(self) -> float:
        return self.defense_base + self.defense_buff

    @defense.setter
    def defense(self, value: float) -> None:
        self.defense_base = value

    @property
    def magic_resistance(self) -> float:
        return self.magic_resistance_base + self.magic_resistance_buff

    @magic_resistance.setter
    def magic_resistance(self, value: float) -> None:
        self.magic_resistance_base = value

    @property
    def speed(self) -> float:
        return self.speed_base + self.speed_buff

    @speed.setter
    def speed(self, value: float) -> None:
        self.speed_base = value

    @property
    def critical_rate(self) -> float:
        return self.critical_rate_base + self.critical_rate_buff

    @critical_rate.setter
    def critical_rate(self, value: float) -> None:
        self.critical_rate_base = value

    @property
    def critical_damage(self) -> float:
        return self.critical_damage_base + self.critical_damage_buff

    @critical_damage.setter
    def critical_damage(self, value: float) -> None:
        self.critical_damage_base = value

    @property
    def dodge_rate(self) -> float:
        return self.dodge_rate_base + self.dodge_rate_buff

    @dodge_rate.setter
    def dodge_rate(self, value: float) -> None:
        self.dodge_rate_base = value
    
    def __post_init__(self):
        """初始化后计算衍生属性"""
        self.calculate_derived_attributes()
    
    def calculate_derived_attributes(self) -> None:
        """计算衍生属性"""
        # 生命值 = 体质 * 10 + 力量 * 5 + 等级 * 20
        self.max_health = self.constitution * 10 + self.strength * 5 + self.cultivation_level * 20
        
        # 灵力 = 智力 * 10 + 意志 * 5 + 等级 * 10
        self.max_mana = self.intelligence * 10 + self.willpower * 5 + self.cultivation_level * 10
        
        # 体力 = 体质 * 5 + 力量 * 3 + 等级 * 5
        self.max_stamina = self.constitution * 5 + self.strength * 3 + self.cultivation_level * 5
        
        # 攻击力 = 力量 * 2 + 敏捷 * 0.5 + 等级 * 3
        self.attack_power = self.strength * 2 + self.agility * 0.5 + self.cultivation_level * 3
        
        # 法术威力 = 智力 * 2 + 意志 * 0.5 + 等级 * 3
        self.spell_power = self.intelligence * 2 + self.willpower * 0.5 + self.cultivation_level * 3
        
        # 防御 = 体质 * 1.5 + 力量 * 0.5 + 等级 * 2
        self.defense = self.constitution * 1.5 + self.strength * 0.5 + self.cultivation_level * 2
        
        # 法术抗性 = 意志 * 1.5 + 智力 * 0.5 + 等级 * 2
        self.magic_resistance = self.willpower * 1.5 + self.intelligence * 0.5 + self.cultivation_level * 2
        
        # 速度 = 敏捷 * 1.5 + 等级
        self.speed = self.agility * 1.5 + self.cultivation_level
        
        # 暴击率 = 基础5% + 运气影响
        self.critical_rate = 0.05 + (self.luck - 10) * 0.005
        
        # 暴击伤害 = 基础150% + 力量影响
        self.critical_damage = 1.5 + (self.strength - 10) * 0.01
        
        # 闪避率 = 基础5% + 敏捷影响
        self.dodge_rate = 0.05 + (self.agility - 10) * 0.003
        
        # 限制数值范围
        self.critical_rate = max(0.01, min(0.5, self.critical_rate))
        self.dodge_rate = max(0.01, min(0.3, self.dodge_rate))
    
    def get(self, attr_name: str, default: Any = 0) -> Any:
        """获取属性值"""
        return getattr(self, attr_name, default)
    
    def set(self, attr_name: str, value: Any) -> None:
        """设置属性值"""
        if hasattr(self, attr_name):
            setattr(self, attr_name, value)
            # 重新计算衍生属性
            self.calculate_derived_attributes()
    
    def modify(self, attr_name: str, delta: float) -> None:
        """修改属性值"""
        current = self.get(attr_name, 0)
        self.set(attr_name, current + delta)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            # 基础属性
            "strength": self.strength,
            "constitution": self.constitution,
            "agility": self.agility,
            "intelligence": self.intelligence,
            "willpower": self.willpower,
            "comprehension": self.comprehension,
            "luck": self.luck,
            
            # 修炼相关
            "realm_name": self.realm_name,
            "realm_level": self.realm_level,
            "cultivation_level": self.cultivation_level,
            "cultivation_exp": self.cultivation_exp,
            
            # 资源
            "current_health": self.current_health,
            "max_health": self.max_health,
            "current_mana": self.current_mana,
            "max_mana": self.max_mana,
            "current_stamina": self.current_stamina,
            "max_stamina": self.max_stamina,
            
            # 战斗属性
            "attack_power": self.attack_power,
            "spell_power": self.spell_power,
            "defense": self.defense,
            "magic_resistance": self.magic_resistance,
            "speed": self.speed,
            
            # 其他
            "critical_rate": self.critical_rate,
            "critical_damage": self.critical_damage,
            "dodge_rate": self.dodge_rate,
            "elemental_resistance": self.elemental_resistance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterAttributes":
        """从字典创建"""
        attrs = cls()
        
        # 设置所有属性
        for key, value in data.items():
            if hasattr(attrs, key):
                setattr(attrs, key, value)
        
        # 重新计算衍生属性
        attrs.calculate_derived_attributes()
        
        return attrs


class AttributeSystem:
    """
    属性系统管理器
    
    处理属性计算、加成等
    """
    
    def __init__(self, expression_parser: Any = None):
        self.parser = expression_parser
        self.attribute_formulas = {
            "max_health": "constitution * 10 + strength * 5 + level * 20",
            "max_mana": "intelligence * 10 + willpower * 5 + level * 10",
            "attack_power": "strength * 2 + agility * 0.5 + level * 3",
            "defense": "constitution * 1.5 + strength * 0.5 + level * 2"
        }
    
    def calculate_attribute(self, formula: str, context: Dict[str, Any]) -> float:
        """
        根据公式计算属性值
        
        Args:
            formula: 计算公式
            context: 变量上下文
            
        Returns:
            计算结果
        """
        if self.parser:
            return self.parser.evaluate(formula, context)
        
        # 简单的备用计算
        try:
            # 使用eval的安全版本
            allowed_names = {
                k: v for k, v in context.items() 
                if isinstance(v, (int, float))
            }
            return eval(formula, {"__builtins__": {}}, allowed_names)
        except:
            return 0
    
    def apply_buff(self, attributes: CharacterAttributes,
                   buff_type: str, value: float, is_percentage: bool = False) -> None:
        """
        应用增益效果
        
        Args:
            attributes: 角色属性
            buff_type: 增益类型
            value: 增益值
            is_percentage: 是否是百分比加成
        """
        buff_attr = f"{buff_type}_buff"
        if hasattr(attributes, buff_attr):
            current = getattr(attributes, buff_attr)
            if is_percentage:
                delta = getattr(attributes, buff_type) * value / 100
                new_value = current + delta
            else:
                new_value = current + value
            setattr(attributes, buff_attr, new_value)
            # 基础属性变化可能影响衍生属性
            attributes.calculate_derived_attributes()
    
    def calculate_combat_power(self, attributes: CharacterAttributes) -> int:
        """计算战斗力"""
        # 简单的战斗力计算公式
        combat_power = (
            attributes.attack_power * 2 +
            attributes.defense * 1.5 +
            attributes.max_health * 0.1 +
            attributes.max_mana * 0.1 +
            attributes.speed * 1 +
            attributes.cultivation_level * 10
        )
        
        return int(combat_power)
