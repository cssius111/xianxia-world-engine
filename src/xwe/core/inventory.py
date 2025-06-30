"""
物品栏系统
管理角色的物品存储
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Item:
    """物品基类"""
    id: str
    name: str
    description: str
    stack_size: int = 99
    item_type: str = "misc"
    rarity: str = "common"
    value: int = 0
    
    def __hash__(self):
        return hash(self.id)


class Inventory:
    """
    物品栏类
    
    管理角色的物品存储和操作
    """
    
    def __init__(self, capacity: int = 50):
        """
        初始化物品栏
        
        Args:
            capacity: 物品栏容量
        """
        self.capacity = capacity
        self.items: Dict[str, int] = {}  # item_id -> quantity
        self.gold: int = 0  # 金币
        
    def add(self, item_id: str, quantity: int = 1) -> bool:
        """
        添加物品
        
        Args:
            item_id: 物品ID
            quantity: 数量
            
        Returns:
            是否成功添加
        """
        if quantity <= 0:
            return False
            
        # 检查容量（简化处理，每种物品占一个格子）
        if item_id not in self.items and len(self.items) >= self.capacity:
            logger.warning(f"物品栏已满，无法添加 {item_id}")
            return False
            
        # 添加物品
        current = self.items.get(item_id, 0)
        self.items[item_id] = current + quantity
        
        logger.info(f"添加物品: {item_id} x{quantity}")
        return True
        
    def remove(self, item_id: str, quantity: int = 1) -> bool:
        """
        移除物品
        
        Args:
            item_id: 物品ID
            quantity: 数量
            
        Returns:
            是否成功移除
        """
        if quantity <= 0:
            return False
            
        current = self.items.get(item_id, 0)
        if current < quantity:
            logger.warning(f"物品数量不足: {item_id} (需要{quantity}，拥有{current})")
            return False
            
        # 移除物品
        self.items[item_id] = current - quantity
        
        # 如果数量为0，移除该物品
        if self.items[item_id] == 0:
            del self.items[item_id]
            
        logger.info(f"移除物品: {item_id} x{quantity}")
        return True
        
    def has(self, item_id: str, quantity: int = 1) -> bool:
        """
        检查是否拥有足够的物品
        
        Args:
            item_id: 物品ID
            quantity: 需要的数量
            
        Returns:
            是否拥有足够数量
        """
        return self.items.get(item_id, 0) >= quantity
        
    def get_quantity(self, item_id: str) -> int:
        """获取物品数量"""
        return self.items.get(item_id, 0)
        
    def list_items(self) -> List[Tuple[str, int]]:
        """
        列出所有物品
        
        Returns:
            物品列表 [(item_id, quantity), ...]
        """
        return [(item_id, qty) for item_id, qty in self.items.items() if qty > 0]
        
    def is_full(self) -> bool:
        """检查物品栏是否已满"""
        return len(self.items) >= self.capacity
        
    def get_used_capacity(self) -> int:
        """获取已使用的容量"""
        return len(self.items)
        
    def clear(self) -> None:
        """清空物品栏"""
        self.items.clear()
        logger.info("物品栏已清空")
        
    def add_gold(self, amount: int) -> None:
        """添加金币"""
        if amount > 0:
            self.gold += amount
            logger.info(f"获得金币: {amount}")
            
    def spend_gold(self, amount: int) -> bool:
        """
        花费金币
        
        Args:
            amount: 花费数量
            
        Returns:
            是否成功花费
        """
        if amount <= 0:
            return False
            
        if self.gold < amount:
            logger.warning(f"金币不足: 需要{amount}，拥有{self.gold}")
            return False
            
        self.gold -= amount
        logger.info(f"花费金币: {amount}")
        return True
        
    def to_dict(self) -> Dict[str, any]:
        """转换为字典"""
        return {
            "capacity": self.capacity,
            "items": self.items.copy(),
            "gold": self.gold
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "Inventory":
        """从字典创建"""
        inventory = cls(capacity=data.get("capacity", 50))
        inventory.items = data.get("items", {}).copy()
        inventory.gold = data.get("gold", 0)
        return inventory
        
    def get_item_count(self, item_id: str) -> int:
        """获取物品数量（兼容方法）"""
        return self.get_quantity(item_id)
