"""
技能系统模块
管理角色的技能学习和使用
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class SkillType(Enum):
    """技能类型"""
    ATTACK = "attack"       # 攻击技能
    DEFENSE = "defense"     # 防御技能
    SUPPORT = "support"     # 辅助技能
    PASSIVE = "passive"     # 被动技能
    CULTIVATION = "cultivation"  # 修炼技能

@dataclass
class Skill:
    """技能数据类"""
    id: str
    name: str
    description: str
    skill_type: SkillType
    level: int = 1
    max_level: int = 10
    mana_cost: int = 0
    cooldown: int = 0
    effects: Dict[str, Any] = None
    requirements: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = {}
        if self.requirements is None:
            self.requirements = {}

class SkillSystem:
    """技能系统"""
    
    def __init__(self):
        self.available_skills = self._load_default_skills()
        self.learned_skills: Dict[str, Skill] = {}
        self.skill_cooldowns: Dict[str, int] = {}
    
    def _load_default_skills(self) -> Dict[str, Skill]:
        """加载默认技能"""
        return {
            "basic_sword": Skill(
                id="basic_sword",
                name="基础剑法",
                description="最基础的剑术招式",
                skill_type=SkillType.ATTACK,
                mana_cost=5,
                effects={"damage_multiplier": 1.2}
            ),
            "basic_defense": Skill(
                id="basic_defense",
                name="基础防御",
                description="提升防御力的基础技能",
                skill_type=SkillType.DEFENSE,
                mana_cost=3,
                effects={"defense_boost": 1.5}
            ),
            "meditation": Skill(
                id="meditation",
                name="冥想",
                description="恢复法力值的修炼技能",
                skill_type=SkillType.CULTIVATION,
                mana_cost=0,
                effects={"mana_regen": 10}
            )
        }
    
    def learn_skill(self, skill_id: str) -> bool:
        """学习技能"""
        if skill_id in self.available_skills and skill_id not in self.learned_skills:
            skill = self.available_skills[skill_id]
            self.learned_skills[skill_id] = skill
            return True
        return False
    
    def use_skill(self, skill_id: str, target=None) -> Dict[str, Any]:
        """使用技能"""
        if skill_id not in self.learned_skills:
            return {"success": False, "message": "未学习该技能"}
        
        skill = self.learned_skills[skill_id]
        
        # 检查冷却
        if skill_id in self.skill_cooldowns and self.skill_cooldowns[skill_id] > 0:
            return {"success": False, "message": f"技能冷却中，剩余{self.skill_cooldowns[skill_id]}回合"}
        
        # 设置冷却
        if skill.cooldown > 0:
            self.skill_cooldowns[skill_id] = skill.cooldown
        
        return {
            "success": True,
            "skill": skill,
            "effects": skill.effects,
            "message": f"使用了{skill.name}！"
        }
    
    def update_cooldowns(self):
        """更新冷却时间"""
        for skill_id in list(self.skill_cooldowns.keys()):
            if self.skill_cooldowns[skill_id] > 0:
                self.skill_cooldowns[skill_id] -= 1
                if self.skill_cooldowns[skill_id] <= 0:
                    del self.skill_cooldowns[skill_id]
    
    def get_skill_info(self, skill_id: str) -> Optional[Skill]:
        """获取技能信息"""
        return self.available_skills.get(skill_id) or self.learned_skills.get(skill_id)

__all__ = ["SkillSystem", "Skill", "SkillType"]
