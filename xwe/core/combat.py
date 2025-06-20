"""
战斗系统优化实现
使用数据驱动的方式处理战斗计算和AI行为
"""

import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from xwe.core.data_manager import DM
from xwe.core.formula_engine import calculate, evaluate_expression, formula_engine

logger = logging.getLogger(__name__)


class CombatPhase(Enum):
    """战斗阶段枚举"""

    INITIALIZATION = "initialization"
    INITIATIVE = "initiative"
    ACTION = "action"
    RESOLUTION = "resolution"
    END_TURN = "end_turn"


class ActionType(Enum):
    """行动类型枚举"""

    ATTACK = "attack"
    CAST_SPELL = "cast_spell"
    USE_SKILL = "use_skill"
    USE_ITEM = "use_item"
    DEFEND = "defend"
    MOVE = "move"
    FLEE = "flee"


# 兼容旧接口
CombatActionType = ActionType


@dataclass
class CombatAction:
    """简单的战斗行动数据类"""

    action_type: ActionType
    actor_id: str
    target_ids: List[str] = field(default_factory=list)
    skill: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action_type,
            "target": self.target_ids[0] if self.target_ids else None,
            "skill": self.skill,
        }


@dataclass
class CombatResult:
    """Simplified result object for backward compatibility."""

    success: bool
    message: str = ""
    damage_dealt: Optional[Dict[str, Any]] = None


