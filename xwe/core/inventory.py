# core/inventory.py
"""
简易背包系统，用于管理角色携带的物品。
"""
from typing import Dict, List, Tuple

class Inventory:
    def __init__(self):
        self.items: Dict[str, int] = {}
        self.max_slots = 100  # 最大格数

    def add(self, item: str, quantity: int = 1) -> bool:
        """
        向背包中添加物品
        
        Args:
            item: 物品ID
            quantity: 数量
            
        Returns:
            是否成功添加
        """
        if quantity <= 0:
            return False
        
        # 检查背包空间（简化实现，每种物品占一格）
        if item not in self.items and len(self.items) >= self.max_slots:
            return False
        
        self.items[item] = self.items.get(item, 0) + quantity
        return True

    def remove(self, item: str, quantity: int = 1) -> bool:
        """从背包中移除物品，返回是否成功"""
        if self.items.get(item, 0) < quantity or quantity <= 0:
            return False
        self.items[item] -= quantity
        if self.items[item] <= 0:
            del self.items[item]
        return True
    
    def has(self, item: str, quantity: int = 1) -> bool:
        """检查是否有足够的物品"""
        return self.items.get(item, 0) >= quantity
    
    def get_quantity(self, item: str) -> int:
        """获取物品数量"""
        return self.items.get(item, 0)

    def list_items(self) -> List[Tuple[str, int]]:
        """列出所有物品及数量"""
        return list(self.items.items())
    
    def get_used_slots(self) -> int:
        """获取已使用格数"""
        return len(self.items)
    
    def get_free_slots(self) -> int:
        """获取剩余格数"""
        return self.max_slots - len(self.items)

    def __len__(self) -> int:
        return sum(self.items.values())
