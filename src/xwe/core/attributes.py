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
    strength: int = 10          # 力量 - 影响物理攻击
    constitution: int = 10      # 体质 - 影响生命值和防御
    agility: int = 10          # 敏捷 - 影响速度和闪避
    intelligence: int = 10      # 智力 - 影响法术攻击和灵力
    willpower: int = 10        # 意志 - 影响法术防御和精神抗性
    comprehension: int = 10    # 悟性 - 影响学习和修炼速度
    luck: int = 10            # 运气 - 影响暴击和掉落
    
    # 修炼相关
    realm_name: str = "凡人"   # 境界名称
    realm_level: int = 0       # 境界等级
    cultivation_level: int = 0  # 总等级
    cultivation_exp: int = 0    # 修炼经验
    max_cultivation: int = 100  # 最大修为值
    realm_progress: float = 0   # 境界进度
    
    # 资源属性
    current_health: float = 100
    max_health: float = 100
    current_mana: float = 50
    max_mana: float = 50
    current_stamina: float = 100
    max_stamina: float = 100
    
    # 战斗属性
    attack_power: float = 10
    spell_power: float = 10
    defense: float = 5
    magic_resistance: float = 5
    speed: float = 10
    
    # 其他衍生属性
    critical_rate: float = 0.05
    critical_damage: float = 1.5
    dodge_rate: float = 0.05
    
    # 元素抗性
    elemental_resistance: Dict[str, float] = field(default_factory=lambda: {
        "fire": 0,
        "water": 0,
        "wood": 0,
        "metal": 0,
        "earth": 0
    })
    
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
        if hasattr(attributes, buff_type):
            current = getattr(attributes, buff_type)
            if is_percentage:
                new_value = current * (1 + value / 100)
            else:
                new_value = current + value
            setattr(attributes, buff_type, new_value)
    
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
