# core/skills.py
"""
技能系统模块

管理游戏中的所有技能，包括技能定义、释放条件和效果计算。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import logging

from ..engine.expression import ExpressionParser
from .character import Character

logger = logging.getLogger(__name__)


class SkillType(Enum):
    """技能类型"""
    ATTACK = "attack"          # 攻击
    DEFENSE = "defense"        # 防御
    HEAL = "heal"              # 治疗
    BUFF = "buff"              # 增益
    DEBUFF = "debuff"          # 减益
    CONTROL = "control"        # 控制
    MOVEMENT = "movement"      # 身法
    PASSIVE = "passive"        # 被动


class TargetType(Enum):
    """目标类型"""
    SELF = "self"              # 自身
    SINGLE_ENEMY = "single_enemy"  # 单个敌人
    SINGLE_ALLY = "single_ally"    # 单个友方
    ALL_ENEMIES = "all_enemies"    # 所有敌人
    ALL_ALLIES = "all_allies"      # 所有友方
    AREA = "area"                  # 范围（需要指定中心）


class DamageType(Enum):
    """伤害类型"""
    PHYSICAL = "physical"      # 物理
    MAGICAL = "magical"        # 法术
    TRUE = "true"              # 真实
    MIXED = "mixed"            # 混合


@dataclass
class SkillEffect:
    """技能效果"""
    effect_type: str              # 效果类型
    formula: str                  # 计算公式
    duration: int = 0             # 持续时间（回合）
    chance: float = 1.0           # 触发概率
    element: Optional[str] = None # 元素属性
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Skill:
    """
    技能类
    
    表示游戏中的一个技能。
    """
    
    # 基础信息
    id: str
    name: str
    description: str
    skill_type: SkillType
    
    # 释放条件
    mana_cost: float = 0
    stamina_cost: float = 0
    health_cost: float = 0
    cooldown: int = 0              # 冷却回合数
    cast_time: float = 0           # 施法时间
    
    # 目标
    target_type: TargetType = TargetType.SINGLE_ENEMY
    max_targets: int = 1           # 最大目标数
    range: float = 1.0             # 施法距离
    
    # 效果
    effects: List[SkillEffect] = field(default_factory=list)
    damage_type: DamageType = DamageType.PHYSICAL
    
    # 需求
    required_level: int = 1        # 需要等级
    required_realm: str = ""       # 需要境界
    required_weapon: str = ""      # 需要武器类型
    prerequisite_skills: List[str] = field(default_factory=list)  # 前置技能
    
    # 连招
    combo_with: List[str] = field(default_factory=list)  # 可连招技能
    combo_bonus: float = 1.0       # 连招加成
    
    # 其他
    tags: List[str] = field(default_factory=list)  # 标签
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    # 运行时数据
    current_cooldown: int = 0      # 当前冷却
    
    def can_use(self, caster: Character) -> tuple[bool, str]:
        """
        检查是否可以使用技能
        
        Args:
            caster: 施法者
            
        Returns:
            (是否可用, 原因)
        """
        # 检查等级
        if caster.attributes.cultivation_level < self.required_level:
            return False, f"需要修为等级 {self.required_level}"
        
        # 检查境界
        if self.required_realm and caster.attributes.realm_name != self.required_realm:
            return False, f"需要境界 {self.required_realm}"
        
        # 检查资源
        if caster.attributes.current_mana < self.mana_cost:
            return False, "法力不足"
        
        if caster.attributes.current_stamina < self.stamina_cost:
            return False, "体力不足"
        
        if self.health_cost > 0 and caster.attributes.current_health <= self.health_cost:
            return False, "生命值不足"
        
        # 检查冷却
        if self.current_cooldown > 0:
            return False, f"技能冷却中（{self.current_cooldown}回合）"
        
        # 检查前置技能
        for prereq in self.prerequisite_skills:
            if not caster.has_skill(prereq):
                return False, f"需要前置技能: {prereq}"
        
        return True, "可以使用"
    
    def consume_resources(self, caster: Character):
        """
        消耗资源
        
        Args:
            caster: 施法者
        """
        caster.consume_mana(self.mana_cost)
        caster.consume_stamina(self.stamina_cost)
        
        if self.health_cost > 0:
            caster.take_damage(self.health_cost, "skill_cost")
        
        # 设置冷却
        self.current_cooldown = self.cooldown
    
    def reduce_cooldown(self):
        """减少冷却时间"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def reset_cooldown(self):
        """重置冷却"""
        self.current_cooldown = 0
    
    @classmethod
    def from_data(cls, skill_data: Dict[str, Any]) -> 'Skill':
        """
        从数据创建技能
        
        Args:
            skill_data: 技能数据
            
        Returns:
            技能对象
        """
        # 解析效果
        effects = []
        for effect_data in skill_data.get('effects', []):
            effect = SkillEffect(
                effect_type=effect_data['type'],
                formula=effect_data['formula'],
                duration=effect_data.get('duration', 0),
                chance=effect_data.get('chance', 1.0),
                element=effect_data.get('element'),
                extra_params=effect_data.get('params', {})
            )
            effects.append(effect)
        
        # 创建技能
        skill = cls(
            id=skill_data['id'],
            name=skill_data['name'],
            description=skill_data['description'],
            skill_type=SkillType(skill_data['type']),
            mana_cost=skill_data.get('mana_cost', 0),
            stamina_cost=skill_data.get('stamina_cost', 0),
            health_cost=skill_data.get('health_cost', 0),
            cooldown=skill_data.get('cooldown', 0),
            cast_time=skill_data.get('cast_time', 0),
            target_type=TargetType(skill_data.get('target_type', 'single_enemy')),
            max_targets=skill_data.get('max_targets', 1),
            range=skill_data.get('range', 1.0),
            effects=effects,
            damage_type=DamageType(skill_data.get('damage_type', 'physical')),
            required_level=skill_data.get('required_level', 1),
            required_realm=skill_data.get('required_realm', ''),
            required_weapon=skill_data.get('required_weapon', ''),
            prerequisite_skills=skill_data.get('prerequisite_skills', []),
            combo_with=skill_data.get('combo_with', []),
            combo_bonus=skill_data.get('combo_bonus', 1.0),
            tags=skill_data.get('tags', []),
            extra_data=skill_data.get('extra', {})
        )
        
        return skill


