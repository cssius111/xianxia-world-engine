"""
物品系统 - 管理游戏中的物品、背包、交易等
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Item:
    """物品基础类"""
    id: str
    name: str
    description: str
    value: int = 0
    stackable: bool = True
    max_stack: int = 99


class ItemSystem:
    """物品系统管理器"""
    
    def __init__(self) -> None:
        self.items: Dict[str, Item] = {}
        self.player_inventories: Dict[str, Dict[str, int]] = {}
    
    def get_spirit_stones(self, player_id: str) -> int:
        """获取玩家的灵石数量"""
        inventory = self.player_inventories.get(player_id, {})
        # 兼容不同写法的灵石ID
        return inventory.get('spirit_stone', inventory.get('spirit_stones', 0))
    
    def add_item(self, player_id: str, item_id: str, quantity: int = 1) -> bool:
        """添加物品到玩家背包"""
        if player_id not in self.player_inventories:
            self.player_inventories[player_id] = {}
        
        current = self.player_inventories[player_id].get(item_id, 0)
        self.player_inventories[player_id][item_id] = current + quantity
        return True
    
    def remove_item(self, player_id: str, item_id: str, quantity: int = 1) -> bool:
        """从玩家背包移除物品"""
        inventory = self.player_inventories.get(player_id, {})
        if inventory.get(item_id, 0) >= quantity:
            inventory[item_id] -= quantity
            if inventory[item_id] <= 0:
                del inventory[item_id]
            return True
        return False


# 全局物品系统实例
item_system = ItemSystem()
