class ItemSystem:
    """简单的物品系统占位实现"""

    def __init__(self):
        self.player_items = {}

    def get_spirit_stones(self, player_id: str) -> int:
        return self.player_items.get(player_id, {}).get("spirit_stones", 0)

    def add_item(self, player_id: str, item_id: str, quantity: int = 1) -> None:
        inv = self.player_items.setdefault(player_id, {})
        inv[item_id] = inv.get(item_id, 0) + quantity


# 默认的物品系统实例
item_system = ItemSystem()
