"""
战斗系统
管理游戏中的战斗机制
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import random
import logging
import uuid

logger = logging.getLogger(__name__)


class CombatActionType(Enum):
    """战斗行动类型"""
    ATTACK = "attack"
    SKILL = "skill"
    DEFEND = "defend"
    ITEM = "item"
    FLEE = "flee"
    WAIT = "wait"


@dataclass
class CombatAction:
    """战斗行动"""
    action_type: CombatActionType
    actor_id: str
    target_ids: List[str] = field(default_factory=list)
    skill: Optional[str] = None
    item: Optional[str] = None


@dataclass
class DamageInfo:
    """伤害信息"""
    damage: float
    damage_type: str = "physical"
    is_critical: bool = False
    is_evaded: bool = False


@dataclass
class CombatResult:
    """战斗结果"""
    success: bool
    message: str = ""
    damage_dealt: Dict[str, DamageInfo] = field(default_factory=dict)
    healing_done: Dict[str, float] = field(default_factory=dict)
    effects_applied: List[Any] = field(default_factory=list)
    effects_removed: List[str] = field(default_factory=list)


class CombatState:
    """
    战斗状态
    
    管理一场战斗的状态
    """
    
    def __init__(self, combat_id: str):
        self.id = combat_id
        self.round_count = 0
        self.participants: Dict[str, Any] = {}  # character_id -> Character
        self.teams: Dict[str, Set[str]] = {}   # team_name -> set of character_ids
        self.turn_order: List[str] = []
        self.current_turn_index = 0
        self.is_active = True
        
    def add_participant(self, character: Any, team: str) -> None:
        """添加参与者"""
        self.participants[character.id] = character
        
        if team not in self.teams:
            self.teams[team] = set()
        self.teams[team].add(character.id)
        
        # 更新回合顺序
        self._update_turn_order()
        
    def remove_participant(self, character_id: str) -> None:
        """移除参与者"""
        if character_id in self.participants:
            del self.participants[character_id]
            
            # 从队伍中移除
            for team in self.teams.values():
                team.discard(character_id)
                
            # 更新回合顺序
            self._update_turn_order()
            
    def _update_turn_order(self) -> None:
        """根据速度更新行动顺序"""
        # 按速度排序
        self.turn_order = sorted(
            [p_id for p_id, p in self.participants.items() if p.is_alive],
            key=lambda p_id: self.participants[p_id].attributes.get("speed", 0),
            reverse=True
        )
        
    def get_current_actor(self) -> Optional[Any]:
        """获取当前行动者"""
        if not self.turn_order:
            return None
            
        while self.current_turn_index < len(self.turn_order):
            actor_id = self.turn_order[self.current_turn_index]
            actor = self.participants.get(actor_id)
            
            if actor and actor.is_alive:
                return actor
                
            self.current_turn_index += 1
            
        # 回合结束，开始新回合
        self.start_new_round()
        return self.get_current_actor()
        
    def start_new_round(self) -> None:
        """开始新回合"""
        self.round_count += 1
        self.current_turn_index = 0
        self._update_turn_order()
        
        # 更新所有角色的回合状态
        for character in self.participants.values():
            if hasattr(character, "on_round_start"):
                character.on_round_start()
                
    def next_turn(self) -> None:
        """进入下一回合"""
        self.current_turn_index += 1
        
        if self.current_turn_index >= len(self.turn_order):
            self.start_new_round()
            
    def get_team_members(self, team: str) -> List[Any]:
        """获取队伍成员"""
        if team not in self.teams:
            return []
            
        return [
            self.participants[p_id]
            for p_id in self.teams[team]
            if p_id in self.participants
        ]
        
    def get_enemies(self, character: Any) -> List[Any]:
        """获取敌人列表"""
        # 找到角色所在队伍
        character_team = None
        for team, members in self.teams.items():
            if character.id in members:
                character_team = team
                break
                
        if not character_team:
            return []
            
        # 返回其他队伍的存活成员
        enemies = []
        for team, members in self.teams.items():
            if team != character_team:
                for member_id in members:
                    member = self.participants.get(member_id)
                    if member and member.is_alive:
                        enemies.append(member)
                        
        return enemies
        
    def is_combat_over(self) -> bool:
        """检查战斗是否结束"""
        if not self.is_active:
            return True
            
        # 检查是否只有一个队伍有存活成员
        alive_teams = set()
        
        for team, members in self.teams.items():
            for member_id in members:
                member = self.participants.get(member_id)
                if member and member.is_alive:
                    alive_teams.add(team)
                    break
                    
        return len(alive_teams) <= 1
        
    def get_winning_team(self) -> Optional[str]:
        """获取胜利队伍"""
        if not self.is_combat_over():
            return None
            
        for team, members in self.teams.items():
            for member_id in members:
                member = self.participants.get(member_id)
                if member and member.is_alive:
                    return team
                    
        return None


class CombatSystem:
    """
    战斗系统管理器
    
    处理所有战斗相关的逻辑
    """
    
    def __init__(self, skill_system: Any = None, expression_parser: Any = None, heaven_law_engine: Any = None):
        self.skill_system = skill_system
        self.parser = expression_parser
        self.heaven_law_engine = heaven_law_engine
        self.active_combats: Dict[str, CombatState] = {}
        
    def create_combat(self, combat_id: Optional[str] = None) -> CombatState:
        """创建新战斗"""
        if not combat_id:
            combat_id = str(uuid.uuid4())
            
        combat = CombatState(combat_id)
        self.active_combats[combat_id] = combat
        
        logger.info(f"创建新战斗: {combat_id}")
        return combat
        
    def get_combat(self, combat_id: str) -> Optional[CombatState]:
        """获取战斗状态"""
        return self.active_combats.get(combat_id)
        
    def end_combat(self, combat_id: str) -> None:
        """结束战斗"""
        if combat_id in self.active_combats:
            combat = self.active_combats[combat_id]
            combat.is_active = False
            del self.active_combats[combat_id]

            logger.info(f"战斗结束: {combat_id}")

    def attack(self, attacker: Any, defender: Any) -> CombatResult:
        """执行一次简单的攻击并返回结果"""
        # 创建行动上下文
        from src.xwe.core.heaven_law_engine import ActionContext
        ctx = ActionContext()
        
        # ⛩ NEW: 天道审判
        if self.heaven_law_engine:
            self.heaven_law_engine.enforce(attacker, defender, ctx)
            if ctx.cancelled:
                # 处理天雷劫事件
                result = CombatResult(False, ctx.reason or "天道不容！")
                for event in ctx.events:
                    if hasattr(event, 'apply'):
                        event_msg = event.apply()
                        result.message += "\n" + event_msg
                return result
        
        # 原有的攻击逻辑
        # 创建临时战斗状态以复用伤害计算逻辑
        temp_combat = CombatState(str(uuid.uuid4()))
        temp_combat.add_participant(attacker, "attacker")
        temp_combat.add_participant(defender, "defender")

        result = self._execute_attack(attacker, [defender.id], temp_combat)

        damage = result.damage_dealt.get(defender.id)
        if damage:
            if damage.is_evaded:
                result.message = f"{defender.name} 闪避了攻击！"
            else:
                dmg_text = f"{damage.damage:.0f}"
                if damage.is_critical:
                    dmg_text = f"暴击！{dmg_text}"
                result.message = f"你对{defender.name}造成了{dmg_text}点伤害"
        else:
            result.message = "攻击未能造成伤害"

        return result
            
    def execute_action(self, combat_id: str, action: CombatAction) -> CombatResult:
        """
        执行战斗行动
        
        Args:
            combat_id: 战斗ID
            action: 战斗行动
            
        Returns:
            行动结果
        """
        combat = self.get_combat(combat_id)
        if not combat:
            return CombatResult(False, "战斗不存在")
            
        actor = combat.participants.get(action.actor_id)
        if not actor:
            return CombatResult(False, "行动者不存在")
            
        if not actor.is_alive:
            return CombatResult(False, "行动者已死亡")
            
        # 根据行动类型执行
        if action.action_type == CombatActionType.ATTACK:
            result = self._execute_attack(actor, action.target_ids, combat)
        elif action.action_type == CombatActionType.SKILL:
            result = self._execute_skill(actor, action.skill, action.target_ids, combat)
        elif action.action_type == CombatActionType.DEFEND:
            result = self._execute_defend(actor)
        elif action.action_type == CombatActionType.ITEM:
            result = self._execute_item(actor, action.item, action.target_ids)
        elif action.action_type == CombatActionType.FLEE:
            result = self._execute_flee(actor, combat)
        else:
            result = CombatResult(True, "等待")
            
        # 进入下一回合
        combat.next_turn()
        
        return result
        
    def _execute_attack(self, actor: Any, target_ids: List[str], 
                       combat: CombatState) -> CombatResult:
        """执行普通攻击"""
        result = CombatResult(True)
        
        for target_id in target_ids:
            target = combat.participants.get(target_id)
            if not target or not target.is_alive:
                continue
                
            # 计算伤害
            damage_info = self._calculate_damage(actor, target, "physical")
            
            if not damage_info.is_evaded:
                # 应用伤害
                target.take_damage(damage_info.damage, damage_info.damage_type)
                
            result.damage_dealt[target_id] = damage_info
            
        return result
        
    def _execute_skill(self, actor: Any, skill_id: str, target_ids: List[str],
                      combat: CombatState) -> CombatResult:
        """执行技能"""
        if not self.skill_system:
            return CombatResult(False, "技能系统未初始化")
            
        skill = self.skill_system.get_skill(skill_id)
        if not skill:
            return CombatResult(False, "技能不存在")
            
        # 检查是否可以使用
        if not self.skill_system.can_use_skill(actor, skill_id):
            return CombatResult(False, "无法使用该技能")
            
        # 消耗资源
        actor.consume_mana(skill.mana_cost)
        actor.consume_stamina(skill.stamina_cost)
        
        result = CombatResult(True, f"使用了 {skill.name}")
        
        # 应用技能效果
        for target_id in target_ids:
            target = combat.participants.get(target_id)
            if not target:
                continue
                
            # 伤害效果
            if hasattr(skill, "damage_multiplier") and skill.damage_multiplier > 0:
                base_damage = actor.attributes.attack_power * skill.damage_multiplier
                damage_info = DamageInfo(
                    damage=base_damage,
                    damage_type=skill.damage_type
                )
                
                # 应用伤害
                target.take_damage(damage_info.damage, damage_info.damage_type)
                result.damage_dealt[target_id] = damage_info
                
            # 治疗效果
            if hasattr(skill, "heal_amount") and skill.heal_amount > 0:
                heal = skill.heal_amount
                target.heal(heal)
                result.healing_done[target_id] = heal
                
            # 状态效果
            if hasattr(skill, "effects"):
                for effect in skill.effects:
                    # TODO: 应用状态效果
                    result.effects_applied.append(effect)
                    
        # 设置技能冷却
        self.skill_system.use_skill(actor, skill_id)
        
        return result
        
    def _execute_defend(self, actor: Any) -> CombatResult:
        """执行防御"""
        # 添加防御状态
        # TODO: 实现防御状态效果
        return CombatResult(True, f"{actor.name} 进入防御姿态")
        
    def _execute_item(self, actor: Any, item_id: str, 
                     target_ids: List[str]) -> CombatResult:
        """执行使用物品"""
        # TODO: 实现物品使用逻辑
        return CombatResult(False, "物品系统未实现")
        
    def _execute_flee(self, actor: Any, combat: CombatState) -> CombatResult:
        """执行逃跑"""
        # 计算逃跑成功率
        flee_chance = 0.5  # 基础50%
        
        # 根据速度差调整
        enemies = combat.get_enemies(actor)
        if enemies:
            avg_enemy_speed = sum(e.attributes.get("speed", 0) for e in enemies) / len(enemies)
            speed_diff = actor.attributes.get("speed", 0) - avg_enemy_speed
            flee_chance += speed_diff * 0.01  # 每点速度差增加1%
            
        flee_chance = max(0.1, min(0.9, flee_chance))  # 限制在10%-90%
        
        if random.random() < flee_chance:
            # 逃跑成功
            combat.remove_participant(actor.id)
            return CombatResult(True, f"{actor.name} 成功逃离战斗")
        else:
            return CombatResult(True, f"{actor.name} 逃跑失败")
            
    def _calculate_damage(self, attacker: Any, defender: Any, 
                         damage_type: str = "physical") -> DamageInfo:
        """计算伤害"""
        # 检查闪避
        if random.random() < defender.attributes.dodge_rate:
            return DamageInfo(0, damage_type, is_evaded=True)
            
        # 基础伤害
        if damage_type == "physical":
            base_damage = attacker.attributes.attack_power
            defense = defender.attributes.defense
        else:  # magical
            base_damage = attacker.attributes.spell_power
            defense = defender.attributes.magic_resistance
            
        # 防御减伤
        damage_reduction = defense / (defense + 100)  # 防御力公式
        damage = base_damage * (1 - damage_reduction)
        
        # 暴击判定
        is_critical = random.random() < attacker.attributes.critical_rate
        if is_critical:
            damage *= attacker.attributes.critical_damage
            
        # 随机浮动±10%
        damage *= random.uniform(0.9, 1.1)
        
        # 最少造成1点伤害
        damage = max(1, damage)
        
        return DamageInfo(damage, damage_type, is_critical)
