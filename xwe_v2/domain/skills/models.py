"""
XWE V2 Skills System

Domain models for character skills and abilities.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class SkillType(Enum):
    """Types of skills."""

    ATTACK = "attack"
    DEFENSE = "defense"
    SUPPORT = "support"
    PASSIVE = "passive"
    MOVEMENT = "movement"
    CULTIVATION = "cultivation"


class SkillTarget(Enum):
    """Skill targeting types."""

    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    SINGLE_ALLY = "single_ally"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"
    AREA = "area"


@dataclass
class SkillRequirement:
    """Requirements to learn or use a skill."""

    level: int = 1
    cultivation_realm: str = ""
    prerequisite_skills: List[str] = field(default_factory=list)
    attributes: Dict[str, int] = field(default_factory=dict)  # attr_name -> min_value
    spirit_root: Optional[str] = None


@dataclass
class SkillEffect:
    """Effect of using a skill."""

    damage: float = 0.0
    healing: float = 0.0
    buff: Optional[str] = None
    debuff: Optional[str] = None
    duration: int = 0
    special: Dict[str, any] = field(default_factory=dict)


@dataclass
class Skill:
    """Represents a skill or ability."""

    id: str
    name: str
    description: str
    skill_type: SkillType
    target_type: SkillTarget

    # Resource costs
    mana_cost: int = 0
    stamina_cost: int = 0
    qi_cost: int = 0
    cooldown: int = 0

    # Requirements
    requirements: SkillRequirement = field(default_factory=SkillRequirement)

    # Effects
    effects: List[SkillEffect] = field(default_factory=list)

    # Progression
    max_level: int = 10
    current_level: int = 1
    experience: int = 0

    def can_upgrade(self) -> bool:
        """Check if skill can be upgraded."""
        return self.current_level < self.max_level

    def get_effect_at_level(self, level: Optional[int] = None) -> SkillEffect:
        """Get skill effect at specific level."""
        level = level or self.current_level
        if not self.effects:
            return SkillEffect()

        # Scale effect based on level
        base_effect = self.effects[0]
        scaled_effect = SkillEffect(
            damage=base_effect.damage * (1 + (level - 1) * 0.1),
            healing=base_effect.healing * (1 + (level - 1) * 0.1),
            buff=base_effect.buff,
            debuff=base_effect.debuff,
            duration=base_effect.duration,
            special=base_effect.special.copy(),
        )
        return scaled_effect


class SkillSystem:
    """System for managing skills."""

    def __init__(self):
        self.skill_database: Dict[str, Skill] = {}
        self.skill_trees: Dict[str, List[str]] = {}  # path -> skill_ids

    def register_skill(self, skill: Skill) -> None:
        """Register a skill in the system."""
        self.skill_database[skill.id] = skill

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by ID."""
        return self.skill_database.get(skill_id)

    def can_learn_skill(self, character_data: Dict, skill_id: str) -> bool:
        """Check if a character can learn a skill."""
        skill = self.get_skill(skill_id)
        if not skill:
            return False

        req = skill.requirements

        # Check level
        if character_data.get("level", 1) < req.level:
            return False

        # Check cultivation realm
        if req.cultivation_realm:
            char_realm = character_data.get("cultivation_realm", "")
            if char_realm != req.cultivation_realm:
                return False

        # Check prerequisites
        char_skills = set(character_data.get("skills", []))
        if not all(prereq in char_skills for prereq in req.prerequisite_skills):
            return False

        # Check attributes
        char_attrs = character_data.get("attributes", {})
        for attr_name, min_value in req.attributes.items():
            if char_attrs.get(attr_name, 0) < min_value:
                return False

        # Check spirit root
        if req.spirit_root:
            char_roots = character_data.get("spirit_roots", [])
            if req.spirit_root not in char_roots:
                return False

        return True

    def get_skills_for_path(self, path: str) -> List[Skill]:
        """Get all skills for a cultivation path."""
        skill_ids = self.skill_trees.get(path, [])
        return [self.get_skill(sid) for sid in skill_ids if self.get_skill(sid)]

    def calculate_skill_damage(
        self, skill: Skill, attacker_stats: Dict, target_stats: Dict
    ) -> float:
        """Calculate skill damage based on stats."""
        effect = skill.get_effect_at_level()
        base_damage = effect.damage

        # Apply attacker stats
        if skill.skill_type == SkillType.ATTACK:
            attack_power = attacker_stats.get("attack_power", 10)
            base_damage += attack_power * 0.5

        # Apply elemental bonuses if applicable
        if "element" in effect.special:
            element = effect.special["element"]
            elem_power = attacker_stats.get(f"{element}_power", 0)
            base_damage *= 1 + elem_power / 100

        # Apply target defense
        defense = target_stats.get("defense", 0)
        final_damage = max(1, base_damage - defense * 0.3)

        return final_damage
