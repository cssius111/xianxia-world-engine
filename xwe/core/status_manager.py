"""
状态显示管理器
管理游戏状态的显示和更新
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class StatusDisplay:
    """状态显示数据"""
    health: str = ""
    mana: str = ""
    stamina: str = ""
    realm: str = ""
    location: str = ""
    gold: int = 0

class StatusDisplayManager:
    """状态显示管理器"""
    
    def __init__(self):
        self.current_status = StatusDisplay()
        self.display_enabled = True
    
    def update_status(self, player_data: Dict[str, Any]) -> None:
        """更新状态显示"""
        if not player_data:
            return
        
        attrs = player_data.get("attributes", {})
        self.current_status.health = f"{attrs.get('current_health', 0)}/{attrs.get('max_health', 100)}"
        self.current_status.mana = f"{attrs.get('current_mana', 0)}/{attrs.get('max_mana', 100)}"
        self.current_status.stamina = f"{attrs.get('current_stamina', 0)}/{attrs.get('max_stamina', 100)}"
        self.current_status.realm = attrs.get('realm_name', '凡人')
        self.current_status.location = player_data.get('location', '未知')
        
        if hasattr(player_data.get('inventory'), 'gold'):
            self.current_status.gold = player_data['inventory'].gold
    
    def get_status_bar(self) -> str:
        """获取状态栏文本"""
        if not self.display_enabled:
            return ""
        
        status = self.current_status
        return (f"[生命: {status.health}] [法力: {status.mana}] "
                f"[体力: {status.stamina}] [境界: {status.realm}] "
                f"[位置: {status.location}] [金币: {status.gold}]")
    
    def toggle_display(self) -> None:
        """切换显示状态"""
        self.display_enabled = not self.display_enabled
    
    def clear_status(self) -> None:
        """清空状态"""
        self.current_status = StatusDisplay()

__all__ = ["StatusDisplayManager", "StatusDisplay"]
