# core/ai.py
"""
AI系统模块

管理NPC的行为决策和战斗AI。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import random
import logging

from .character import Character
from .combat import CombatState, CombatAction, CombatActionType
from .skills import SkillSystem, TargetType

logger = logging.getLogger(__name__)


class AIPersonality(Enum):
    """AI性格类型"""
    AGGRESSIVE = "aggressive"      # 激进型
    DEFENSIVE = "defensive"        # 防御型
    BALANCED = "balanced"          # 均衡型
    SUPPORT = "support"            # 辅助型
    CUNNING = "cunning"            # 狡诈型
    BERSERKER = "berserker"        # 狂战士


class ThreatLevel(Enum):
    """威胁等级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ThreatInfo:
    """威胁信息"""
    character_id: str
    threat_value: float
    threat_level: ThreatLevel
    reasons: List[str] = field(default_factory=list)


@dataclass
class AIDecision:
    """AI决策结果"""
    action: CombatAction
    priority: float
    reasoning: str


class AIBehaviorNode:
    """AI行为树节点"""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List['AIBehaviorNode'] = []
        
    def evaluate(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """评估节点，返回决策"""
        raise NotImplementedError


class SelectorNode(AIBehaviorNode):
    """选择节点 - 依次尝试子节点直到成功"""
    
    def evaluate(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        for child in self.children:
            result = child.evaluate(context)
            if result:
                return result
        return None


class SequenceNode(AIBehaviorNode):
    """序列节点 - 依次执行所有子节点"""
    
    def evaluate(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        results = []
        for child in self.children:
            result = child.evaluate(context)
            if not result:
                return None
            results.append(result)
        # 返回优先级最高的决策
        return max(results, key=lambda x: x.priority) if results else None


class ConditionNode(AIBehaviorNode):
    """条件节点"""
    
    def __init__(self, name: str, condition_func):
        super().__init__(name)
        self.condition_func = condition_func
        
    def evaluate(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        if self.condition_func(context):
            # 条件满足，评估子节点
            for child in self.children:
                result = child.evaluate(context)
                if result:
                    return result
        return None


class ActionNode(AIBehaviorNode):
    """行动节点"""
    
    def __init__(self, name: str, action_func):
        super().__init__(name)
        self.action_func = action_func
        
    def evaluate(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        return self.action_func(context)


class AIController:
    """
    AI控制器
    
    负责NPC的决策和行为控制。
    """
    
    def __init__(self, skill_system: SkillSystem):
        """
        初始化AI控制器
        
        Args:
            skill_system: 技能系统
        """
        self.skill_system = skill_system
        self.behavior_trees: Dict[str, AIBehaviorNode] = {}
        
        # 初始化默认行为树
        self._init_default_behaviors()
    
    def _init_default_behaviors(self):
        """初始化默认行为树"""
        # 激进型AI
        aggressive_tree = self._build_aggressive_tree()
        self.behavior_trees['aggressive'] = aggressive_tree
        
        # 防御型AI
        defensive_tree = self._build_defensive_tree()
        self.behavior_trees['defensive'] = defensive_tree
        
        # 均衡型AI
        balanced_tree = self._build_balanced_tree()
        self.behavior_trees['balanced'] = balanced_tree
        
        # 默认AI
        self.behavior_trees['default'] = balanced_tree
    
    def _build_aggressive_tree(self) -> AIBehaviorNode:
        """构建激进型行为树"""
        root = SelectorNode("aggressive_root")
        
        # 低血量时的紧急行为
        emergency = ConditionNode("emergency_check", 
                                  lambda ctx: ctx['self_health_percent'] < 0.2)
        emergency.children.append(
            ActionNode("flee_or_heal", self._action_emergency_response)
        )
        root.children.append(emergency)
        
        # 主要攻击行为
        attack_sequence = SequenceNode("attack_sequence")
        
        # 优先使用大招
        use_ultimate = ConditionNode("can_use_ultimate",
                                     lambda ctx: self._has_ultimate_ready(ctx))
        use_ultimate.children.append(
            ActionNode("use_ultimate", self._action_use_strongest_skill)
        )
        attack_sequence.children.append(use_ultimate)
        
        # 常规攻击
        attack_sequence.children.append(
            ActionNode("normal_attack", self._action_aggressive_attack)
        )
        
        root.children.append(attack_sequence)
        
        return root
    
    def _build_defensive_tree(self) -> AIBehaviorNode:
        """构建防御型行为树"""
        root = SelectorNode("defensive_root")
        
        # 高威胁时防御
        high_threat = ConditionNode("high_threat",
                                    lambda ctx: ctx['threat_level'] >= ThreatLevel.HIGH)
        high_threat.children.append(
            ActionNode("defend", self._action_defend)
        )
        root.children.append(high_threat)
        
        # 治疗自己或队友
        need_heal = ConditionNode("need_healing",
                                  lambda ctx: self._need_healing(ctx))
        need_heal.children.append(
            ActionNode("heal", self._action_heal)
        )
        root.children.append(need_heal)
        
        # 保守攻击
        root.children.append(
            ActionNode("conservative_attack", self._action_conservative_attack)
        )
        
        return root
    
    def _build_balanced_tree(self) -> AIBehaviorNode:
        """构建均衡型行为树"""
        root = SelectorNode("balanced_root")
        
        # 紧急情况
        emergency = ConditionNode("emergency_check",
                                  lambda ctx: ctx['self_health_percent'] < 0.3)
        emergency_selector = SelectorNode("emergency_actions")
        emergency_selector.children.extend([
            ActionNode("heal_self", self._action_heal_self),
            ActionNode("defend", self._action_defend)
        ])
        emergency.children.append(emergency_selector)
        root.children.append(emergency)
        
        # 正常战斗
        combat_selector = SelectorNode("combat_actions")
        
        # 根据情况选择行动
        good_opportunity = ConditionNode("good_opportunity",
                                         lambda ctx: self._has_advantage(ctx))
        good_opportunity.children.append(
            ActionNode("power_attack", self._action_use_strongest_skill)
        )
        combat_selector.children.append(good_opportunity)
        
        # 默认攻击
        combat_selector.children.append(
            ActionNode("balanced_attack", self._action_balanced_attack)
        )
        
        root.children.append(combat_selector)
        
        return root
    
    def decide_action(self, character: Character, combat_state: CombatState) -> CombatAction:
        """
        决定NPC的行动
        
        Args:
            character: NPC角色
            combat_state: 战斗状态
            
        Returns:
            战斗行动
        """
        # 构建决策上下文
        context = self._build_context(character, combat_state)
        
        # 获取对应的行为树
        ai_profile = character.ai_profile or 'default'
        behavior_tree = self.behavior_trees.get(ai_profile, self.behavior_trees['default'])
        
        # 评估行为树
        decision = behavior_tree.evaluate(context)
        
        if decision:
            logger.debug(f"{character.name} 决策: {decision.reasoning}")
            return decision.action
        
        # 默认行动
        return self._default_action(character, combat_state)
    
    def _build_context(self, character: Character, combat_state: CombatState) -> Dict[str, Any]:
        """构建决策上下文"""
        # 计算自身状态
        self_health_percent = character.attributes.current_health / character.attributes.max_health
        self_mana_percent = character.attributes.current_mana / character.attributes.max_mana
        
        # 评估威胁
        enemies = combat_state.get_enemies(character)
        threats = self.evaluate_threats(character, enemies)
        
        # 获取可用技能
        available_skills = self.skill_system.get_available_skills(character)
        
        # 统计队友状态
        allies = combat_state.get_allies(character)
        injured_allies = [a for a in allies if a.attributes.current_health / a.attributes.max_health < 0.5]
        
        context = {
            'character': character,
            'combat_state': combat_state,
            'self_health_percent': self_health_percent,
            'self_mana_percent': self_mana_percent,
            'enemies': enemies,
            'allies': allies,
            'injured_allies': injured_allies,
            'threats': threats,
            'threat_level': max([t.threat_level for t in threats]) if threats else ThreatLevel.LOW,
            'available_skills': available_skills,
            'turn_count': combat_state.turn_count,
        }
        
        return context
    
    def evaluate_threats(self, character: Character, enemies: List[Character]) -> List[ThreatInfo]:
        """
        评估威胁等级
        
        Args:
            character: 自身角色
            enemies: 敌人列表
            
        Returns:
            威胁信息列表
        """
        threats = []
        
        for enemy in enemies:
            threat_value = 0
            reasons = []
            
            # 基于攻击力的威胁
            enemy_attack = enemy.attributes.get('attack_power')
            threat_value += enemy_attack * 0.5
            
            # 基于当前血量的威胁（残血敌人威胁度降低）
            enemy_health_percent = enemy.attributes.current_health / enemy.attributes.max_health
            if enemy_health_percent < 0.3:
                threat_value *= 0.5
                reasons.append("敌人血量较低")
            
            # 基于技能的威胁
            enemy_skills = self.skill_system.get_available_skills(enemy)
            if Any(s.skill_type.value in ['control', 'debuff'] for s in enemy_skills):
                threat_value *= 1.5
                reasons.append("拥有控制技能")
            
            # 基于境界的威胁
            level_diff = enemy.attributes.cultivation_level - character.attributes.cultivation_level
            if level_diff > 0:
                threat_value *= (1 + level_diff * 0.1)
                reasons.append(f"境界高出{level_diff}级")
            
            # 确定威胁等级
            if threat_value < 50:
                threat_level = ThreatLevel.LOW
            elif threat_value < 100:
                threat_level = ThreatLevel.MEDIUM  
            elif threat_value < 150:
                threat_level = ThreatLevel.HIGH
            else:
                threat_level = ThreatLevel.CRITICAL
            
            threats.append(ThreatInfo(
                character_id=enemy.id,
                threat_value=threat_value,
                threat_level=threat_level,
                reasons=reasons
            ))
        
        # 按威胁值排序
        threats.sort(key=lambda x: x.threat_value, reverse=True)
        
        return threats
    
    def select_target(self, 
                      character: Character,
                      enemies: List[Character],
                      strategy: str = "highest_threat") -> Optional[Character]:
        """
        选择目标
        
        Args:
            character: 自身角色
            enemies: 敌人列表
            strategy: 选择策略
            
        Returns:
            目标角色
        """
        if not enemies:
            return None
        
        if strategy == "highest_threat":
            # 选择威胁最高的目标
            threats = self.evaluate_threats(character, enemies)
            if threats:
                target_id = threats[0].character_id
                return next((e for e in enemies if e.id == target_id), None)
                
        elif strategy == "lowest_health":
            # 选择血量最低的目标
            return min(enemies, key=lambda e: e.attributes.current_health)
            
        elif strategy == "highest_damage":
            # 选择攻击力最高的目标
            return max(enemies, key=lambda e: e.attributes.get('attack_power'))
            
        elif strategy == "support_first":
            # 优先攻击治疗/辅助职业
            healers = [e for e in enemies if Any(
                s.skill_type.value in ['heal', 'buff'] 
                for s in self.skill_system.get_character_skills(e)
            )]
            if healers:
                return healers[0]
        
        # 默认选择第一个
        return enemies[0]
    
    # === 行动函数 ===
    
    def _action_emergency_response(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """紧急响应行动"""
        character = context['character']
        
        # 尝试使用治疗技能
        heal_skills = [s for s in context['available_skills'] 
                       if s.skill_type.value == 'heal']
        if heal_skills:
            skill = heal_skills[0]
            return AIDecision(
                action=CombatAction(
                    action_type=CombatActionType.SKILL,
                    actor_id=character.id,
                    target_ids=[character.id],
                    skill_id=skill.id
                ),
                priority=10,
                reasoning="紧急治疗自己"
            )
        
        # 否则防御
        return AIDecision(
            action=CombatAction(
                action_type=CombatActionType.DEFEND,
                actor_id=character.id
            ),
            priority=9,
            reasoning="紧急防御"
        )
    
    def _action_use_strongest_skill(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """使用最强技能"""
        character = context['character']
        enemies = context['enemies']
        
        if not enemies:
            return None
        
        # 选择伤害最高的技能
        damage_skills = [s for s in context['available_skills']
                         if s.skill_type.value in ['attack', 'control']]
        
        if not damage_skills:
            return None
        
        # 简单地选择灵力消耗最高的技能（通常更强）
        skill = max(damage_skills, key=lambda s: s.mana_cost)
        
        # 选择目标
        target = self.select_target(character, enemies, "highest_threat")
        if not target:
            return None
        
        return AIDecision(
            action=CombatAction(
                action_type=CombatActionType.SKILL,
                actor_id=character.id,
                target_ids=[target.id],
                skill_id=skill.id
            ),
            priority=8,
            reasoning=f"使用强力技能 {skill.name}"
        )
    
    def _action_aggressive_attack(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """激进攻击"""
        character = context['character']
        enemies = context['enemies']
        
        if not enemies:
            return None
        
        # 选择血量最低的敌人
        target = self.select_target(character, enemies, "lowest_health")
        
        # 优先使用技能
        attack_skills = [s for s in context['available_skills']
                         if s.skill_type.value == 'attack']
        
        if attack_skills:
            skill = random.choice(attack_skills)
            return AIDecision(
                action=CombatAction(
                    action_type=CombatActionType.SKILL,
                    actor_id=character.id,
                    target_ids=[target.id],
                    skill_id=skill.id
                ),
                priority=7,
                reasoning="激进技能攻击"
            )
        
        # 普通攻击
        return AIDecision(
            action=CombatAction(
                action_type=CombatActionType.ATTACK,
                actor_id=character.id,
                target_ids=[target.id]
            ),
            priority=5,
            reasoning="激进普通攻击"
        )
    
    def _action_defend(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """防御行动"""
        character = context['character']
        
        return AIDecision(
            action=CombatAction(
                action_type=CombatActionType.DEFEND,
                actor_id=character.id
            ),
            priority=6,
            reasoning="进入防御姿态"
        )
    
    def _action_heal(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """治疗行动"""
        character = context['character']
        injured_allies = context['injured_allies']
        
        # 获取治疗技能
        heal_skills = [s for s in context['available_skills']
                       if s.skill_type.value == 'heal']
        
        if not heal_skills:
            return None
        
        skill = heal_skills[0]
        
        # 选择治疗目标
        if character.attributes.current_health / character.attributes.max_health < 0.5:
            target_id = character.id
            reasoning = "治疗自己"
        elif injured_allies:
            target = min(injured_allies, 
                         key=lambda a: a.attributes.current_health / a.attributes.max_health)
            target_id = target.id
            reasoning = f"治疗队友 {target.name}"
        else:
            return None
        
        return AIDecision(
            action=CombatAction(
                action_type=CombatActionType.SKILL,
                actor_id=character.id,
                target_ids=[target_id],
                skill_id=skill.id
            ),
            priority=8,
            reasoning=reasoning
        )
    
    def _action_heal_self(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """自我治疗"""
        character = context['character']
        
        heal_skills = [s for s in context['available_skills']
                       if s.skill_type.value == 'heal' and 
                       s.target_type.value in ['self', 'single_ally']]
        
        if heal_skills:
            skill = heal_skills[0]
            return AIDecision(
                action=CombatAction(
                    action_type=CombatActionType.SKILL,
                    actor_id=character.id,
                    target_ids=[character.id],
                    skill_id=skill.id
                ),
                priority=9,
                reasoning="紧急自我治疗"
            )
        
        return None
    
    def _action_conservative_attack(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """保守攻击"""
        character = context['character']
        enemies = context['enemies']
        
        if not enemies:
            return None
        
        # 选择威胁最高的目标
        target = self.select_target(character, enemies, "highest_threat")
        
        # 只使用消耗较少的技能
        cheap_skills = [s for s in context['available_skills']
                        if s.skill_type.value == 'attack' and s.mana_cost <= 20]
        
        if cheap_skills and context['self_mana_percent'] > 0.5:
            skill = random.choice(cheap_skills)
            return AIDecision(
                action=CombatAction(
                    action_type=CombatActionType.SKILL,
                    actor_id=character.id,
                    target_ids=[target.id],
                    skill_id=skill.id
                ),
                priority=5,
                reasoning="保守技能攻击"
            )
        
        # 普通攻击
        return AIDecision(
            action=CombatAction(
                action_type=CombatActionType.ATTACK,
                actor_id=character.id,
                target_ids=[target.id]
            ),
            priority=4,
            reasoning="保守普通攻击"
        )
    
    def _action_balanced_attack(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """均衡攻击"""
        character = context['character']
        enemies = context['enemies']
        
        if not enemies:
            return None
        
        # 根据灵力选择行动
        if context['self_mana_percent'] > 0.6:
            # 灵力充足，使用技能
            attack_skills = [s for s in context['available_skills']
                             if s.skill_type.value in ['attack', 'control']]
            
            if attack_skills:
                skill = random.choice(attack_skills)
                target = self.select_target(character, enemies, "highest_threat")
                
                return AIDecision(
                    action=CombatAction(
                        action_type=CombatActionType.SKILL,
                        actor_id=character.id,
                        target_ids=[target.id],
                        skill_id=skill.id
                    ),
                    priority=6,
                    reasoning="均衡技能攻击"
                )
        
        # 普通攻击
        target = self.select_target(character, enemies, "lowest_health")
        return AIDecision(
            action=CombatAction(
                action_type=CombatActionType.ATTACK,
                actor_id=character.id,
                target_ids=[target.id]
            ),
            priority=5,
            reasoning="均衡普通攻击"
        )
    
    def _default_action(self, character: Character, combat_state: CombatState) -> CombatAction:
        """默认行动"""
        enemies = combat_state.get_enemies(character)
        
        if enemies:
            # 有敌人，进行普通攻击
            target = random.choice(enemies)
            return CombatAction(
                action_type=CombatActionType.ATTACK,
                actor_id=character.id,
                target_ids=[target.id]
            )
        
        # 没有敌人，等待
        return CombatAction(
            action_type=CombatActionType.WAIT,
            actor_id=character.id
        )
    
    # === 辅助函数 ===
    
    def _has_ultimate_ready(self, context: Dict[str, Any]) -> bool:
        """检查是否有大招可用"""
        # 简单地检查是否有高消耗技能可用
        skills = context['available_skills']
        return Any(s.mana_cost >= 50 for s in skills)
    
    def _need_healing(self, context: Dict[str, Any]) -> bool:
        """检查是否需要治疗"""
        character = context['character']
        
        # 自己需要治疗
        if context['self_health_percent'] < 0.5:
            return True
        
        # 队友需要治疗
        if context['injured_allies']:
            return True
        
        return False
    
    def _has_advantage(self, context: Dict[str, Any]) -> bool:
        """检查是否有优势"""
        character = context['character']
        enemies = context['enemies']
        allies = context['allies']
        
        # 人数优势
        if len(allies) > len(enemies):
            return True
        
        # 等级优势
        if enemies:
            avg_enemy_level = sum(e.attributes.cultivation_level for e in enemies) / len(enemies)
            if character.attributes.cultivation_level > avg_enemy_level + 2:
                return True
        
        # 状态优势
        if context['self_health_percent'] > 0.8 and context['self_mana_percent'] > 0.6:
            return True
        
        return False