class SkillSystem:
    """
    技能系统管理器
    
    负责技能的加载、管理和效果计算。
    """
    
    def __init__(self, data_loader, expression_parser: ExpressionParser):
        """
        初始化技能系统
        
        Args:
            data_loader: 数据加载器
            expression_parser: 表达式解析器
        """
        self.data_loader = data_loader
        self.parser = expression_parser
        self.skills: Dict[str, Skill] = {}
        self.skill_callbacks: Dict[str, List[Callable]] = {}
        
        # 加载技能数据
        self._load_skills()
    
    def _load_skills(self):
        """加载技能数据"""
        try:
            skill_data = self.data_loader.get_skill_data()
            
            for category in skill_data.get('skill_categories', []):
                for skill_info in category.get('skills', []):
                    skill = Skill.from_data(skill_info)
                    self.skills[skill.id] = skill
                    
            logger.info(f"加载了 {len(self.skills)} 个技能")
            
        except Exception as e:
            logger.error(f"加载技能数据失败: {e}")
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """
        获取技能
        
        Args:
            skill_id: 技能ID
            
        Returns:
            技能对象，如果不存在则返回None
        """
        return self.skills.get(skill_id)
    
    def get_character_skills(self, character: Character) -> List[Skill]:
        """
        获取角色拥有的技能
        
        Args:
            character: 角色
            
        Returns:
            技能列表
        """
        skills = []
        for skill_id in character.skills:
            skill = self.get_skill(skill_id)
            if skill:
                skills.append(skill)
        
        return skills
    
    def get_available_skills(self, character: Character) -> List[Skill]:
        """
        获取角色当前可用的技能
        
        Args:
            character: 角色
            
        Returns:
            可用技能列表
        """
        available = []
        
        for skill in self.get_character_skills(character):
            can_use, _ = skill.can_use(character)
            if can_use:
                available.append(skill)
        
        return available
    
    def calculate_skill_damage(self, 
                               skill: Skill,
                               caster: Character,
                               target: Character,
                               effect: SkillEffect) -> float:
        """
        计算技能伤害
        
        Args:
            skill: 技能
            caster: 施法者
            target: 目标
            effect: 效果配置
            
        Returns:
            伤害值
        """
        # 构建计算上下文
        context = {
            # 施法者属性
            'attack_power': caster.attributes.get('attack_power'),
            'spell_power': caster.attributes.get('spell_power'),
            'level': caster.attributes.cultivation_level,
            
            # 目标属性
            'target_defense': target.attributes.get('defense'),
            'target_resistance': target.attributes.get('magic_resistance'),
            
            # 技能参数
            'skill_level': 1,  # TODO: 实现技能等级系统
            'combo_bonus': skill.combo_bonus,
        }
        
        # 添加施法者所有属性
        context.update(caster.attributes.to_dict())
        
        # 计算基础伤害
        try:
            damage = self.parser.evaluate(effect.formula, context)
        except Exception as e:
            logger.error(f"计算技能伤害失败: {e}")
            damage = 0
        
        # 应用元素克制
        if effect.element and target.spiritual_root:
            damage *= self._calculate_element_bonus(
                effect.element,
                target.spiritual_root
            )
        
        return max(0, damage)
    
    def _calculate_element_bonus(self, 
                                 attack_element: str,
                                 target_spiritual_root: Dict[str, float]) -> float:
        """
        计算元素克制加成
        
        Args:
            attack_element: 攻击元素
            target_spiritual_root: 目标灵根
            
        Returns:
            伤害倍率
        """
        # 简化的五行相克
        element_counters = {
            '金': '木',
            '木': '土',
            '土': '水',
            '水': '火',
            '火': '金'
        }
        
        # 找出目标最强的灵根
        if not target_spiritual_root:
            return 1.0
        
        main_element = max(target_spiritual_root.items(), key=lambda x: x[1])[0]
        
        # 检查克制关系
        if element_counters.get(attack_element) == main_element:
            return 1.5  # 克制加成50%
        elif element_counters.get(main_element) == attack_element:
            return 0.7  # 被克制减少30%
        
        return 1.0
    
    def register_skill_callback(self, event: str, callback: Callable):
        """
        注册技能事件回调
        
        Args:
            event: 事件名称
            callback: 回调函数
        """
        if event not in self.skill_callbacks:
            self.skill_callbacks[event] = []
        
        self.skill_callbacks[event].append(callback)
    
    def trigger_skill_callbacks(self, event: str, **kwargs):
        """
        触发技能事件回调
        
        Args:
            event: 事件名称
            **kwargs: 传递给回调的参数
        """
        if event in self.skill_callbacks:
            for callback in self.skill_callbacks[event]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(f"技能回调执行失败: {e}")
    
    def update_cooldowns(self, character: Character):
        """
        更新角色技能冷却
        
        Args:
            character: 角色
        """
        for skill in self.get_character_skills(character):
            skill.reduce_cooldown()
