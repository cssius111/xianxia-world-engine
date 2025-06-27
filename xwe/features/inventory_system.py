"""
背包系统
管理玩家的物品存储和同步
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from xwe.core.inventory import Inventory

logger = logging.getLogger(__name__)


class InventorySystem:
    """
    背包系统
    
    提供物品管理、持久化等功能
    """
    
    def __init__(self, save_path: Optional[Path] = None):
        """
        初始化背包系统
        
        Args:
            save_path: 存档路径
        """
        if save_path is None:
            self.save_path = Path("saves") / "inventory"
        else:
            self.save_path = Path(save_path)
            
        # 确保存档目录存在
        self.save_path.mkdir(parents=True, exist_ok=True)
        
        # 玩家背包缓存
        self.inventories: Dict[str, Inventory] = {}
        
    def get_inventory(self, player_id: str) -> Inventory:
        """
        获取玩家背包
        
        Args:
            player_id: 玩家ID
            
        Returns:
            背包对象
        """
        if player_id not in self.inventories:
            # 尝试加载存档
            loaded = self.load(player_id)
            if loaded:
                self.inventories[player_id] = loaded
            else:
                # 创建新背包
                self.inventories[player_id] = Inventory()
                
        return self.inventories[player_id]
    
    def add_item(self, player_id: str, item_data: Dict[str, Any]) -> bool:
        """
        添加物品到背包
        
        Args:
            player_id: 玩家ID
            item_data: 物品数据，包含name, qty, rarity等
            
        Returns:
            是否成功添加
        """
        inventory = self.get_inventory(player_id)
        
        # 从item_data提取信息
        item_name = item_data.get("name", "未知物品")
        quantity = item_data.get("qty", 1)
        
        # 添加到背包
        success = inventory.add(item_name, quantity)

        # 记录当前数量
        current_qty = inventory.get_quantity(item_name)
        save_success = False

        if success:
            logger.info(
                f"[INVENTORY] 玩家 {player_id} 获得物品: {item_name} x{quantity}"
            )
            # 自动保存
            save_success = self.save(player_id)
        else:
            logger.warning(
                f"[INVENTORY] 玩家 {player_id} 添加物品失败: {item_name} x{quantity}"
            )

        logger.debug(
            f"[INVENTORY] {item_name} 当前数量: {current_qty}, 保存成功: {save_success}"
        )

        return success
    
    def add_items(self, player_id: str, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        批量添加物品
        
        Args:
            player_id: 玩家ID
            items: 物品列表
            
        Returns:
            成功添加的物品统计
        """
        added = {}

        for item_data in items:
            if self.add_item(player_id, item_data):
                item_name = item_data.get("name", "未知物品")
                quantity = item_data.get("qty", 1)
                added[item_name] = added.get(item_name, 0) + quantity

        total_qty = sum(added.values())
        if added:
            logger.info(f"[INVENTORY] 批量添加物品，总数: {total_qty}")
            for name, qty in added.items():
                logger.debug(f"[INVENTORY] {name} x{qty}")

        return added
    
    def remove_item(self, player_id: str, item_name: str, quantity: int = 1) -> bool:
        """
        移除物品
        
        Args:
            player_id: 玩家ID
            item_name: 物品名称
            quantity: 数量
            
        Returns:
            是否成功移除
        """
        inventory = self.get_inventory(player_id)
        success = inventory.remove(item_name, quantity)
        
        if success:
            logger.info(f"玩家 {player_id} 移除物品: {item_name} x{quantity}")
            # 自动保存
            self.save(player_id)
            
        return success
    
    def get_inventory_data(self, player_id: str) -> Dict[str, Any]:
        """
        获取背包数据（用于前端显示）
        
        Args:
            player_id: 玩家ID
            
        Returns:
            背包数据
        """
        inventory = self.get_inventory(player_id)
        
        # 构建物品列表
        items = []
        for item_id, quantity in inventory.list_items():
            items.append({
                "id": item_id,
                "name": item_id,  # 简化处理，使用ID作为名称
                "quantity": quantity,
                "rarity": "common"  # 默认稀有度
            })
            
        return {
            "capacity": inventory.capacity,
            "used": inventory.get_used_capacity(),
            "gold": inventory.gold,
            "items": items
        }
    
    def save(self, player_id: str) -> bool:
        """
        保存背包数据
        
        Args:
            player_id: 玩家ID
            
        Returns:
            是否成功保存
        """
        try:
            inventory = self.get_inventory(player_id)
            file_path = self.save_path / f"{player_id}_inventory.json"
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(inventory.to_dict(), f, ensure_ascii=False, indent=2)
                
            logger.debug(f"保存玩家 {player_id} 的背包数据")
            return True
        except Exception as e:
            logger.error(f"保存背包失败: {e}")
            return False
    
    def load(self, player_id: str) -> Optional[Inventory]:
        """
        加载背包数据
        
        Args:
            player_id: 玩家ID
            
        Returns:
            背包对象，如果不存在则返回None
        """
        try:
            file_path = self.save_path / f"{player_id}_inventory.json"
            
            if not file_path.exists():
                return None
                
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            inventory = Inventory.from_dict(data)
            logger.debug(f"加载玩家 {player_id} 的背包数据")
            return inventory
        except Exception as e:
            logger.error(f"加载背包失败: {e}")
            return None
    
    def create_initial_inventory(self, player_id: str) -> Inventory:
        """
        创建初始背包
        
        Args:
            player_id: 玩家ID
            
        Returns:
            初始化的背包
        """
        inventory = Inventory()
        
        # 添加初始物品（只有驻灵石）
        inventory.add("驻灵石", 1)
        
        # 缓存并保存
        self.inventories[player_id] = inventory
        self.save(player_id)
        
        logger.info(f"为玩家 {player_id} 创建初始背包")
        return inventory
