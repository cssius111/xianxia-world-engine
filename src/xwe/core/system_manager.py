"""
游戏系统管理器 - 管理角色的特殊系统（如修炼系统、战斗系统等）
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SystemManager:
    """游戏系统管理器"""
    
    def __init__(self) -> None:
        self.active_systems: Dict[str, Dict[str, Any]] = {}
    
    def activate_system(self, player_id: str, system_data: Dict[str, Any]) -> None:
        """激活玩家的系统"""
        if not system_data:
            return
        
        system_type = system_data.get('name', '')
        system_rarity = system_data.get('rarity', 'common')
        
        logger.info(f"激活系统: {system_type} ({system_rarity}) for player {player_id}")
        
        if "修炼" in system_type:
            self._activate_cultivation_system(player_id, system_data)
        elif "战斗" in system_type:
            self._activate_combat_system(player_id, system_data) 
        elif "交易" in system_type:
            self._activate_trading_system(player_id, system_data)
        else:
            self._activate_generic_system(player_id, system_data)
    
    def _activate_cultivation_system(self, player_id: str, system_data: Dict[str, Any]) -> None:
        """激活修炼系统"""
        rarity = system_data.get('rarity', 'common')
        
        # 根据稀有度设置加成
        bonuses = {
            'common': {'cultivation_speed': 1.2, 'breakthrough_success': 1.1},
            'rare': {'cultivation_speed': 1.5, 'breakthrough_success': 1.2},
            'epic': {'cultivation_speed': 2.0, 'breakthrough_success': 1.5},
            'legendary': {'cultivation_speed': 3.0, 'breakthrough_success': 2.0}
        }
        
        system_bonuses = bonuses.get(rarity, bonuses['common'])
        
        self.active_systems[player_id] = {
            'type': 'cultivation',
            'name': system_data.get('name'),
            'rarity': rarity,
            'bonuses': system_bonuses,
            'features': system_data.get('features', [])
        }
    
    def _activate_combat_system(self, player_id: str, system_data: Dict[str, Any]) -> None:
        """激活战斗系统"""
        rarity = system_data.get('rarity', 'common')
        
        bonuses = {
            'common': {'damage_bonus': 1.1, 'crit_chance': 1.1},
            'rare': {'damage_bonus': 1.3, 'crit_chance': 1.2},
            'epic': {'damage_bonus': 1.6, 'crit_chance': 1.4},
            'legendary': {'damage_bonus': 2.0, 'crit_chance': 1.8}
        }
        
        system_bonuses = bonuses.get(rarity, bonuses['common'])
        
        self.active_systems[player_id] = {
            'type': 'combat',
            'name': system_data.get('name'),
            'rarity': rarity,
            'bonuses': system_bonuses,
            'features': system_data.get('features', [])
        }
    
    def _activate_trading_system(self, player_id: str, system_data: Dict[str, Any]) -> None:
        """激活交易系统"""
        self.active_systems[player_id] = {
            'type': 'trading',
            'name': system_data.get('name'),
            'rarity': system_data.get('rarity'),
            'bonuses': {'price_discount': 0.9, 'sell_bonus': 1.2},
            'features': system_data.get('features', [])
        }
    
    def _activate_generic_system(self, player_id: str, system_data: Dict[str, Any]) -> None:
        """激活通用系统"""
        self.active_systems[player_id] = {
            'type': 'generic',
            'name': system_data.get('name'),
            'rarity': system_data.get('rarity'),
            'bonuses': {},
            'features': system_data.get('features', [])
        }
    
    def get_system_bonus(self, player_id: str, bonus_type: str) -> float:
        """获取系统提供的加成"""
        system = self.active_systems.get(player_id)
        if system:
            return system.get('bonuses', {}).get(bonus_type, 1.0)
        return 1.0
    
    def get_player_system(self, player_id: str) -> Optional[Dict[str, Any]]:
        """获取玩家的系统信息"""
        return self.active_systems.get(player_id)
    
    def has_feature(self, player_id: str, feature_name: str) -> bool:
        """检查玩家是否有特定功能"""
        system = self.active_systems.get(player_id)
        if system:
            return feature_name in system.get('features', [])
        return False


# 全局系统管理器实例
system_manager = SystemManager()
