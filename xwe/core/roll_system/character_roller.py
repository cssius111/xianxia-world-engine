"""
角色 Roll 系统主模块

实现角色初始属性的随机生成，支持无限重骰。
"""

import json
import random
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from .roll_data import ROLL_DATA
from .roll_utils import (
    weighted_random_choice, 
    random_select_elements,
    random_attribute_value,
    generate_random_name,
    get_rarity_color,
    calculate_combat_power
)


@dataclass
class RollResult:
    """Roll结果数据类"""
    # 基础信息
    name: str
    gender: str
    identity: str
    identity_desc: str
    
    # 基础属性
    attributes: Dict[str, int]
    
    # 灵根
    spiritual_root_type: str
    spiritual_root_elements: List[str]
    spiritual_root_desc: str
    
    # 命格
    destiny: str
    destiny_desc: str
    destiny_rarity: str
    destiny_effects: Dict[str, Any]
    
    # 天赋
    talents: List[Dict[str, Any]]
    
    # 系统
    system: Optional[Dict[str, Any]]
    
    # 综合评价
    combat_power: int
    overall_rating: str
    
    # 特殊标记
    special_tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "基础信息": {
                "姓名": self.name,
                "性别": self.gender,
                "身份": self.identity,
                "身份说明": self.identity_desc
            },
            "属性面板": self.attributes,
            "灵根": {
                "类型": self.spiritual_root_type,
                "属性": self.spiritual_root_elements,
                "说明": self.spiritual_root_desc
            },
            "命格": {
                "名称": self.destiny,
                "稀有度": self.destiny_rarity,
                "说明": self.destiny_desc,
                "效果": self.destiny_effects
            },
            "天赋": self.talents,
            "系统": self.system,
            "综合评价": {
                "战斗力": self.combat_power,
                "总体评级": self.overall_rating,
                "特殊标签": self.special_tags
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    def display(self) -> str:
        """生成展示用的格式化文本"""
        lines = [
            "="*60,
            f"【角色面板】",
            "="*60,
            f"姓名：{self.name} ({self.gender})",
            f"身份：{self.identity} - {self.identity_desc}",
            "",
            "【基础属性】",
            f"攻击力：{self.attributes['attack']}  防御力：{self.attributes['defense']}",
            f"生命值：{self.attributes['health']}  法力值：{self.attributes['mana']}",
            f"速度：{self.attributes['speed']}    悟性：{self.attributes['comprehension']}",
            f"气运：{self.attributes['luck']}     根骨：{self.attributes['constitution']}",
            f"魅力：{self.attributes['charm']}",
            "",
            f"【灵根】{self.spiritual_root_type} - {'、'.join(self.spiritual_root_elements)}属性",
            f"说明：{self.spiritual_root_desc}",
            "",
            f"【命格】{self.destiny} ★{self.destiny_rarity}★",
            f"说明：{self.destiny_desc}",
        ]
        
        # 天赋部分
        lines.extend(["", "【天赋】"])
        for i, talent in enumerate(self.talents, 1):
            lines.append(f"{i}. {talent['name']} - {talent['description']}")
        
        # 系统部分
        if self.system:
            lines.extend([
                "",
                f"【系统】{self.system['name']} ★{self.system['rarity']}★",
                f"说明：{self.system['description']}",
                "功能："
            ])
            for feature in self.system['features']:
                lines.append(f"  • {feature}")
        
        # 综合评价
        lines.extend([
            "",
            "【综合评价】",
            f"战斗力评分：{self.combat_power}",
            f"总体评级：{self.overall_rating}",
        ])
        
        if self.special_tags:
            lines.append(f"特殊标签：{', '.join(self.special_tags)}")
        
        lines.append("="*60)
        
        return '\n'.join(lines)


class CharacterRoller:
    """角色Roll系统主类"""
    
    def __init__(self):
        self.data = ROLL_DATA
        self.roll_count = 0
    
    def roll(self) -> RollResult:
        """
        执行一次角色roll
        
        Returns:
            RollResult: roll结果
        """
        self.roll_count += 1
        
        # 生成基础信息
        gender = random.choice(['男', '女'])
        if gender == '男':
            name = generate_random_name(
                self.data['character_creation']['name_generation']['surnames'],
                self.data['character_creation']['name_generation']['male_names']
            )
        else:
            name = generate_random_name(
                self.data['character_creation']['name_generation']['surnames'],
                self.data['character_creation']['name_generation']['female_names']
            )
        
        # 生成身份
        identity_key, identity_data = weighted_random_choice(self.data['identities'])
        
        # 生成基础属性
        attributes = {}
        for attr_name, attr_config in self.data['base_attributes'].items():
            attributes[attr_name] = random_attribute_value(attr_config)
        
        # 生成灵根
        root_type_key, root_type_data = weighted_random_choice(
            self.data['spiritual_roots']['types']
        )
        root_elements = random_select_elements(
            self.data['spiritual_roots']['elements'],
            {"single": 1, "dual": 2, "triple": 3, "quad": 4, "penta": 5}[root_type_key]
        )
        
        # 生成命格
        destiny_key, destiny_data = weighted_random_choice(self.data['destinies'])
        
        # 应用命格对属性的影响
        for effect_key, effect_value in destiny_data.get('effects', {}).items():
            if effect_key in attributes and isinstance(effect_value, (int, float)):
                attributes[effect_key] = int(attributes[effect_key] + effect_value)
        
        # 生成天赋（1-3个）
        talent_count = random.choices([1, 2, 3], weights=[50, 40, 10], k=1)[0]
        selected_talents = []
        available_talents = list(self.data['talents'].items())
        
        for _ in range(min(talent_count, len(available_talents))):
            talent_key, talent_data = weighted_random_choice(
                dict(available_talents)
            )
            selected_talents.append({
                "name": talent_key,
                "category": talent_data['category'],
                "description": talent_data['description'],
                "effects": talent_data['effects']
            })
            # 移除已选天赋避免重复
            available_talents = [(k, v) for k, v in available_talents if k != talent_key]
        
        # 生成系统（30%概率）
        system_data = None
        if random.random() < 0.3:
            system_key, system_info = weighted_random_choice(self.data['systems'])
            system_data = {
                "name": system_key,
                "rarity": system_info['rarity'],
                "description": system_info['description'],
                "features": system_info['features'],
                "initial_bonus": system_info.get('initial_bonus', {})
            }
        
        # 计算战斗力和评级
        combat_power = calculate_combat_power(attributes)
        overall_rating = self._calculate_overall_rating(
            attributes, root_type_key, destiny_data.get('rarity', 'common'),
            len(selected_talents), system_data is not None
        )
        
        # 特殊标记
        special_tags = []
        if destiny_data.get('rarity') in ['epic', 'legendary']:
            special_tags.append("天命不凡")
        if root_type_key in ['single', 'dual']:
            special_tags.append("天赋异禀")
        if system_data:
            special_tags.append("系统加身")
        if combat_power > 500:
            special_tags.append("天生强者")
        
        # 创建结果
        result = RollResult(
            name=name,
            gender=gender,
            identity=identity_key,
            identity_desc=identity_data['description'],
            attributes=attributes,
            spiritual_root_type=root_type_data['name'],
            spiritual_root_elements=root_elements,
            spiritual_root_desc=root_type_data['description'],
            destiny=destiny_key,
            destiny_desc=destiny_data['description'],
            destiny_rarity=destiny_data.get('rarity', 'common'),
            destiny_effects=destiny_data.get('effects', {}),
            talents=selected_talents,
            system=system_data,
            combat_power=combat_power,
            overall_rating=overall_rating,
            special_tags=special_tags
        )
        
        return result
    
    def _calculate_overall_rating(self, attributes: Dict[str, int], 
                                 root_type: str, destiny_rarity: str,
                                 talent_count: int, has_system: bool) -> str:
        """计算总体评级"""
        score = 0
        
        # 属性评分
        for value in attributes.values():
            if value >= 8:
                score += 1
            if value >= 12:
                score += 1
        
        # 灵根评分
        root_scores = {"single": 5, "dual": 3, "triple": 1, "quad": 0, "penta": 0}
        score += root_scores.get(root_type, 0)
        
        # 命格评分
        rarity_scores = {"common": 0, "uncommon": 1, "rare": 3, "epic": 5, "legendary": 8}
        score += rarity_scores.get(destiny_rarity, 0)
        
        # 天赋评分
        score += talent_count * 2
        
        # 系统评分
        if has_system:
            score += 5
        
        # 评级判定
        if score >= 25:
            return "SSS级 - 万古无一"
        elif score >= 20:
            return "SS级 - 绝世天骄"
        elif score >= 15:
            return "S级 - 天之骄子"
        elif score >= 12:
            return "A级 - 天赋卓越"
        elif score >= 8:
            return "B级 - 资质优秀"
        elif score >= 5:
            return "C级 - 中等之姿"
        else:
            return "D级 - 资质平平"
    
    def multi_roll(self, count: int = 10) -> List[RollResult]:
        """
        批量roll
        
        Args:
            count: roll次数
            
        Returns:
            结果列表
        """
        results = []
        for _ in range(count):
            results.append(self.roll())
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取roll统计信息"""
        return {
            "total_rolls": self.roll_count,
            "session_start": "当前会话",
            "features": {
                "命格种类": len(self.data['destinies']),
                "天赋种类": len(self.data['talents']),
                "系统种类": len(self.data['systems']),
                "身份种类": len(self.data['identities'])
            }
        }
    
    def roll_character(self) -> RollResult:
        """别名方法，兼容旧版本脚本"""
        return self.roll()


# 便捷函数
def quick_roll() -> RollResult:
    """快速roll一次"""
    roller = CharacterRoller()
    return roller.roll()


def roll_until_satisfied(condition_func=None, max_attempts=1000):
    """
    持续roll直到满足条件
    
    Args:
        condition_func: 条件函数，接收RollResult返回bool
        max_attempts: 最大尝试次数
        
    Returns:
        满足条件的结果或None
    """
    roller = CharacterRoller()
    for _ in range(max_attempts):
        result = roller.roll()
        if condition_func is None or condition_func(result):
            return result
    return None
