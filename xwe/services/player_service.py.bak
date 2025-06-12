"""
玩家服务
负责玩家数据的管理和操作
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import uuid
import time

from . import ServiceBase, ServiceContainer
from ..events import EventBus, PlayerEvent


@dataclass
class PlayerData:
    """玩家数据模型"""
    id: str
    name: str
    level: int = 1
    experience: int = 0
    realm: str = "炼气期"
    health: int = 100
    max_health: int = 100
    mana: int = 50
    max_mana: int = 50
    attack: int = 10
    defense: int = 5
    speed: int = 10
    
    # 扩展属性
    spiritual_root: str = "普通"
    talent: str = "平凡"
    fate: str = "普通"
    
    # 技能和物品
    skills: List[str] = field(default_factory=list)
    inventory: Dict[str, int] = field(default_factory=dict)
    equipment: Dict[str, str] = field(default_factory=dict)
    
    # 统计数据
    total_battles: int = 0
    victories: int = 0
    defeats: int = 0
    
    # 时间戳
    created_at: float = field(default_factory=time.time)
    last_save_at: float = field(default_factory=time.time)
    
    @property
    def experience_to_next(self) -> int:
        """计算升级所需经验"""
        return self.level * 100 + 50
        
    @property
    def win_rate(self) -> float:
        """计算胜率"""
        if self.total_battles == 0:
            return 0.0
        return self.victories / self.total_battles


class IPlayerService(ABC):
    """玩家服务接口"""
    
    @abstractmethod
    def create_player(self, name: str, **kwargs) -> str:
        """创建新玩家"""
        pass
        
    @abstractmethod
    def get_player(self, player_id: str) -> Optional[PlayerData]:
        """根据ID获取玩家"""
        pass
        
    @abstractmethod
    def get_current_player(self) -> Optional[PlayerData]:
        """获取当前玩家"""
        pass
        
    @abstractmethod
    def update_player(self, player_id: str, updates: Dict[str, Any]) -> bool:
        """更新玩家数据"""
        pass
        
    @abstractmethod
    def add_experience(self, amount: int) -> Dict[str, Any]:
        """添加经验值"""
        pass
        
    @abstractmethod
    def level_up(self) -> bool:
        """玩家升级"""
        pass
        
    @abstractmethod
    def heal(self, amount: int) -> int:
        """治疗玩家"""
        pass
        
    @abstractmethod
    def damage(self, amount: int) -> int:
        """对玩家造成伤害"""
        pass
        
    @abstractmethod
    def use_mana(self, amount: int) -> bool:
        """消耗灵力"""
        pass
        
    @abstractmethod
    def restore_mana(self, amount: int) -> int:
        """恢复灵力"""
        pass
        
    @abstractmethod
    def add_skill(self, skill_id: str) -> bool:
        """学习技能"""
        pass
        
    @abstractmethod
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """添加物品"""
        pass
        
    @abstractmethod
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """移除物品"""
        pass
        
    @abstractmethod
    def equip_item(self, item_id: str, slot: str) -> bool:
        """装备物品"""
        pass
        
    @abstractmethod
    def get_current_player_data(self) -> Dict[str, Any]:
        """获取当前玩家数据（用于存档）"""
        pass
        
    @abstractmethod
    def load_player_data(self, data: Dict[str, Any]) -> bool:
        """加载玩家数据（从存档）"""
        pass


class PlayerService(ServiceBase[IPlayerService], IPlayerService):
    """玩家服务实现"""
    
    def __init__(self, container: ServiceContainer):
        super().__init__(container)
        self._players: Dict[str, PlayerData] = {}
        self._current_player_id: Optional[str] = None
        self._event_bus: Optional[EventBus] = None
        
    def _do_initialize(self) -> None:
        """初始化服务"""
        self._event_bus = EventBus()
        
    def create_player(self, name: str, **kwargs) -> str:
        """创建新玩家"""
        # 生成唯一ID
        player_id = str(uuid.uuid4())
        
        # 创建玩家数据
        player = PlayerData(
            id=player_id,
            name=name,
            spiritual_root=kwargs.get('spiritual_root', '普通'),
            talent=kwargs.get('talent', '平凡'),
            fate=kwargs.get('fate', '普通')
        )
        
        # 根据灵根调整初始属性
        if player.spiritual_root == '天灵根':
            player.max_mana += 50
            player.mana = player.max_mana
        elif player.spiritual_root == '异灵根':
            player.attack += 5
            player.defense += 5
            
        # 根据天赋调整初始属性
        if player.talent == '剑道天才':
            player.attack += 10
            player.skills.append('basic_sword')
        elif player.talent == '炼体天才':
            player.max_health += 50
            player.health = player.max_health
            player.defense += 5
            
        # 保存玩家
        self._players[player_id] = player
        self._current_player_id = player_id
        
        # 发布玩家创建事件
        self._publish_event(PlayerEvent('player_created', {
            'player_id': player_id,
            'name': name
        }))
        
        self.logger.info(f"Created player: {name} (ID: {player_id})")
        
        return player_id
        
    def get_player(self, player_id: str) -> Optional[PlayerData]:
        """根据ID获取玩家"""
        return self._players.get(player_id)
        
    def get_current_player(self) -> Optional[PlayerData]:
        """获取当前玩家"""
        if self._current_player_id:
            return self._players.get(self._current_player_id)
        return None
        
    def update_player(self, player_id: str, updates: Dict[str, Any]) -> bool:
        """更新玩家数据"""
        player = self.get_player(player_id)
        if not player:
            return False
            
        # 更新属性
        for key, value in updates.items():
            if hasattr(player, key):
                setattr(player, key, value)
                
        player.last_save_at = time.time()
        
        # 发布更新事件
        self._publish_event(PlayerEvent('player_updated', {
            'player_id': player_id,
            'updates': updates
        }))
        
        return True
        
    def add_experience(self, amount: int) -> Dict[str, Any]:
        """添加经验值"""
        player = self.get_current_player()
        if not player:
            return {'success': False, 'message': '未找到玩家'}
            
        old_level = player.level
        player.experience += amount
        
        # 检查升级
        levels_gained = 0
        while player.experience >= player.experience_to_next:
            player.experience -= player.experience_to_next
            self.level_up()
            levels_gained += 1
            
        result = {
            'success': True,
            'experience_gained': amount,
            'current_experience': player.experience,
            'levels_gained': levels_gained
        }
        
        if levels_gained > 0:
            result['new_level'] = player.level
            result['message'] = f"获得{amount}点经验，升到了{player.level}级！"
        else:
            result['message'] = f"获得{amount}点经验"
            
        # 发布经验获得事件
        self._publish_event(PlayerEvent('experience_gained', {
            'player_id': player.id,
            'amount': amount,
            'levels_gained': levels_gained
        }))
        
        return result
        
    def level_up(self) -> bool:
        """玩家升级"""
        player = self.get_current_player()
        if not player:
            return False
            
        player.level += 1
        
        # 提升属性
        player.max_health += 20
        player.health = player.max_health  # 升级时恢复满血
        player.max_mana += 10
        player.mana = player.max_mana  # 恢复满灵力
        player.attack += 3
        player.defense += 2
        player.speed += 1
        
        # 发布升级事件
        self._publish_event(PlayerEvent('player_level_up', {
            'player_id': player.id,
            'new_level': player.level
        }))
        
        self.logger.info(f"Player {player.name} leveled up to {player.level}")
        
        return True
        
    def heal(self, amount: int) -> int:
        """治疗玩家"""
        player = self.get_current_player()
        if not player:
            return 0
            
        old_health = player.health
        player.health = min(player.health + amount, player.max_health)
        actual_heal = player.health - old_health
        
        if actual_heal > 0:
            self._publish_event(PlayerEvent('player_healed', {
                'player_id': player.id,
                'amount': actual_heal,
                'current_health': player.health
            }))
            
        return actual_heal
        
    def damage(self, amount: int) -> int:
        """对玩家造成伤害"""
        player = self.get_current_player()
        if not player:
            return 0
            
        # 计算实际伤害（考虑防御）
        actual_damage = max(1, amount - player.defense // 2)
        
        old_health = player.health
        player.health = max(0, player.health - actual_damage)
        damage_dealt = old_health - player.health
        
        self._publish_event(PlayerEvent('player_damaged', {
            'player_id': player.id,
            'damage': damage_dealt,
            'current_health': player.health
        }))
        
        # 检查死亡
        if player.health <= 0:
            self._publish_event(PlayerEvent('player_died', {
                'player_id': player.id
            }))
            
        return damage_dealt
        
    def use_mana(self, amount: int) -> bool:
        """消耗灵力"""
        player = self.get_current_player()
        if not player or player.mana < amount:
            return False
            
        player.mana -= amount
        
        self._publish_event(PlayerEvent('mana_used', {
            'player_id': player.id,
            'amount': amount,
            'current_mana': player.mana
        }))
        
        return True
        
    def restore_mana(self, amount: int) -> int:
        """恢复灵力"""
        player = self.get_current_player()
        if not player:
            return 0
            
        old_mana = player.mana
        player.mana = min(player.mana + amount, player.max_mana)
        actual_restore = player.mana - old_mana
        
        if actual_restore > 0:
            self._publish_event(PlayerEvent('mana_restored', {
                'player_id': player.id,
                'amount': actual_restore,
                'current_mana': player.mana
            }))
            
        return actual_restore
        
    def add_skill(self, skill_id: str) -> bool:
        """学习技能"""
        player = self.get_current_player()
        if not player:
            return False
            
        if skill_id in player.skills:
            return False  # 已经学会
            
        player.skills.append(skill_id)
        
        self._publish_event(PlayerEvent('skill_learned', {
            'player_id': player.id,
            'skill_id': skill_id
        }))
        
        self.logger.info(f"Player {player.name} learned skill: {skill_id}")
        
        return True
        
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """添加物品"""
        player = self.get_current_player()
        if not player:
            return False
            
        if item_id in player.inventory:
            player.inventory[item_id] += quantity
        else:
            player.inventory[item_id] = quantity
            
        self._publish_event(PlayerEvent('item_added', {
            'player_id': player.id,
            'item_id': item_id,
            'quantity': quantity
        }))
        
        return True
        
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """移除物品"""
        player = self.get_current_player()
        if not player:
            return False
            
        if item_id not in player.inventory:
            return False
            
        if player.inventory[item_id] < quantity:
            return False
            
        player.inventory[item_id] -= quantity
        
        if player.inventory[item_id] <= 0:
            del player.inventory[item_id]
            
        self._publish_event(PlayerEvent('item_removed', {
            'player_id': player.id,
            'item_id': item_id,
            'quantity': quantity
        }))
        
        return True
        
    def equip_item(self, item_id: str, slot: str) -> bool:
        """装备物品"""
        player = self.get_current_player()
        if not player:
            return False
            
        # 检查是否拥有物品
        if item_id not in player.inventory:
            return False
            
        # 卸下原有装备
        old_item = player.equipment.get(slot)
        if old_item:
            self.add_item(old_item, 1)
            
        # 装备新物品
        player.equipment[slot] = item_id
        self.remove_item(item_id, 1)
        
        self._publish_event(PlayerEvent('item_equipped', {
            'player_id': player.id,
            'item_id': item_id,
            'slot': slot,
            'old_item': old_item
        }))
        
        return True
        
    def get_current_player_data(self) -> Dict[str, Any]:
        """获取当前玩家数据（用于存档）"""
        player = self.get_current_player()
        if not player:
            return {}
            
        return {
            'id': player.id,
            'name': player.name,
            'level': player.level,
            'experience': player.experience,
            'realm': player.realm,
            'health': player.health,
            'max_health': player.max_health,
            'mana': player.mana,
            'max_mana': player.max_mana,
            'attack': player.attack,
            'defense': player.defense,
            'speed': player.speed,
            'spiritual_root': player.spiritual_root,
            'talent': player.talent,
            'fate': player.fate,
            'skills': player.skills,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'total_battles': player.total_battles,
            'victories': player.victories,
            'defeats': player.defeats,
            'created_at': player.created_at
        }
        
    def load_player_data(self, data: Dict[str, Any]) -> bool:
        """加载玩家数据（从存档）"""
        if not data or 'id' not in data:
            return False
            
        player = PlayerData(**data)
        self._players[player.id] = player
        self._current_player_id = player.id
        
        self.logger.info(f"Loaded player data: {player.name}")
        
        return True
        
    def _publish_event(self, event: PlayerEvent) -> None:
        """发布事件"""
        if self._event_bus:
            self._event_bus.publish(event)
