"""
玩家服务接口定义
负责玩家角色的创建、管理、属性操作和成长系统
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum


class PlayerStatus(Enum):
    """玩家状态枚举"""
    NORMAL = "normal"
    COMBAT = "combat"
    MEDITATION = "meditation"
    TRADING = "trading"
    DIALOGUE = "dialogue"
    DEAD = "dead"
    UNCONSCIOUS = "unconscious"


@dataclass
class PlayerData:
    """玩家数据模型"""
    # 基础信息
    id: str
    name: str
    title: str = "初入江湖"
    
    # 等级和经验
    level: int = 1
    experience: int = 0
    realm: str = "炼气期"
    realm_stage: int = 1  # 境界层数（如炼气一层）
    
    # 基础属性
    health: int = 100
    max_health: int = 100
    mana: int = 50
    max_mana: int = 50
    stamina: int = 100
    max_stamina: int = 100
    
    # 战斗属性
    attack: int = 10
    defense: int = 5
    speed: int = 10
    critical_rate: float = 0.1
    dodge_rate: float = 0.1
    
    # 修炼属性
    spiritual_root: str = "普通"
    comprehension: int = 10  # 悟性
    luck: int = 10  # 气运
    karma: int = 0  # 因果值
    
    # 特殊属性
    talent: str = "平凡"
    physique: str = "凡体"  # 体质
    bloodline: str = "凡人"  # 血脉
    
    # 技能和物品
    skills: List[str] = field(default_factory=list)
    inventory: Dict[str, int] = field(default_factory=dict)
    equipment: Dict[str, str] = field(default_factory=dict)
    
    # 社交属性
    reputation: int = 0
    relationships: Dict[str, int] = field(default_factory=dict)  # NPC好感度
    faction: Optional[str] = None  # 所属门派
    faction_reputation: int = 0
    
    # 状态
    status: PlayerStatus = PlayerStatus.NORMAL
    status_effects: List[Dict[str, Any]] = field(default_factory=list)
    
    # 统计
    total_battles: int = 0
    victories: int = 0
    defeats: int = 0
    monsters_killed: int = 0
    quests_completed: int = 0
    
    # 财富
    gold: int = 0
    spirit_stones: int = 0
    contribution_points: int = 0
    
    @property
    def experience_to_next(self) -> int:
        """计算升级所需经验"""
        return self.level * 100 + 50
        
    @property
    def is_dead(self) -> bool:
        """是否死亡"""
        return self.health <= 0 or self.status == PlayerStatus.DEAD


class IPlayerService(ABC):
    """
    玩家服务接口
    
    主要职责：
    1. 玩家创建和管理
    2. 属性查询和修改
    3. 成长系统（升级、突破）
    4. 技能和物品管理
    5. 状态效果管理
    6. 社交系统
    """
    
    # ========== 玩家管理 ==========
    
    @abstractmethod
    def create_player(self, name: str, **attributes) -> str:
        """
        创建新玩家
        
        Args:
            name: 玩家名称
            **attributes: 初始属性
                - spiritual_root: 灵根
                - talent: 天赋
                - physique: 体质
                
        Returns:
            str: 玩家ID
            
        Example:
            >>> player_id = player_service.create_player(
            ...     "李逍遥",
            ...     spiritual_root="天灵根",
            ...     talent="剑道天才"
            ... )
        """
        pass
        
    @abstractmethod
    def delete_player(self, player_id: str) -> bool:
        """
        删除玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            bool: 是否删除成功
        """
        pass
        
    @abstractmethod
    def get_player(self, player_id: str) -> Optional[PlayerData]:
        """
        根据ID获取玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            PlayerData: 玩家数据，如果不存在返回None
        """
        pass
        
    @abstractmethod
    def get_current_player(self) -> Optional[PlayerData]:
        """
        获取当前玩家
        
        Returns:
            PlayerData: 当前玩家数据
        """
        pass
        
    @abstractmethod
    def set_current_player(self, player_id: str) -> bool:
        """
        设置当前玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    @abstractmethod
    def list_players(self) -> List[PlayerData]:
        """
        列出所有玩家
        
        Returns:
            List[PlayerData]: 玩家列表
        """
        pass
        
    # ========== 属性操作 ==========
    
    @abstractmethod
    def update_player(self, player_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新玩家属性
        
        Args:
            player_id: 玩家ID
            updates: 要更新的属性字典
            
        Returns:
            bool: 是否更新成功
        """
        pass
        
    @abstractmethod
    def get_attribute(self, attribute: str) -> Any:
        """
        获取玩家属性
        
        Args:
            attribute: 属性名称
            
        Returns:
            Any: 属性值
        """
        pass
        
    @abstractmethod
    def set_attribute(self, attribute: str, value: Any) -> bool:
        """
        设置玩家属性
        
        Args:
            attribute: 属性名称
            value: 属性值
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    # ========== 生命值和资源管理 ==========
    
    @abstractmethod
    def heal(self, amount: int, source: str = "normal") -> int:
        """
        治疗玩家
        
        Args:
            amount: 治疗量
            source: 治疗来源 ('normal', 'skill', 'item', 'meditation')
            
        Returns:
            int: 实际治疗量
        """
        pass
        
    @abstractmethod
    def damage(self, amount: int, damage_type: str = "physical") -> int:
        """
        对玩家造成伤害
        
        Args:
            amount: 伤害量
            damage_type: 伤害类型 ('physical', 'magical', 'true')
            
        Returns:
            int: 实际伤害量
        """
        pass
        
    @abstractmethod
    def use_mana(self, amount: int) -> bool:
        """
        消耗灵力
        
        Args:
            amount: 消耗量
            
        Returns:
            bool: 是否有足够灵力
        """
        pass
        
    @abstractmethod
    def restore_mana(self, amount: int) -> int:
        """
        恢复灵力
        
        Args:
            amount: 恢复量
            
        Returns:
            int: 实际恢复量
        """
        pass
        
    @abstractmethod
    def use_stamina(self, amount: int) -> bool:
        """
        消耗体力
        
        Args:
            amount: 消耗量
            
        Returns:
            bool: 是否有足够体力
        """
        pass
        
    @abstractmethod
    def restore_stamina(self, amount: int) -> int:
        """
        恢复体力
        
        Args:
            amount: 恢复量
            
        Returns:
            int: 实际恢复量
        """
        pass
        
    # ========== 成长系统 ==========
    
    @abstractmethod
    def add_experience(self, amount: int, source: str = "normal") -> Dict[str, Any]:
        """
        添加经验值
        
        Args:
            amount: 经验值数量
            source: 经验来源 ('combat', 'quest', 'cultivation', 'item')
            
        Returns:
            Dict: 结果信息
                - success: 是否成功
                - experience_gained: 获得的经验
                - levels_gained: 升级数
                - new_level: 新等级（如果升级）
        """
        pass
        
    @abstractmethod
    def level_up(self) -> bool:
        """
        玩家升级
        
        Returns:
            bool: 是否升级成功
        """
        pass
        
    @abstractmethod
    def can_breakthrough(self) -> bool:
        """
        检查是否可以突破境界
        
        Returns:
            bool: 是否可以突破
        """
        pass
        
    @abstractmethod
    def breakthrough(self) -> Dict[str, Any]:
        """
        突破境界
        
        Returns:
            Dict: 突破结果
                - success: 是否成功
                - new_realm: 新境界
                - bonus: 属性加成
                - message: 结果消息
        """
        pass
        
    # ========== 技能管理 ==========
    
    @abstractmethod
    def add_skill(self, skill_id: str) -> bool:
        """
        学习技能
        
        Args:
            skill_id: 技能ID
            
        Returns:
            bool: 是否学习成功
        """
        pass
        
    @abstractmethod
    def remove_skill(self, skill_id: str) -> bool:
        """
        遗忘技能
        
        Args:
            skill_id: 技能ID
            
        Returns:
            bool: 是否遗忘成功
        """
        pass
        
    @abstractmethod
    def upgrade_skill(self, skill_id: str) -> bool:
        """
        升级技能
        
        Args:
            skill_id: 技能ID
            
        Returns:
            bool: 是否升级成功
        """
        pass
        
    @abstractmethod
    def get_skills(self) -> List[Dict[str, Any]]:
        """
        获取所有技能
        
        Returns:
            List[Dict]: 技能列表
        """
        pass
        
    # ========== 物品管理 ==========
    
    @abstractmethod
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        添加物品
        
        Args:
            item_id: 物品ID
            quantity: 数量
            
        Returns:
            bool: 是否添加成功
        """
        pass
        
    @abstractmethod
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        移除物品
        
        Args:
            item_id: 物品ID
            quantity: 数量
            
        Returns:
            bool: 是否移除成功
        """
        pass
        
    @abstractmethod
    def use_item(self, item_id: str) -> Dict[str, Any]:
        """
        使用物品
        
        Args:
            item_id: 物品ID
            
        Returns:
            Dict: 使用结果
        """
        pass
        
    @abstractmethod
    def equip_item(self, item_id: str, slot: str) -> bool:
        """
        装备物品
        
        Args:
            item_id: 物品ID
            slot: 装备槽位
            
        Returns:
            bool: 是否装备成功
        """
        pass
        
    @abstractmethod
    def unequip_item(self, slot: str) -> Optional[str]:
        """
        卸下装备
        
        Args:
            slot: 装备槽位
            
        Returns:
            str: 卸下的物品ID，如果槽位为空返回None
        """
        pass
        
    # ========== 状态管理 ==========
    
    @abstractmethod
    def change_status(self, status: PlayerStatus) -> bool:
        """
        改变玩家状态
        
        Args:
            status: 新状态
            
        Returns:
            bool: 是否改变成功
        """
        pass
        
    @abstractmethod
    def add_status_effect(self, effect: Dict[str, Any]) -> bool:
        """
        添加状态效果
        
        Args:
            effect: 状态效果
                - type: 效果类型
                - duration: 持续时间
                - value: 效果值
                
        Returns:
            bool: 是否添加成功
        """
        pass
        
    @abstractmethod
    def remove_status_effect(self, effect_type: str) -> bool:
        """
        移除状态效果
        
        Args:
            effect_type: 效果类型
            
        Returns:
            bool: 是否移除成功
        """
        pass
        
    @abstractmethod
    def update_status_effects(self, delta_time: float) -> List[str]:
        """
        更新状态效果
        
        Args:
            delta_time: 时间增量（秒）
            
        Returns:
            List[str]: 过期的效果类型列表
        """
        pass
        
    # ========== 社交系统 ==========
    
    @abstractmethod
    def change_reputation(self, amount: int, faction: str = None) -> int:
        """
        改变声望
        
        Args:
            amount: 声望变化量
            faction: 门派（如果为None则改变总声望）
            
        Returns:
            int: 新的声望值
        """
        pass
        
    @abstractmethod
    def change_relationship(self, npc_id: str, amount: int) -> int:
        """
        改变与NPC的关系
        
        Args:
            npc_id: NPC ID
            amount: 好感度变化量
            
        Returns:
            int: 新的好感度
        """
        pass
        
    @abstractmethod
    def join_faction(self, faction_id: str) -> bool:
        """
        加入门派
        
        Args:
            faction_id: 门派ID
            
        Returns:
            bool: 是否加入成功
        """
        pass
        
    @abstractmethod
    def leave_faction(self) -> bool:
        """
        离开门派
        
        Returns:
            bool: 是否离开成功
        """
        pass
        
    # ========== 财富管理 ==========
    
    @abstractmethod
    def add_gold(self, amount: int) -> int:
        """
        添加金币
        
        Args:
            amount: 金币数量
            
        Returns:
            int: 当前金币总数
        """
        pass
        
    @abstractmethod
    def spend_gold(self, amount: int) -> bool:
        """
        花费金币
        
        Args:
            amount: 金币数量
            
        Returns:
            bool: 是否有足够金币
        """
        pass
        
    @abstractmethod
    def add_spirit_stones(self, amount: int) -> int:
        """
        添加灵石
        
        Args:
            amount: 灵石数量
            
        Returns:
            int: 当前灵石总数
        """
        pass
        
    @abstractmethod
    def spend_spirit_stones(self, amount: int) -> bool:
        """
        花费灵石
        
        Args:
            amount: 灵石数量
            
        Returns:
            bool: 是否有足够灵石
        """
        pass
        
    # ========== 数据持久化 ==========
    
    @abstractmethod
    def get_player_data(self, player_id: str = None) -> Dict[str, Any]:
        """
        获取玩家数据（用于存档）
        
        Args:
            player_id: 玩家ID，如果为None则获取当前玩家
            
        Returns:
            Dict: 玩家数据
        """
        pass
        
    @abstractmethod
    def load_player_data(self, data: Dict[str, Any]) -> bool:
        """
        加载玩家数据（从存档）
        
        Args:
            data: 玩家数据
            
        Returns:
            bool: 是否加载成功
        """
        pass
