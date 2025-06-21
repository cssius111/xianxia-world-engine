"""
AI控制器
管理NPC和怪物的AI行为
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)


class AIBehavior(Enum):
    """AI行为模式"""
    AGGRESSIVE = "aggressive"      # 激进
    DEFENSIVE = "defensive"        # 防守
    BALANCED = "balanced"          # 平衡
    SUPPORT = "support"            # 辅助
    FLEE = "flee"                  # 逃跑
    BERSERK = "berserk"           # 狂暴


class AIController:
    """
    AI控制器
    
    负责NPC和怪物的行为决策
    """
    
    def __init__(self, skill_system: Any = None):
        self.skill_system = skill_system
        
        # AI行为权重配置
        self.behavior_weights = {
            "aggressive": {
                "attack": 0.7,
                "skill": 0.2,
                "defend": 0.05,
                "wait": 0.05
            },
            "defensive": {
                "attack": 0.2,
                "skill": 0.2,
                "defend": 0.5,
                "wait": 0.1
            },
            "balanced": {
                "attack": 0.4,
                "skill": 0.3,
                "defend": 0.2,
                "wait": 0.1
            },
            "support": {
                "attack": 0.1,
                "skill": 0.6,
                "defend": 0.2,
                "wait": 0.1
            },
            "flee": {
                "attack": 0.1,
                "skill": 0.1,
                "defend": 0.3,
                "wait": 0.5
            },
            "berserk": {
                "attack": 0.8,
                "skill": 0.2,
                "defend": 0.0,
                "wait": 0.0
            }
        }
        
    def decide_action(self, actor: Any, combat_state: Any) -> Any:
        """
        决定行动
        
        Args:
            actor: 行动者
            combat_state: 战斗状态
            
        Returns:
            战斗行动
        """
        # 获取AI配置
        ai_profile = getattr(actor, "ai_profile", "balanced")
        behavior = self._determine_behavior(actor, combat_state)
        
        # 获取可用行动
        available_actions = self._get_available_actions(actor, combat_state)
        
        # 根据行为模式选择行动
        action_type = self._choose_action_type(behavior, available_actions)
        
        # 执行具体决策
        if action_type == "attack":
            return self._decide_attack(actor, combat_state)
        elif action_type == "skill":
            return self._decide_skill(actor, combat_state)
        elif action_type == "defend":
            return self._decide_defend(actor, combat_state)
        else:
            return self._decide_wait(actor, combat_state)
            
    def _determine_behavior(self, actor: Any, combat_state: Any) -> str:
        """
        确定当前行为模式
        
        基于角色状态动态调整行为
        """
        base_behavior = getattr(actor, "ai_profile", "balanced")
        
        # 生命值低时更倾向防守或逃跑
        health_percent = actor.attributes.current_health / actor.attributes.max_health
        if health_percent < 0.2:
            if random.random() < 0.7:  # 70%概率逃跑
                return "flee"
            else:
                return "defensive"
        elif health_percent < 0.5:
            if base_behavior == "aggressive":
                return "balanced"
            elif base_behavior == "balanced":
                return "defensive"
                
        # 如果有强力技能可用，更倾向使用技能
        if self._has_powerful_skill_ready(actor):
            if base_behavior in ["aggressive", "balanced"]:
                return "aggressive"
                
        return base_behavior
        
    def _get_available_actions(self, actor: Any, combat_state: Any) -> List[str]:
        """获取可用行动列表"""
        actions = ["attack", "defend", "wait"]
        
        # 检查是否有可用技能
        if self.skill_system and hasattr(actor, "skills"):
            for skill_id in actor.skills:
                skill = self.skill_system.get_skill(skill_id)
                if skill and self._can_use_skill(actor, skill):
                    actions.append("skill")
                    break
                    
        return actions
        
    def _choose_action_type(self, behavior: str, available_actions: List[str]) -> str:
        """
        根据行为模式选择行动类型
        
        使用权重随机选择
        """
        weights = self.behavior_weights.get(behavior, self.behavior_weights["balanced"])
        
        # 过滤可用行动的权重
        action_weights = []
        for action in ["attack", "skill", "defend", "wait"]:
            if action in available_actions or action in ["defend", "wait"]:
                action_weights.append((action, weights.get(action, 0.1)))
                
        # 根据权重随机选择
        total_weight = sum(w for _, w in action_weights)
        if total_weight <= 0:
            return "wait"
            
        rand = random.random() * total_weight
        current = 0
        
        for action, weight in action_weights:
            current += weight
            if rand <= current:
                return action
                
        return "wait"
        
    def _decide_attack(self, actor: Any, combat_state: Any) -> Any:
        """决定攻击目标"""
        from xwe.core.combat import CombatAction, CombatActionType
        
        # 获取敌人列表
        enemies = combat_state.get_enemies(actor)
        if not enemies:
            return CombatAction(
                action_type=CombatActionType.WAIT,
                actor_id=actor.id
            )
            
        # 选择目标（优先攻击低血量敌人）
        target = self._select_target(enemies, "lowest_health")
        
        return CombatAction(
            action_type=CombatActionType.ATTACK,
            actor_id=actor.id,
            target_ids=[target.id]
        )
        
    def _decide_skill(self, actor: Any, combat_state: Any) -> Any:
        """决定使用技能"""
        from xwe.core.combat import CombatAction, CombatActionType
        
        if not self.skill_system or not hasattr(actor, "skills"):
            return self._decide_attack(actor, combat_state)
            
        # 获取可用技能
        available_skills = []
        for skill_id in actor.skills:
            skill = self.skill_system.get_skill(skill_id)
            if skill and self._can_use_skill(actor, skill):
                available_skills.append(skill)
                
        if not available_skills:
            return self._decide_attack(actor, combat_state)
            
        # 选择技能（优先高伤害技能）
        skill = self._select_best_skill(available_skills, actor, combat_state)
        
        # 确定目标
        if skill.target_type == "self":
            target_ids = [actor.id]
        elif skill.target_type == "single_enemy":
            enemies = combat_state.get_enemies(actor)
            if enemies:
                target = self._select_target(enemies, "lowest_health")
                target_ids = [target.id]
            else:
                return self._decide_wait(actor, combat_state)
        elif skill.target_type == "all_enemies":
            enemies = combat_state.get_enemies(actor)
            target_ids = [e.id for e in enemies[:skill.max_targets]]
        else:
            target_ids = []
            
        return CombatAction(
            action_type=CombatActionType.SKILL,
            actor_id=actor.id,
            target_ids=target_ids,
            skill=skill.id
        )
        
    def _decide_defend(self, actor: Any, combat_state: Any) -> Any:
        """决定防御"""
        from xwe.core.combat import CombatAction, CombatActionType
        
        return CombatAction(
            action_type=CombatActionType.DEFEND,
            actor_id=actor.id
        )
        
    def _decide_wait(self, actor: Any, combat_state: Any) -> Any:
        """决定等待"""
        from xwe.core.combat import CombatAction, CombatActionType
        
        return CombatAction(
            action_type=CombatActionType.WAIT,
            actor_id=actor.id
        )
        
    def _can_use_skill(self, actor: Any, skill: Any) -> bool:
        """检查是否可以使用技能"""
        # 检查冷却
        if hasattr(skill, "current_cooldown") and skill.current_cooldown > 0:
            return False
            
        # 检查资源消耗
        if hasattr(skill, "mana_cost") and actor.attributes.current_mana < skill.mana_cost:
            return False
            
        if hasattr(skill, "stamina_cost") and actor.attributes.current_stamina < skill.stamina_cost:
            return False
            
        return True
        
    def _has_powerful_skill_ready(self, actor: Any) -> bool:
        """检查是否有强力技能就绪"""
        if not self.skill_system or not hasattr(actor, "skills"):
            return False
            
        for skill_id in actor.skills:
            skill = self.skill_system.get_skill(skill_id)
            if skill and self._can_use_skill(actor, skill):
                # 简单判断：伤害系数大于2的算强力技能
                if hasattr(skill, "damage_multiplier") and skill.damage_multiplier > 2:
                    return True
                    
        return False
        
    def _select_target(self, enemies: List[Any], strategy: str = "lowest_health") -> Any:
        """
        选择目标
        
        Args:
            enemies: 敌人列表
            strategy: 选择策略
            
        Returns:
            选中的目标
        """
        if not enemies:
            return None
            
        if strategy == "lowest_health":
            # 优先攻击血量最低的
            return min(enemies, key=lambda e: e.attributes.current_health)
        elif strategy == "highest_threat":
            # 优先攻击威胁最高的（攻击力最高）
            return max(enemies, key=lambda e: e.attributes.attack_power)
        elif strategy == "random":
            # 随机选择
            return random.choice(enemies)
        else:
            return enemies[0]
            
    def _select_best_skill(self, skills: List[Any], actor: Any, combat_state: Any) -> Any:
        """选择最佳技能"""
        # 简单策略：选择伤害最高的技能
        damage_skills = [s for s in skills if hasattr(s, "damage_multiplier")]
        if damage_skills:
            return max(damage_skills, key=lambda s: s.damage_multiplier)
            
        # 如果没有伤害技能，随机选择
        return random.choice(skills)
        
    def get_npc_response(self, npc: Any, player_action: str, context: Dict[str, Any]) -> str:
        """
        获取NPC对玩家行为的反应
        
        Args:
            npc: NPC对象
            player_action: 玩家行为
            context: 上下文信息
            
        Returns:
            NPC的反应文本
        """
        personality = getattr(npc, "personality", "neutral")
        relationship = context.get("relationship", 0)
        
        # 根据性格和关系生成反应
        if player_action == "greet":
            if relationship > 50:
                return f"{npc.name}热情地向你打招呼。"
            elif relationship < -50:
                return f"{npc.name}冷冷地看了你一眼。"
            else:
                return f"{npc.name}礼貌地点了点头。"
                
        elif player_action == "trade":
            if personality == "merchant":
                return f"{npc.name}露出了商人的笑容：'看看有什么需要的？'"
            elif relationship < 0:
                return f"{npc.name}摇了摇头：'我不想和你做生意。'"
            else:
                return f"{npc.name}考虑了一下：'看看你能出什么价。'"
                
        else:
            return f"{npc.name}看着你，等待你说些什么。"
