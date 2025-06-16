"""
战斗服务接口定义
负责战斗系统的管理，包括战斗流程、伤害计算、技能释放和AI控制
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CombatType(Enum):
    """战斗类型"""
    PVE = "pve"              # 玩家对环境
    PVP = "pvp"              # 玩家对玩家
    GUILD_WAR = "guild_war"  # 门派战
    ARENA = "arena"          # 竞技场
    BOSS = "boss"            # Boss战
    SIEGE = "siege"          # 攻城战


class CombatantType(Enum):
    """战斗者类型"""
    PLAYER = "player"
    NPC = "npc"
    MONSTER = "monster"
    BOSS = "boss"
    SUMMON = "summon"
    PET = "pet"


class ActionType(Enum):
    """行动类型"""
    ATTACK = "attack"          # 普通攻击
    SKILL = "skill"            # 使用技能
    DEFEND = "defend"          # 防御
    FLEE = "flee"              # 逃跑
    ITEM = "item"              # 使用物品
    SUMMON = "summon"          # 召唤
    WAIT = "wait"              # 等待


class DamageType(Enum):
    """伤害类型"""
    PHYSICAL = "physical"      # 物理伤害
    MAGICAL = "magical"        # 法术伤害
    TRUE = "true"              # 真实伤害
    ELEMENTAL = "elemental"    # 元素伤害
    POISON = "poison"          # 毒伤害
    BLEED = "bleed"            # 流血伤害


@dataclass
class Combatant:
    """战斗参与者"""
    id: str
    name: str
    type: CombatantType
    team: int  # 队伍编号
    
    # 战斗属性
    health: int
    max_health: int
    mana: int
    max_mana: int
    attack: int
    defense: int
    speed: int
    
    # 元素属性
    element: str = "neutral"  # 元素属性
    element_resistance: Dict[str, float] = field(default_factory=dict)
    
    # 技能和物品
    skills: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    
    # 状态
    is_alive: bool = True
    is_defending: bool = False
    status_effects: List[Dict[str, Any]] = field(default_factory=list)
    
    # AI配置（对于NPC）
    ai_type: str = "aggressive"  # AI类型
    ai_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CombatAction:
    """战斗行动"""
    actor_id: str
    action_type: ActionType
    target_id: Optional[str] = None
    skill_id: Optional[str] = None
    item_id: Optional[str] = None
    priority: int = 0  # 行动优先级


@dataclass
class CombatResult:
    """战斗结果"""
    success: bool
    description: str
    damage_dealt: int = 0
    healing_done: int = 0
    mana_used: int = 0
    
    # 效果
    effects_applied: List[Dict[str, Any]] = field(default_factory=list)
    effects_removed: List[str] = field(default_factory=list)
    
    # 额外信息
    is_critical: bool = False
    is_dodged: bool = False
    is_blocked: bool = False
    element_reaction: Optional[str] = None


@dataclass
class CombatState:
    """战斗状态"""
    id: str
    type: CombatType
    round: int = 1
    turn: int = 1
    
    # 参与者
    combatants: Dict[str, Combatant] = field(default_factory=dict)
    teams: Dict[int, List[str]] = field(default_factory=dict)
    
    # 状态
    is_active: bool = True
    winner_team: Optional[int] = None
    
    # 行动队列
    action_queue: List[str] = field(default_factory=list)
    current_actor: Optional[str] = None
    
    # 战斗日志
    combat_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # 奖励
    rewards: Dict[str, Any] = field(default_factory=dict)


class ICombatService(ABC):
    """
    战斗服务接口
    
    主要职责：
    1. 战斗流程管理
    2. 伤害计算和效果处理
    3. 技能系统
    4. 战斗AI
    5. 战斗奖励
    6. 战斗日志
    """
    
    # ========== 战斗管理 ==========
    
    @abstractmethod
    def start_combat(self, combat_type: CombatType, 
                     teams: Dict[int, List[Dict[str, Any]]]) -> str:
        """
        开始战斗
        
        Args:
            combat_type: 战斗类型
            teams: 队伍配置
                {
                    1: [{"id": "player", "type": "player", ...}],
                    2: [{"id": "monster_1", "type": "monster", ...}]
                }
                
        Returns:
            str: 战斗ID
            
        Example:
            >>> combat_id = combat_service.start_combat(
            ...     CombatType.PVE,
            ...     {
            ...         1: [player_data],
            ...         2: [monster_data]
            ...     }
            ... )
        """
        pass
        
    @abstractmethod
    def end_combat(self, combat_id: str, reason: str = "normal") -> Dict[str, Any]:
        """
        结束战斗
        
        Args:
            combat_id: 战斗ID
            reason: 结束原因 ('normal', 'flee', 'timeout', 'error')
            
        Returns:
            Dict: 战斗结果
                - winner_team: 获胜队伍
                - rewards: 奖励
                - statistics: 战斗统计
        """
        pass
        
    @abstractmethod
    def get_combat_state(self, combat_id: str = None) -> Optional[CombatState]:
        """
        获取战斗状态
        
        Args:
            combat_id: 战斗ID，None表示当前战斗
            
        Returns:
            CombatState: 战斗状态
        """
        pass
        
    @abstractmethod
    def is_in_combat(self) -> bool:
        """
        检查是否在战斗中
        
        Returns:
            bool: 是否在战斗中
        """
        pass
        
    # ========== 行动处理 ==========
    
    @abstractmethod
    def execute_action(self, action: CombatAction) -> CombatResult:
        """
        执行战斗行动
        
        Args:
            action: 战斗行动
            
        Returns:
            CombatResult: 行动结果
        """
        pass
        
    @abstractmethod
    def attack(self, target_id: str) -> CombatResult:
        """
        执行普通攻击
        
        Args:
            target_id: 目标ID
            
        Returns:
            CombatResult: 攻击结果
        """
        pass
        
    @abstractmethod
    def use_skill(self, skill_id: str, target_id: Optional[str] = None) -> CombatResult:
        """
        使用技能
        
        Args:
            skill_id: 技能ID
            target_id: 目标ID（某些技能可能不需要目标）
            
        Returns:
            CombatResult: 技能结果
        """
        pass
        
    @abstractmethod
    def defend(self) -> CombatResult:
        """
        进行防御
        
        Returns:
            CombatResult: 防御结果
        """
        pass
        
    @abstractmethod
    def flee(self) -> CombatResult:
        """
        尝试逃跑
        
        Returns:
            CombatResult: 逃跑结果
        """
        pass
        
    @abstractmethod
    def use_item(self, item_id: str, target_id: Optional[str] = None) -> CombatResult:
        """
        使用物品
        
        Args:
            item_id: 物品ID
            target_id: 目标ID
            
        Returns:
            CombatResult: 使用结果
        """
        pass
        
    # ========== 伤害计算 ==========
    
    @abstractmethod
    def calculate_damage(self, attacker_id: str, defender_id: str,
                        damage_type: DamageType, base_damage: int) -> int:
        """
        计算伤害
        
        Args:
            attacker_id: 攻击者ID
            defender_id: 防御者ID
            damage_type: 伤害类型
            base_damage: 基础伤害
            
        Returns:
            int: 最终伤害
        """
        pass
        
    @abstractmethod
    def apply_damage(self, target_id: str, damage: int, 
                    damage_type: DamageType) -> Dict[str, Any]:
        """
        应用伤害
        
        Args:
            target_id: 目标ID
            damage: 伤害值
            damage_type: 伤害类型
            
        Returns:
            Dict: 伤害结果
                - actual_damage: 实际伤害
                - is_killed: 是否击杀
                - overkill: 溢出伤害
        """
        pass
        
    @abstractmethod
    def heal_target(self, target_id: str, amount: int, 
                   source: str = "normal") -> int:
        """
        治疗目标
        
        Args:
            target_id: 目标ID
            amount: 治疗量
            source: 治疗来源
            
        Returns:
            int: 实际治疗量
        """
        pass
        
    # ========== 状态效果 ==========
    
    @abstractmethod
    def apply_effect(self, target_id: str, effect: Dict[str, Any]) -> bool:
        """
        应用状态效果
        
        Args:
            target_id: 目标ID
            effect: 效果配置
                - type: 效果类型
                - duration: 持续时间
                - value: 效果值
                
        Returns:
            bool: 是否成功应用
        """
        pass
        
    @abstractmethod
    def remove_effect(self, target_id: str, effect_type: str) -> bool:
        """
        移除状态效果
        
        Args:
            target_id: 目标ID
            effect_type: 效果类型
            
        Returns:
            bool: 是否成功移除
        """
        pass
        
    @abstractmethod
    def update_effects(self) -> List[Tuple[str, str]]:
        """
        更新所有状态效果
        
        Returns:
            List[Tuple[str, str]]: 过期的效果列表 (目标ID, 效果类型)
        """
        pass
        
    # ========== 回合管理 ==========
    
    @abstractmethod
    def next_turn(self) -> Optional[str]:
        """
        进入下一回合
        
        Returns:
            str: 当前行动者ID，如果战斗结束返回None
        """
        pass
        
    @abstractmethod
    def get_turn_order(self) -> List[str]:
        """
        获取行动顺序
        
        Returns:
            List[str]: 行动者ID列表（按速度排序）
        """
        pass
        
    @abstractmethod
    def skip_turn(self) -> bool:
        """
        跳过当前回合
        
        Returns:
            bool: 是否成功跳过
        """
        pass
        
    # ========== AI控制 ==========
    
    @abstractmethod
    def get_ai_action(self, combatant_id: str) -> CombatAction:
        """
        获取AI行动
        
        Args:
            combatant_id: 战斗者ID
            
        Returns:
            CombatAction: AI决定的行动
        """
        pass
        
    @abstractmethod
    def set_ai_difficulty(self, difficulty: str) -> bool:
        """
        设置AI难度
        
        Args:
            difficulty: 难度 ('easy', 'normal', 'hard', 'nightmare')
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    # ========== 战斗查询 ==========
    
    @abstractmethod
    def get_combatant(self, combatant_id: str) -> Optional[Combatant]:
        """
        获取战斗者信息
        
        Args:
            combatant_id: 战斗者ID
            
        Returns:
            Combatant: 战斗者信息
        """
        pass
        
    @abstractmethod
    def get_combat_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取战斗日志
        
        Args:
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 战斗日志
        """
        pass
        
    @abstractmethod
    def get_combat_statistics(self) -> Dict[str, Any]:
        """
        获取战斗统计
        
        Returns:
            Dict: 统计信息
                - total_damage_dealt: 总伤害
                - total_damage_taken: 总承受伤害
                - skills_used: 技能使用次数
                - items_used: 物品使用次数
        """
        pass
        
    # ========== 战斗配置 ==========
    
    @abstractmethod
    def set_combat_speed(self, speed: float) -> bool:
        """
        设置战斗速度
        
        Args:
            speed: 速度倍率
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    @abstractmethod
    def enable_auto_combat(self, enabled: bool) -> bool:
        """
        启用/禁用自动战斗
        
        Args:
            enabled: 是否启用
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    @abstractmethod
    def set_combat_timeout(self, timeout: int) -> bool:
        """
        设置战斗超时时间
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        pass