class CombatSystemV3:
    """
    数据驱动的战斗系统V3
    从JSON配置加载所有战斗规则和计算公式
    """

    # 提供枚举别名，便于外部访问
    ActionType = ActionType

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            logger.debug("战斗系统已初始化，跳过")
            return

        self._initialized = True

        self.combat_data = {}
        self.element_data = {}
        self.active_combats = {}
        self._load_combat_data()

    def _load_combat_data(self) -> None:
        """加载战斗系统数据"""
        try:
            self.combat_data = DM.load("combat_system")
            logger.info("Combat system data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load combat data: {e}")
            raise

    def create_combat(self, combat_id: str, participants: Optional[List[Any]] = None) -> "Combat":
        """
        创建新的战斗实例

        Args:
            combat_id: 战斗唯一标识
            participants: 参与者列表

        Returns:
            Combat实例
        """
        participants = participants or []
        combat = Combat(self, combat_id, participants)
        self.active_combats[combat_id] = combat
        return combat

    def execute_action(self, combat_id: str, action: CombatAction) -> CombatResult:
        """对外暴露的执行行动接口"""
        combat = self.active_combats.get(combat_id)
        if not combat:
            return CombatResult(False, "invalid combat")

        if isinstance(action, CombatAction):
            action_dict = action.to_dict()
        else:
            action_dict = action

        result_dict = combat.execute_turn(action_dict)
        return CombatResult(
            result_dict.get("success", False),
            result_dict.get("message", ""),
            result_dict.get("damage_dealt"),
        )

    def calculate_damage(
        self, attacker, defender, action_type: str, skill_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        计算伤害

        Returns:
            包含伤害值和详细信息的字典
        """
        result = {
            "hit": False,
            "critical": False,
            "damage": 0,
            "damage_type": "physical",
            "effects": [],
            "details": {},
        }

        # 命中判定
        hit_chance = self._calculate_hit_chance(attacker, defender)
        result["details"]["hit_chance"] = hit_chance

        if random.random() > hit_chance:
            result["details"]["miss_reason"] = "evasion"
            return result

        result["hit"] = True

        # 暴击判定
        crit_chance = self._calculate_critical_chance(attacker, skill_data)
        result["details"]["crit_chance"] = crit_chance

        if random.random() < crit_chance:
            result["critical"] = True

        # 计算基础伤害
        if action_type == "physical":
            damage = self._calculate_physical_damage(attacker, defender, skill_data)
            result["damage_type"] = "physical"
        elif action_type == "magical":
            damage = self._calculate_magical_damage(attacker, defender, skill_data)
            result["damage_type"] = "magical"
        else:
            damage = skill_data.get("base_damage", 0)
            result["damage_type"] = skill_data.get("damage_type", "true")

        # 应用暴击
        if result["critical"]:
            crit_multi = self.combat_data["attack_resolution"]["hit_calculation"]["critical_hit"][
                "damage_multiplier"
            ]
            damage *= crit_multi

        # 应用元素克制
        if hasattr(attacker, "element") and hasattr(defender, "element"):
            element_multi = self._get_element_multiplier(attacker.element, defender.element)
            damage *= element_multi
            result["details"]["element_multiplier"] = element_multi

        # 应用境界压制
        if hasattr(attacker, "realm") and hasattr(defender, "realm"):
            from xwe.core.cultivation_system import cultivation_system

            suppression = cultivation_system.get_realm_suppression(attacker.realm, defender.realm)
            damage *= 1 + suppression
            result["details"]["realm_suppression"] = suppression

        # 最终伤害
        result["damage"] = max(1, int(damage))

        # 检查特殊效果
        if skill_data and "effects" in skill_data:
            result["effects"] = self._process_skill_effects(
                skill_data["effects"], attacker, defender
            )

        return result

    def _calculate_hit_chance(self, attacker, defender) -> float:
        """计算命中率"""
        context = {
            "accuracy": attacker.attributes.get("accuracy", 50),
            "evasion": defender.attributes.get("evasion", 20),
            "level_difference": attacker.level - defender.level,
        }

        return calculate("hit_chance", **context)

    def _calculate_critical_chance(self, attacker, skill_data: Optional[Dict]) -> float:
        """计算暴击率"""
        context = {
            "base_critical": attacker.attributes.get("critical_rate", 0.05),
            "weapon_critical": attacker.equipment.get("weapon", {}).get("critical_rate", 0),
            "skill_critical": skill_data.get("critical_bonus", 0) if skill_data else 0,
            "luck": attacker.attributes.get("luck", 0),
        }

        return calculate("critical_chance", **context)

    def _calculate_physical_damage(self, attacker, defender, skill_data: Optional[Dict]) -> float:
        """计算物理伤害"""
        # 获取配置的公式
        damage_config = self.combat_data["attack_resolution"]["damage_calculation"]["physical"]

        # 基础攻击力
        weapon_damage = attacker.equipment.get("weapon", {}).get("damage", 0)
        strength_bonus = attacker.attributes.get("strength", 0) * 2
        skill_bonus = skill_data.get("damage_bonus", 0) if skill_data else 0

        # 计算基础伤害
        base_damage = weapon_damage + strength_bonus + skill_bonus

        # 如果有技能倍率
        if skill_data and "damage_multiplier" in skill_data:
            base_damage *= skill_data["damage_multiplier"]

        # 计算防御减免
        armor = defender.attributes.get("armor", 0)
        constitution = defender.attributes.get("constitution", 0)
        reduction = armor + constitution / 10

        # 最终伤害
        final_damage = max(damage_config["minimum"], base_damage - reduction)

        return final_damage

    def _calculate_magical_damage(self, attacker, defender, skill_data: Optional[Dict]) -> float:
        """计算魔法伤害"""
        context = {
            "spell_power": attacker.attributes.get("spell_power", 0),
            "element_multiplier": 1.0,  # 将在外部计算
            "magic_resistance": defender.attributes.get("magic_resistance", 0),
        }

        # 如果有技能数据，使用技能的基础伤害
        if skill_data:
            context["spell_power"] = skill_data.get("base_damage", context["spell_power"])

        return calculate("magical_damage", **context)

    def _get_element_multiplier(self, attacker_element: str, defender_element: str) -> float:
        """获取元素克制倍率"""
        element_system = self.combat_data["elemental_system"]["basic_elements"]

        if attacker_element not in element_system:
            return 1.0

        element_data = element_system[attacker_element]

        if defender_element in element_data["strong_against"]:
            return element_data["damage_bonus"]
        elif defender_element in element_data["weak_against"]:
            return element_data["resistance_penalty"]

        return 1.0

    def _process_skill_effects(self, effects: List[Dict], attacker, defender) -> List[Dict]:
        """处理技能效果"""
        processed_effects = []

        for effect in effects:
            effect_type = effect.get("type")

            if effect_type == "status":
                # 状态效果
                status_name = effect.get("status")
                duration = effect.get("duration", 1)
                chance = effect.get("chance", 1.0)

                if random.random() < chance:
                    processed_effects.append(
                        {
                            "type": "apply_status",
                            "target": "defender",
                            "status": status_name,
                            "duration": duration,
                        }
                    )

            elif effect_type == "damage_over_time":
                # 持续伤害
                processed_effects.append(
                    {
                        "type": "dot",
                        "target": "defender",
                        "damage": effect.get("damage", 0),
                        "duration": effect.get("duration", 3),
                        "element": effect.get("element", "physical"),
                    }
                )

            elif effect_type == "heal":
                # 治疗效果
                heal_amount = effect.get("amount", 0)
                if isinstance(heal_amount, str) and "%" in heal_amount:
                    # 百分比治疗
                    percentage = float(heal_amount.strip("%")) / 100
                    heal_amount = int(attacker.attributes.get("max_health", 100) * percentage)

                processed_effects.append(
                    {"type": "heal", "target": effect.get("target", "self"), "amount": heal_amount}
                )

        return processed_effects

    def get_ai_action(self, character, combat_state: "CombatState") -> Dict[str, Any]:
        """
        AI决策系统
        根据行为树和当前状态选择行动
        """
        # 获取AI行为模式
        behavior = character.ai_behavior or "defensive"
        behavior_tree = self.combat_data["ai_behavior"]["behavior_trees"].get(behavior, {})

        # 评估威胁
        threats = self._calculate_threats(character, combat_state)

        # 检查生存状况
        health_percentage = character.health / character.max_health
        retreat_threshold = behavior_tree.get("retreat_threshold", 0.3)

        if health_percentage < retreat_threshold:
            # 需要撤退或防御
            if character.has_skill("teleport") and character.can_use_skill("teleport"):
                return {"action": ActionType.USE_SKILL, "skill": "teleport"}
            elif random.random() < 0.7:
                return {"action": ActionType.DEFEND}
            else:
                return {"action": ActionType.FLEE}

        # 根据优先级选择目标
        priority = behavior_tree.get("priority", [])
        target = self._select_target(character, combat_state, priority, threats)

        if not target:
            return {"action": ActionType.DEFEND}

        # 选择技能
        skill_preference = behavior_tree.get("skill_preference", "balanced")
        available_skills = character.get_available_skills()

        if available_skills:
            skill = self._select_skill(available_skills, skill_preference, character, target)
            if skill:
                return {"action": ActionType.USE_SKILL, "skill": skill, "target": target}

        # 默认攻击
        return {"action": ActionType.ATTACK, "target": target}

    def _calculate_threats(self, character, combat_state: "CombatState") -> Dict[str, float]:
        """计算威胁值"""
        threats: Dict[str, Any] = {}
        threat_formula = self.combat_data["ai_behavior"]["threat_calculation"]["formula"]
        modifiers = self.combat_data["ai_behavior"]["threat_calculation"]["modifiers"]

        for participant in combat_state.get_enemies(character):
            # 基础威胁值
            damage_dealt = combat_state.get_damage_dealt_by(participant.id)
            healing_done = combat_state.get_healing_done_by(participant.id)
            taunt_value = participant.attributes.get("taunt", 0)

            base_threat = damage_dealt * 1.0 + healing_done * 0.5 + taunt_value

            # 应用修正
            for status, modifier in modifiers.items():
                if participant.has_status(status):
                    base_threat *= modifier

            threats[participant.id] = base_threat

        return threats

    def _select_target(
        self, character, combat_state: "CombatState", priority: List[str], threats: Dict[str, float]
    ) -> Optional[Any]:
        """选择目标"""
        enemies = combat_state.get_enemies(character)
        if not enemies:
            return None

        for criteria in priority:
            if criteria == "highest_damage":
                # 选择输出最高的敌人
                return max(enemies, key=lambda e: e.attributes.get("attack_power", 0))

            elif criteria == "lowest_health_enemy":
                # 选择血量最低的敌人
                return min(enemies, key=lambda e: e.health / e.max_health)

            elif criteria == "closest_enemy":
                # 选择最近的敌人
                return min(enemies, key=lambda e: combat_state.get_distance(character, e))

            elif criteria == "highest_threat":
                # 选择威胁最高的敌人
                return max(enemies, key=lambda e: threats.get(e.id, 0))

        # 默认选择第一个敌人
        return enemies[0]

    def _select_skill(self, skills: List[Any], preference: str, character, target) -> Optional[Any]:
        """选择技能"""
        # 根据偏好过滤技能
        if preference == "offensive":
            filtered = [s for s in skills if s.type in ["damage", "debuff"]]
        elif preference == "defensive":
            filtered = [s for s in skills if s.type in ["heal", "buff", "shield"]]
        elif preference == "utility":
            filtered = [s for s in skills if s.type in ["control", "dispel", "utility"]]
        else:
            filtered = skills

        if not filtered:
            filtered = skills

        # 评估每个技能的价值
        best_skill = None
        best_value = -1

        for skill in filtered:
            value = self._evaluate_skill_value(skill, character, target)
            if value > best_value:
                best_value = value
                best_skill = skill

        return best_skill

    def _evaluate_skill_value(self, skill, character, target) -> float:
        """评估技能价值"""
        value = 0

        # 伤害技能
        if skill.type == "damage":
            # 预估伤害
            estimated_damage = skill.base_damage * skill.damage_multiplier
            # 考虑目标剩余血量
            overkill = max(0, estimated_damage - target.health)
            value = estimated_damage - overkill * 0.5

            # 元素克制加成
            if hasattr(skill, "element") and hasattr(target, "element"):
                multiplier = self._get_element_multiplier(skill.element, target.element)
                value *= multiplier

        # 治疗技能
        elif skill.type == "heal":
            # 需要治疗的量
            missing_health = character.max_health - character.health
            heal_amount = min(skill.heal_amount, missing_health)
            value = heal_amount * 2  # 治疗价值更高

        # 控制技能
        elif skill.type == "control":
            # 根据目标威胁程度
            target_threat = target.attributes.get("attack_power", 0) * (
                target.health / target.max_health
            )
            value = target_threat * skill.duration

        # 冷却时间惩罚
        if hasattr(skill, "cooldown") and skill.cooldown > 0:
            value *= 1 - skill.cooldown / 10

        # 消耗惩罚
        if hasattr(skill, "mana_cost"):
            mana_percentage = character.mana / character.max_mana
            if mana_percentage < 0.3:
                value *= 0.5

        return value


class Combat:
    """战斗实例类"""

    def __init__(self, system: CombatSystemV3, combat_id: str, participants: List[Any]) -> None:
        self.system = system
        self.combat_id = combat_id
        self.participants = {p.id: p for p in participants}
        self.turn_order: List[Any] = []
        self.current_turn = 0
        self.round = 1
        self.phase = CombatPhase.INITIALIZATION
        self.combat_log: List[Dict[str, Any]] = []
        self.state = CombatState(participants)

        # 初始化战斗
        self._initialize_combat()

    def add_participant(self, participant, team: str = "team") -> None:
        """Add a participant after combat creation."""
        self.participants[participant.id] = participant
        setattr(participant, "team", team)
        self.state.participants[participant.id] = participant
        self.turn_order.append(participant)
        self._calculate_initiative()

    def is_combat_over(self) -> bool:
        return self.phase == CombatPhase.END_TURN or self._check_combat_end()

    def _initialize_combat(self) -> None:
        """初始化战斗"""
        self.log("=== 战斗开始 ===")

        # 检测参与者
        self._detect_participants()

        # 计算先攻
        self._calculate_initiative()

        # 应用地形效果
        self._apply_terrain_effects()

        # 激活战前增益
        self._activate_pre_combat_buffs()

        self.phase = CombatPhase.ACTION
        self.log(f"战斗顺序: {[p.name for p in self.turn_order]}")

    def _detect_participants(self) -> None:
        """检测所有参与者"""
        # 将参与者分组
        teams: Dict[str, Any] = {}
        for participant in self.participants.values():
            team = getattr(participant, "team", 0)
            if team not in teams:
                teams[team] = []
            teams[team].append(participant)

        self.teams = teams
        self.log(f"检测到 {len(teams)} 个阵营，共 {len(self.participants)} 名参与者")

    def _calculate_initiative(self) -> None:
        """计算先攻顺序"""
        initiative_rolls = []

        for participant in self.participants.values():
            # 基础速度
            speed = participant.attributes.get("speed", 10)

            # 投骰子 (1-20)
            roll = random.randint(1, 20)

            # 先攻加成
            initiative_bonus = participant.attributes.get("initiative", 0)

            # 计算总先攻值
            total = speed + roll + initiative_bonus

            # 特殊修正
            modifiers = self.system.combat_data["combat_phases"]["initiative"]["modifiers"]
            for status, modifier in modifiers.items():
                if participant.has_status(status):
                    total += modifier

            initiative_rolls.append((total, participant))
            self.log(
                f"{participant.name} 先攻值: {total} (速度:{speed} + 骰子:{roll} + 加成:{initiative_bonus})"
            )

        # 按先攻值排序
        initiative_rolls.sort(key=lambda x: x[0], reverse=True)
        self.turn_order = [p for _, p in initiative_rolls]

    def _apply_terrain_effects(self) -> None:
        """应用地形效果"""
        # TODO: 实现地形系统
        pass

    def _activate_pre_combat_buffs(self) -> None:
        """激活战前增益"""
        for participant in self.participants.values():
            # 激活被动技能
            if hasattr(participant, "passive_skills"):
                for skill in participant.passive_skills:
                    self.log(f"{participant.name} 的被动技能 {skill.name} 已激活")

    def execute_turn(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行一个回合

        Args:
            action: 行动字典，包含action_type, target等

        Returns:
            执行结果
        """
        if self.phase != CombatPhase.ACTION:
            return {"success": False, "message": "当前不在行动阶段"}

        current_participant = self.turn_order[self.current_turn]
        result = {"success": False, "effects": []}

        # 检查是否可以行动
        if not self._can_act(current_participant):
            result["message"] = f"{current_participant.name} 无法行动"
            self._next_turn()
            return result

        # 执行行动
        action_type = action.get("action")

        if action_type == ActionType.ATTACK:
            result = self._execute_attack(current_participant, action.get("target"))
        elif action_type == ActionType.USE_SKILL:
            result = self._execute_skill(
                current_participant, action.get("skill"), action.get("target")
            )
        elif action_type == ActionType.DEFEND:
            result = self._execute_defend(current_participant)
        elif action_type == ActionType.FLEE:
            result = self._execute_flee(current_participant)

        # 结算阶段
        self._resolve_effects(result.get("effects", []))

        # 检查战斗结束
        if self._check_combat_end():
            self._end_combat()
        else:
            self._next_turn()

        return result

    def _can_act(self, participant) -> bool:
        """检查是否可以行动"""
        # 检查晕眩等状态
        if participant.has_status("stun") or participant.has_status("freeze"):
            return False

        # 检查是否存活
        if participant.health <= 0:
            return False

        return True

    def _execute_attack(self, attacker, target_id: str) -> Dict[str, Any]:
        """执行普通攻击"""
        target = self.participants.get(target_id)
        if not target:
            return {"success": False, "message": "无效的目标"}

        # 计算伤害
        damage_result = self.system.calculate_damage(attacker, target, "physical")

        if damage_result["hit"]:
            # 应用伤害
            target.take_damage(damage_result["damage"])
            self.log(f"{attacker.name} 攻击 {target.name}，造成 {damage_result['damage']} 点伤害")

            if damage_result["critical"]:
                self.log("暴击！")

            # 更新战斗状态
            self.state.record_damage(attacker.id, target.id, damage_result["damage"])
        else:
            self.log(f"{attacker.name} 的攻击被 {target.name} 闪避")

        return {
            "success": True,
            "damage": damage_result,
            "effects": damage_result.get("effects", []),
        }

    def _execute_skill(self, caster, skill_id: str, target_id: Optional[str]) -> Dict[str, Any]:
        """执行技能"""
        # 获取技能数据
        skill = caster.get_skill(skill_id)
        if not skill:
            return {"success": False, "message": "未找到技能"}

        # 检查是否可以使用
        if not caster.can_use_skill(skill_id):
            return {"success": False, "message": "无法使用该技能"}

        # 消耗资源
        caster.consume_skill_resources(skill)

        # 根据技能类型执行
        if skill.target_type == "single":
            target = self.participants.get(target_id)
            if not target:
                return {"success": False, "message": "无效的目标"}

            result = self._apply_skill_effect(caster, target, skill)
        elif skill.target_type == "area":
            # 范围技能
            targets = self._get_area_targets(caster, skill)
            results = []
            for target in targets:
                results.append(self._apply_skill_effect(caster, target, skill))
            result = {"success": True, "results": results}
        elif skill.target_type == "self":
            result = self._apply_skill_effect(caster, caster, skill)

        # 记录技能使用
        self.log(f"{caster.name} 使用了 {skill.name}")

        # 触发技能冷却
        caster.trigger_skill_cooldown(skill_id)

        return result

    def _apply_skill_effect(self, caster, target, skill) -> Dict[str, Any]:
        """应用技能效果"""
        result = {"success": True, "effects": []}

        # 伤害技能
        if skill.effect_type == "damage":
            damage_type = skill.damage_type or "magical"
            damage_result = self.system.calculate_damage(
                caster, target, damage_type, skill.to_dict()
            )

            if damage_result["hit"]:
                target.take_damage(damage_result["damage"])
                result["damage"] = damage_result["damage"]
                result["effects"].extend(damage_result.get("effects", []))

        # 治疗技能
        elif skill.effect_type == "heal":
            heal_amount = skill.heal_amount
            if hasattr(caster, "spell_power"):
                heal_amount += caster.spell_power * 0.5

            actual_heal = target.heal(heal_amount)
            result["heal"] = actual_heal
            self.log(f"{target.name} 恢复了 {actual_heal} 点生命")

        # 增益/减益技能
        elif skill.effect_type in ["buff", "debuff"]:
            for status in skill.status_effects:
                target.add_status_effect(status["name"], status["duration"])
                result["effects"].append(
                    {"type": "status", "name": status["name"], "target": target.id}
                )

        return result

    def _execute_defend(self, defender) -> Dict[str, Any]:
        """执行防御"""
        # 添加防御状态
        defender.add_status_effect("defending", 1)
        self.log(f"{defender.name} 进入防御姿态")

        return {
            "success": True,
            "effects": [{"type": "status", "name": "defending", "target": defender.id}],
        }

    def _execute_flee(self, fleer) -> Dict[str, Any]:
        """执行逃跑"""
        # 逃跑成功率
        flee_chance = 0.3 + (fleer.attributes.get("speed", 10) / 100)

        if random.random() < flee_chance:
            # 逃跑成功
            self.participants.pop(fleer.id)
            self.turn_order.remove(fleer)
            self.log(f"{fleer.name} 成功逃离战场")

            return {"success": True, "fled": True}
        else:
            # 逃跑失败
            self.log(f"{fleer.name} 逃跑失败")
            return {"success": False, "message": "逃跑失败"}

    def _resolve_effects(self, effects: List[Dict]) -> None:
        """结算效果"""
        for effect in effects:
            effect_type = effect.get("type")

            if effect_type == "apply_status":
                target = self.participants.get(effect["target"])
                if target:
                    target.add_status_effect(effect["status"], effect["duration"])

            elif effect_type == "dot":
                # 添加持续伤害
                target = self.participants.get(effect["target"])
                if target:
                    target.add_dot_effect(effect)

            elif effect_type == "heal":
                target = self.participants.get(effect["target"])
                if target:
                    target.heal(effect["amount"])

    def _get_area_targets(self, caster, skill) -> List[Any]:
        """获取范围目标"""
        targets = []
        range_type = skill.range_type

        if range_type == "all_enemies":
            team = getattr(caster, "team", 0)
            for participant in self.participants.values():
                if getattr(participant, "team", -1) != team and participant.health > 0:
                    targets.append(participant)

        elif range_type == "all_allies":
            team = getattr(caster, "team", 0)
            for participant in self.participants.values():
                if getattr(participant, "team", -1) == team and participant.health > 0:
                    targets.append(participant)

        elif range_type == "radius":
            # TODO: 实现基于距离的范围判定
            pass

        return targets

    def _next_turn(self) -> None:
        """进入下一回合"""
        # 回合结束处理
        current_participant = self.turn_order[self.current_turn]
        self._end_turn_effects(current_participant)

        # 下一个参与者
        self.current_turn = (self.current_turn + 1) % len(self.turn_order)

        # 如果回到第一个人，新的一轮
        if self.current_turn == 0:
            self.round += 1
            self.log(f"\n=== 第 {self.round} 轮 ===")

    def _end_turn_effects(self, participant) -> None:
        """回合结束效果"""
        # 持续时间递减
        participant.update_status_durations()

        # 持续伤害
        participant.process_dot_effects()

        # 回复效果
        if participant.has_status("regeneration"):
            regen_amount = participant.max_health * 0.05
            participant.heal(regen_amount)

        # 触发回合结束效果
        # TODO: 实现更多回合结束效果

    def _check_combat_end(self) -> bool:
        """检查战斗是否结束"""
        # 统计各队存活人数
        team_alive: Dict[int, int] = {}
        for participant in self.participants.values():
            if participant.health > 0:
                team = getattr(participant, "team", 0)
                team_alive[team] = team_alive.get(team, 0) + 1

        # 只剩一个队伍有存活者
        return len(team_alive) <= 1

    def _end_combat(self) -> None:
        """结束战斗"""
        self.phase = CombatPhase.END_TURN
        self.log("\n=== 战斗结束 ===")

        # 确定胜利方
        winners = []
        for participant in self.participants.values():
            if participant.health > 0:
                winners.append(participant)

        if winners:
            self.log(f"胜利者: {', '.join([w.name for w in winners])}")
        else:
            self.log("战斗以平局结束")

        # 分发奖励
        self._distribute_rewards(winners)

        # 清理战斗
        del self.system.active_combats[self.combat_id]

    def _distribute_rewards(self, winners: List[Any]) -> None:
        """分发战斗奖励"""
        if not winners:
            return

        # 计算总经验值
        total_exp = 0
        for participant in self.participants.values():
            if participant.health <= 0 and participant not in winners:
                # 击败的敌人
                enemy_level = getattr(participant, "level", 1)
                base_exp = enemy_level * 10
                total_exp += base_exp

        # 分配经验
        if total_exp > 0:
            exp_per_winner = total_exp // len(winners)
            for winner in winners:
                winner.gain_experience(exp_per_winner)
                self.log(f"{winner.name} 获得 {exp_per_winner} 点经验")

        # TODO: 实现物品掉落系统

    def log(self, message: str) -> None:
        """记录战斗日志"""
        entry = {"round": self.round, "turn": self.current_turn, "message": message}
        self.combat_log.append(entry)
        logger.info(f"[Combat {self.combat_id}] {message}")


class CombatState:
    """战斗状态管理"""

    def __init__(self, participants: List[Any]) -> None:
        self.participants = {p.id: p for p in participants}
        self.damage_dealt: Dict[str, Dict[str, int]] = {}  # {attacker_id: {target_id: damage}}
        self.healing_done: Dict[str, int] = {}  # {healer_id: total_healing}
        self.distances: Dict[Tuple[str, str], float] = {}  # {(id1, id2): distance}

    def record_damage(self, attacker_id: str, target_id: str, damage: int) -> None:
        """记录伤害"""
        if attacker_id not in self.damage_dealt:
            self.damage_dealt[attacker_id] = {}

        if target_id not in self.damage_dealt[attacker_id]:
            self.damage_dealt[attacker_id][target_id] = 0

        self.damage_dealt[attacker_id][target_id] += damage

    def record_healing(self, healer_id: str, target_id: str, amount: int) -> None:
        """记录治疗量"""
        if healer_id not in self.healing_done:
            self.healing_done[healer_id] = 0

        self.healing_done[healer_id] += amount

    def get_healing_done_by(self, participant_id: str) -> int:
        """获取某人完成的治疗总量"""
        return self.healing_done.get(participant_id, 0)

    def get_damage_dealt_by(self, participant_id: str) -> int:
        """获取某人造成的总伤害"""
        if participant_id not in self.damage_dealt:
            return 0

        return sum(self.damage_dealt[participant_id].values())

    def get_enemies(self, character) -> List[Any]:
        """获取敌人列表"""
        team = getattr(character, "team", 0)
        enemies = []

        for participant in self.participants.values():
            if getattr(participant, "team", -1) != team and participant.health > 0:
                enemies.append(participant)

        return enemies

    def get_allies(self, character) -> List[Any]:
        """获取队友列表"""
        team = getattr(character, "team", 0)
        allies = []

        for participant in self.participants.values():
            if (
                getattr(participant, "team", -1) == team
                and participant.id != character.id
                and participant.health > 0
            ):
                allies.append(participant)

        return allies

    def get_distance(self, char1, char2) -> float:
        """获取两个角色之间的距离"""
        key = tuple(sorted([char1.id, char2.id]))
        return self.distances.get(key, 1.0)  # 默认距离1.0

    def set_distance(self, char1_id: str, char2_id: str, distance: float) -> None:
        """设置距离"""
        key = tuple(sorted([char1_id, char2_id]))
        self.distances[key] = distance


# 全局系统实例


class CombatSystem(CombatSystemV3):
    """向后兼容的 CombatSystem 包装类"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()


combat_system = CombatSystem()


# 导出便捷函数
def create_combat(participants: List[Any]) -> Combat:
    """创建战斗的便捷函数"""
    import uuid

    combat_id = str(uuid.uuid4())
    return combat_system.create_combat(combat_id, participants)


def calculate_damage(attacker, defender, damage_type: str = "physical") -> Dict[str, Any]:
    """计算伤害的便捷函数"""
    return combat_system.calculate_damage(attacker, defender, damage_type)
