# core/combat.py
"""
战斗系统模块

管理游戏中的战斗流程、伤害计算和战斗日志。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import logging
import random

from ..engine.expression import ExpressionParser
from .character import Character, CharacterState
from .skills import Skill, SkillSystem, TargetType, DamageType
from .status import StatusEffect, StatusEffectType

logger = logging.getLogger(__name__)


class CombatActionType(Enum):
    """战斗行动类型"""
    ATTACK = "attack"          # 普通攻击
    SKILL = "skill"            # 使用技能
    DEFEND = "defend"          # 防御
    ITEM = "item"              # 使用物品
    FLEE = "flee"              # 逃跑
    WAIT = "wait"              # 等待


@dataclass
class CombatAction:
    """战斗行动"""
    action_type: CombatActionType
    actor_id: str
    target_ids: List[str] = field(default_factory=list)
    skill_id: Optional[str] = None
    item_id: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DamageInfo:
    """伤害信息"""
    damage: float
    damage_type: DamageType
    is_critical: bool = False
    is_blocked: bool = False
    is_evaded: bool = False
    element: Optional[str] = None


@dataclass
class CombatResult:
    """战斗结果"""
    success: bool
    message: str
    damage_dealt: Dict[str, DamageInfo] = field(default_factory=dict)
    healing_done: Dict[str, float] = field(default_factory=dict)
    effects_applied: List[StatusEffect] = field(default_factory=list)
    resources_consumed: Dict[str, float] = field(default_factory=dict)
    extra_data: Dict[str, Any] = field(default_factory=dict)


class CombatState:
    """战斗状态"""
    
    def __init__(self):
        """初始化战斗状态"""
        self.turn_count: int = 0
        self.participants: Dict[str, Character] = {}
        self.teams: Dict[str, List[str]] = {}  # 队伍ID -> 成员ID列表
        self.action_order: List[str] = []
        self.current_actor_index: int = 0
        self.combat_log: List[str] = []
        self.is_active: bool = True
        
    def add_participant(self, character: Character, team_id: str):
        """添加战斗参与者"""
        self.participants[character.id] = character
        
        if team_id not in self.teams:
            self.teams[team_id] = []
        self.teams[team_id].append(character.id)
        
        character.team_id = team_id
        character.state = CharacterState.COMBAT
        
    def get_team_members(self, team_id: str) -> List[Character]:
        """获取队伍成员"""
        if team_id not in self.teams:
            return []
        
        members = []
        for char_id in self.teams[team_id]:
            if char_id in self.participants:
                members.append(self.participants[char_id])
        
        return members
    
    def get_enemies(self, character: Character) -> List[Character]:
        """获取敌对目标"""
        enemies = []
        
        for team_id, members in self.teams.items():
            if team_id != character.team_id:
                for char_id in members:
                    if char_id in self.participants:
                        enemy = self.participants[char_id]
                        if enemy.is_alive:
                            enemies.append(enemy)
        
        return enemies
    
    def get_allies(self, character: Character) -> List[Character]:
        """获取友方目标"""
        return [c for c in self.get_team_members(character.team_id) 
                if c.id != character.id and c.is_alive]
    
    def is_combat_over(self) -> bool:
        """检查战斗是否结束"""
        alive_teams = set()
        
        for team_id, members in self.teams.items():
            for char_id in members:
                if char_id in self.participants:
                    if self.participants[char_id].is_alive:
                        alive_teams.add(team_id)
                        break
        
        return len(alive_teams) <= 1
    
    def get_winning_team(self) -> Optional[str]:
        """获取胜利队伍"""
        for team_id, members in self.teams.items():
            for char_id in members:
                if char_id in self.participants:
                    if self.participants[char_id].is_alive:
                        return team_id
        return None


class CombatSystem:
    """
    战斗系统管理器
    
    负责战斗流程控制、伤害计算和战斗日志。
    """
    
    def __init__(self, skill_system: SkillSystem, expression_parser: ExpressionParser):
        """
        初始化战斗系统
        
        Args:
            skill_system: 技能系统
            expression_parser: 表达式解析器
        """
        self.skill_system = skill_system
        self.parser = expression_parser
        self.combat_states: Dict[str, CombatState] = {}
        
    def create_combat(self, combat_id: str) -> CombatState:
        """
        创建战斗
        
        Args:
            combat_id: 战斗ID
            
        Returns:
            战斗状态对象
        """
        state = CombatState()
        self.combat_states[combat_id] = state
        logger.info(f"创建战斗: {combat_id}")
        return state
    
    def get_combat(self, combat_id: str) -> Optional[CombatState]:
        """获取战斗状态"""
        return self.combat_states.get(combat_id)
    
    def end_combat(self, combat_id: str):
        """结束战斗"""
        if combat_id in self.combat_states:
            state = self.combat_states[combat_id]
            state.is_active = False
            
            # 重置所有参与者状态
            for character in state.participants.values():
                character.state = CharacterState.NORMAL
                character.team_id = None
                
            del self.combat_states[combat_id]
            logger.info(f"结束战斗: {combat_id}")
    
    def execute_action(self, 
                       combat_id: str,
                       action: CombatAction) -> CombatResult:
        """
        执行战斗行动
        
        Args:
            combat_id: 战斗ID
            action: 战斗行动
            
        Returns:
            战斗结果
        """
        state = self.get_combat(combat_id)
        if not state:
            return CombatResult(False, "战斗不存在")
        
        # 获取行动者
        actor = state.participants.get(action.actor_id)
        if not actor:
            return CombatResult(False, "行动者不存在")
        
        if not actor.can_act:
            return CombatResult(False, f"{actor.name} 无法行动")
        
        # 根据行动类型执行
        if action.action_type == CombatActionType.ATTACK:
            return self._execute_basic_attack(state, actor, action)
            
        elif action.action_type == CombatActionType.SKILL:
            return self._execute_skill(state, actor, action)
            
        elif action.action_type == CombatActionType.DEFEND:
            return self._execute_defend(state, actor)
            
        elif action.action_type == CombatActionType.WAIT:
            return CombatResult(True, f"{actor.name} 选择等待")
            
        else:
            return CombatResult(False, "未实现的行动类型")
    
    def _execute_basic_attack(self, 
                              state: CombatState,
                              actor: Character,
                              action: CombatAction) -> CombatResult:
        """执行普通攻击"""
        if not action.target_ids:
            return CombatResult(False, "未指定目标")
        
        target_id = action.target_ids[0]
        target = state.participants.get(target_id)
        
        if not target or not target.is_alive:
            return CombatResult(False, "无效目标")
        
        # 检查是否命中
        hit_chance = self._calculate_hit_chance(actor, target)
        if random.random() > hit_chance:
            state.combat_log.append(f"{actor.name} 的攻击被 {target.name} 闪避了！")
            return CombatResult(
                True, 
                "攻击被闪避",
                damage_dealt={target_id: DamageInfo(0, DamageType.PHYSICAL, is_evaded=True)}
            )
        
        # 计算伤害
        damage = self._calculate_basic_damage(actor, target)
        
        # 检查暴击
        is_critical = random.random() < self._calculate_crit_chance(actor)
        if is_critical:
            damage *= 2
        
        # 应用伤害
        target.take_damage(damage, "physical")
        
        # 记录日志
        damage_text = f"{damage:.0f}"
        if is_critical:
            damage_text = f"暴击！{damage_text}"
        
        state.combat_log.append(
            f"{actor.name} 对 {target.name} 造成了 {damage_text} 点物理伤害"
        )
        
        return CombatResult(
            True,
            "攻击成功",
            damage_dealt={target_id: DamageInfo(damage, DamageType.PHYSICAL, is_critical)}
        )
    
    def _execute_skill(self,
                       state: CombatState,
                       actor: Character,
                       action: CombatAction) -> CombatResult:
        """执行技能"""
        if not action.skill_id:
            return CombatResult(False, "未指定技能")
        
        # 获取技能
        skill = self.skill_system.get_skill(action.skill_id)
        if not skill:
            return CombatResult(False, "技能不存在")
        
        # 检查是否可用
        can_use, reason = skill.can_use(actor)
        if not can_use:
            return CombatResult(False, reason)
        
        # 获取目标
        targets = self._get_skill_targets(state, actor, skill, action.target_ids)
        if not targets:
            return CombatResult(False, "无有效目标")
        
        # 消耗资源
        skill.consume_resources(actor)
        
        # 执行效果
        result = CombatResult(True, f"{actor.name} 使用了 {skill.name}")
        
        for effect in skill.effects:
            if effect.effect_type == "damage":
                # 造成伤害
                for target in targets:
                    if not target.is_alive:
                        continue
                    
                    damage = self.skill_system.calculate_skill_damage(
                        skill, actor, target, effect
                    )
                    
                    # 检查暴击
                    is_critical = random.random() < self._calculate_crit_chance(actor)
                    if is_critical:
                        damage *= 2
                    
                    target.take_damage(damage, skill.damage_type.value)
                    
                    result.damage_dealt[target.id] = DamageInfo(
                        damage, skill.damage_type, is_critical, element=effect.element
                    )
                    
                    damage_text = f"{damage:.0f}"
                    if is_critical:
                        damage_text = f"暴击！{damage_text}"
                    
                    state.combat_log.append(
                        f"{skill.name} 对 {target.name} 造成了 {damage_text} 点伤害"
                    )
            
            elif effect.effect_type == "heal":
                # 治疗
                for target in targets:
                    if not target.is_alive:
                        continue
                    
                    # 计算治疗量
                    context = {'spell_power': actor.attributes.get('spell_power')}
                    heal_amount = self.parser.evaluate(effect.formula, context)
                    
                    target.heal(heal_amount)
                    result.healing_done[target.id] = heal_amount
                    
                    state.combat_log.append(
                        f"{skill.name} 为 {target.name} 恢复了 {heal_amount:.0f} 点生命"
                    )
            
            elif effect.effect_type in ["buff", "debuff"]:
                # 施加状态
                for target in targets:
                    if not target.is_alive:
                        continue
                    
                    # 创建状态效果
                    status = StatusEffect(
                        name=f"{skill.name}效果",
                        description=skill.description,
                        effect_type=StatusEffectType.BUFF if effect.effect_type == "buff" else StatusEffectType.DEBUFF,
                        duration=effect.duration,
                        remaining_duration=effect.duration,
                        modifier_type=effect.extra_params.get('attribute', ''),
                        modifier_value=effect.extra_params.get('value', 0),
                        source_id=actor.id,
                        source_skill=skill.id
                    )
                    
                    if target.status_effects.add_effect(status):
                        result.effects_applied.append(status)
                        state.combat_log.append(
                            f"{target.name} 获得了 {status.name}"
                        )
        
        # 触发技能回调
        self.skill_system.trigger_skill_callbacks(
            'on_skill_used',
            skill=skill,
            caster=actor,
            targets=targets,
            result=result
        )
        
        return result
    
    def _execute_defend(self,
                        state: CombatState,
                        actor: Character) -> CombatResult:
        """执行防御"""
        # 添加防御状态
        defense_buff = StatusEffect(
            name="防御姿态",
            description="防御力提升50%",
            effect_type=StatusEffectType.BUFF,
            duration=1,
            remaining_duration=1,
            modifier_type="defense",
            modifier_value=actor.attributes.get('defense') * 0.5,
            source_id=actor.id
        )
        
        actor.status_effects.add_effect(defense_buff)
        
        state.combat_log.append(f"{actor.name} 进入防御姿态")
        
        return CombatResult(
            True,
            "防御成功",
            effects_applied=[defense_buff]
        )
    
    def _get_skill_targets(self,
                           state: CombatState,
                           actor: Character,
                           skill: Skill,
                           target_ids: List[str]) -> List[Character]:
        """获取技能目标"""
        targets = []
        
        if skill.target_type == TargetType.SELF:
            targets = [actor]
            
        elif skill.target_type == TargetType.SINGLE_ENEMY:
            if target_ids and target_ids[0] in state.participants:
                target = state.participants[target_ids[0]]
                if target.is_alive and target.team_id != actor.team_id:
                    targets = [target]
                    
        elif skill.target_type == TargetType.SINGLE_ALLY:
            if target_ids and target_ids[0] in state.participants:
                target = state.participants[target_ids[0]]
                if target.is_alive and target.team_id == actor.team_id:
                    targets = [target]
                    
        elif skill.target_type == TargetType.ALL_ENEMIES:
            targets = state.get_enemies(actor)[:skill.max_targets]
            
        elif skill.target_type == TargetType.ALL_ALLIES:
            targets = [actor] + state.get_allies(actor)
            targets = targets[:skill.max_targets]
        
        return targets
    
    def _calculate_basic_damage(self, attacker: Character, defender: Character) -> float:
        """计算基础物理伤害"""
        attack = attacker.attributes.get('attack_power')
        defense = defender.attributes.get('defense')
        
        # 基础伤害公式
        damage = max(1, attack - defense * 0.5)
        
        # 随机浮动
        damage *= random.uniform(0.9, 1.1)
        
        return damage
    
    def _calculate_hit_chance(self, attacker: Character, defender: Character) -> float:
        """计算命中率"""
        accuracy = attacker.attributes.get('accuracy')
        evasion = defender.attributes.get('evasion')
        
        # 命中率公式
        hit_chance = accuracy / (accuracy + evasion)
        
        return max(0.1, min(0.95, hit_chance))
    
    def _calculate_crit_chance(self, character: Character) -> float:
        """计算暴击率"""
        crit_rate = character.attributes.get('critical_rate')
        return min(0.75, crit_rate / 100)
    
    def process_turn(self, combat_id: str):
        """处理回合"""
        state = self.get_combat(combat_id)
        if not state:
            return
        
        # 更新所有角色的状态效果
        for character in state.participants.values():
            if character.is_alive:
                character.status_effects.update()
                
                # 更新技能冷却
                self.skill_system.update_cooldowns(character)
        
        # 增加回合数
        state.turn_count += 1
        
        # 检查战斗是否结束
        if state.is_combat_over():
            winning_team = state.get_winning_team()
            state.combat_log.append(f"战斗结束！胜利方: {winning_team}")
            self.end_combat(combat_id)
