"""
随机玩家面板
生成随机角色属性
"""

import random
from typing import Dict, Any

class RandomPlayerPanel:
    """随机玩家面板生成器"""
    
    def __init__(self, game_mode: str = "player"):
        self.game_mode = game_mode
        self.attribute_ranges = {
            "constitution": (1, 10),  # 根骨
            "comprehension": (1, 10), # 悟性
            "spirit": (1, 10),        # 神识
            "luck": (1, 10)           # 机缘
        }
    
    def generate_random_attributes(self) -> Dict[str, int]:
        """生成随机属性"""
        total_points = 20  # 总点数
        attributes = {}
        
        # 随机分配点数
        remaining = total_points
        for attr in list(self.attribute_ranges.keys())[:-1]:
            min_val, max_val = self.attribute_ranges[attr]
            # 确保不超过剩余点数
            max_possible = min(max_val, remaining - (len(self.attribute_ranges) - len(attributes) - 1))
            value = random.randint(min_val, max_possible)
            attributes[attr] = value
            remaining -= value
        
        # 最后一个属性获得剩余点数
        last_attr = list(self.attribute_ranges.keys())[-1]
        attributes[last_attr] = max(1, min(10, remaining))
        
        return attributes
    
    def sanitize_attributes(self, attributes: Dict[str, Any]) -> Dict[str, int]:
        """清理和验证属性值"""
        sanitized = {}
        for attr, (min_val, max_val) in self.attribute_ranges.items():
            value = attributes.get(attr, min_val)
            try:
                value = int(value)
                value = max(min_val, min(max_val, value))
            except Exception:
                value = min_val
            sanitized[attr] = value
        return sanitized

__all__ = ["RandomPlayerPanel"]
