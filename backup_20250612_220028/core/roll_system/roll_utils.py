"""
Roll 系统工具函数

提供权重随机选择等辅助功能。
"""

import random
from typing import Any, Dict, List, Tuple


def weighted_random_choice(items_with_weights: Dict[str, Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
    """
    根据权重随机选择一个项目
    
    Args:
        items_with_weights: 字典，key为项目ID，value包含'weight'字段
        
    Returns:
        (selected_key, selected_value): 选中的项目
    """
    items = list(items_with_weights.items())
    weights = [item[1].get('weight', 1) for item in items]
    
    selected = random.choices(items, weights=weights, k=1)[0]
    return selected


def random_select_elements(elements: List[str], count: int) -> List[str]:
    """
    从列表中随机选择指定数量的不重复元素
    
    Args:
        elements: 元素列表
        count: 选择数量
        
    Returns:
        选中的元素列表
    """
    count = min(count, len(elements))
    return random.sample(elements, count)


def random_attribute_value(attr_config: Dict[str, Any]) -> int:
    """
    根据配置生成随机属性值
    
    Args:
        attr_config: 包含'min'和'max'的配置字典
        
    Returns:
        随机属性值
    """
    return random.randint(attr_config['min'], attr_config['max'])


def calculate_attribute_modifier(base_value: int, effects: Dict[str, Any]) -> int:
    """
    计算属性修正值
    
    Args:
        base_value: 基础值
        effects: 效果字典，可能包含加值或乘值
        
    Returns:
        修正后的值
    """
    # 先应用加值
    if isinstance(effects.get(base_value, 0), (int, float)):
        base_value += effects.get(base_value, 0)
    
    # 再应用乘值
    multiplier = effects.get(f"{base_value}_multiplier", 1.0)
    
    return int(base_value * multiplier)


def format_description(template: str, **kwargs) -> str:
    """
    格式化描述文本
    
    Args:
        template: 模板字符串
        **kwargs: 替换参数
        
    Returns:
        格式化后的字符串
    """
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def generate_random_name(surname_list: List[str], name_list: List[str]) -> str:
    """
    生成随机姓名
    
    Args:
        surname_list: 姓氏列表
        name_list: 名字列表
        
    Returns:
        完整姓名
    """
    surname = random.choice(surname_list)
    name_chars = random.sample(name_list, random.randint(1, 2))
    return surname + ''.join(name_chars)


def get_rarity_color(rarity: str) -> str:
    """
    根据稀有度返回对应的颜色标识
    
    Args:
        rarity: 稀有度等级
        
    Returns:
        颜色名称或代码
    """
    rarity_colors = {
        "common": "white",
        "uncommon": "green", 
        "rare": "blue",
        "epic": "purple",
        "legendary": "orange",
        "mythic": "red"
    }
    return rarity_colors.get(rarity, "white")


def calculate_combat_power(attributes: Dict[str, int]) -> int:
    """
    计算战斗力评分
    
    Args:
        attributes: 属性字典
        
    Returns:
        战斗力数值
    """
    # 简单的战斗力计算公式
    power = 0
    power += attributes.get('attack', 0) * 10
    power += attributes.get('defense', 0) * 8
    power += attributes.get('health', 0) * 1
    power += attributes.get('mana', 0) * 2
    power += attributes.get('speed', 0) * 5
    
    return power
