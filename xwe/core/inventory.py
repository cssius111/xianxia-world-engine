# core/inventory.py
"""
简易背包系统，用于管理角色携带的物品。
"""
from typing import Dict, List, Tuple

class Inventory:
    def __init__(self):
        self.items: Dict[str, int] = {}

    def add(self, item: str, quantity: int = 1) -> None:
        """向背包中添加物品"""
        if quantity <= 0:
            return
        self.items[item] = self.items.get(item, 0) + quantity

    def remove(self, item: str, quantity: int = 1) -> bool:
        """从背包中移除物品，返回是否成功"""
        if self.items.get(item, 0) < quantity or quantity <= 0:
            return False
        self.items[item] -= quantity
        if self.items[item] <= 0:
            del self.items[item]
        return True

    def list_items(self) -> List[Tuple[str, int]]:
        """列出所有物品及数量"""
        return list(self.items.items())

    def __len__(self) -> int:
        return sum(self.items.values())

    def to_dict(self) -> Dict[str, int]:
        """转换为可序列化的字典"""
        return dict(self.items)

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'Inventory':
        """从字典数据创建背包"""
        inv = cls()
        if isinstance(data, dict):
            for name, qty in data.items():
                if isinstance(qty, int) and qty > 0:
                    inv.items[name] = qty
        return inv
