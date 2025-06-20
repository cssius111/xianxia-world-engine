"""
XWE V2 Cultivation System

Domain models for cultivation mechanics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class CultivationRealm(Enum):
    """Cultivation realms in order."""

    QI_GATHERING = ("聚气期", 1, 9)  # name, min_level, max_level
    FOUNDATION_ESTABLISHMENT = ("筑基期", 10, 19)
    GOLDEN_CORE = ("金丹期", 20, 29)
    NASCENT_SOUL = ("元婴期", 30, 39)
    DEITY_TRANSFORMATION = ("化神期", 40, 49)
    VOID_REFINEMENT = ("炼虚期", 50, 59)
    BODY_INTEGRATION = ("合体期", 60, 69)
    MAHAYANA = ("大乘期", 70, 79)
    TRIBULATION_CROSSING = ("渡劫期", 80, 89)

    def __init__(self, chinese_name: str, min_level: int, max_level: int):
        self.chinese_name = chinese_name
        self.min_level = min_level
        self.max_level = max_level


@dataclass
class CultivationRequirement:
    """Requirements for cultivation advancement."""

    qi_amount: int = 0
    spirit_stones: int = 0
    comprehension: int = 0
    special_items: List[str] = field(default_factory=list)
    tribulation: bool = False


@dataclass
class CultivationPath:
    """A specific cultivation path/method."""

    id: str
    name: str
    description: str
    element_affinities: List[str] = field(default_factory=list)
    stat_bonuses: Dict[str, float] = field(default_factory=dict)
    special_abilities: List[str] = field(default_factory=list)
    requirements: Dict[str, int] = field(default_factory=dict)  # spirit_root -> min_value


class CultivationSystem:
    """System for managing cultivation mechanics."""

    def __init__(self):
        self.paths: Dict[str, CultivationPath] = {}
        self.realm_requirements: Dict[CultivationRealm, CultivationRequirement] = {
            CultivationRealm.QI_GATHERING: CultivationRequirement(qi_amount=100),
            CultivationRealm.FOUNDATION_ESTABLISHMENT: CultivationRequirement(
                qi_amount=1000, spirit_stones=10, tribulation=True
            ),
            CultivationRealm.GOLDEN_CORE: CultivationRequirement(
                qi_amount=10000, spirit_stones=100, comprehension=50, tribulation=True
            ),
            # Add more realm requirements as needed
        }

    def get_realm_by_level(self, level: int) -> Optional[CultivationRealm]:
        """Get cultivation realm based on level."""
        for realm in CultivationRealm:
            if realm.min_level <= level <= realm.max_level:
                return realm
        return None

    def get_realm_progress(self, level: int) -> Tuple[int, int]:
        """Get progress within current realm (current, max)."""
        realm = self.get_realm_by_level(level)
        if not realm:
            return 0, 0

        level_in_realm = level - realm.min_level + 1
        max_levels = realm.max_level - realm.min_level + 1
        return level_in_realm, max_levels

    def can_breakthrough(self, character_data: Dict) -> bool:
        """Check if character can breakthrough to next realm."""
        level = character_data.get("cultivation_level", 1)
        realm = self.get_realm_by_level(level)

        if not realm:
            return False

        # Check if at realm boundary
        if level != realm.max_level:
            return False

        # Get next realm
        next_realm = None
        for r in CultivationRealm:
            if r.min_level == realm.max_level + 1:
                next_realm = r
                break

        if not next_realm:
            return False

        # Check requirements
        req = self.realm_requirements.get(next_realm)
        if not req:
            return True  # No specific requirements

        # Check qi
        if character_data.get("qi", 0) < req.qi_amount:
            return False

        # Check spirit stones
        if character_data.get("spirit_stones", 0) < req.spirit_stones:
            return False

        # Check comprehension
        if character_data.get("comprehension", 0) < req.comprehension:
            return False

        # Check special items
        inventory = set(character_data.get("inventory", []))
        if not all(item in inventory for item in req.special_items):
            return False

        return True

    def calculate_cultivation_speed(self, character_data: Dict) -> float:
        """Calculate cultivation speed multiplier."""
        base_speed = 1.0

        # Spirit root quality affects speed
        spirit_root_purity = sum(character_data.get("spirit_root", {}).values())
        if spirit_root_purity > 80:  # High purity
            base_speed *= 2.0
        elif spirit_root_purity > 60:  # Good purity
            base_speed *= 1.5
        elif spirit_root_purity < 40:  # Poor purity
            base_speed *= 0.7

        # Comprehension affects speed
        comprehension = character_data.get("comprehension", 50)
        base_speed *= comprehension / 50

        # Cultivation method affects speed
        if character_data.get("cultivation_path"):
            path = self.paths.get(character_data["cultivation_path"])
            if path:
                base_speed *= path.stat_bonuses.get("cultivation_speed", 1.0)

        # Environment affects speed (placeholder)
        # Could check location, time, special events, etc.

        return base_speed

    def register_path(self, path: CultivationPath) -> None:
        """Register a cultivation path."""
        self.paths[path.id] = path

    def get_compatible_paths(self, spirit_root: Dict[str, int]) -> List[CultivationPath]:
        """Get cultivation paths compatible with spirit root."""
        compatible = []

        for path in self.paths.values():
            # Check requirements
            meets_requirements = True
            for element, min_value in path.requirements.items():
                if spirit_root.get(element, 0) < min_value:
                    meets_requirements = False
                    break

            if meets_requirements:
                compatible.append(path)

        return compatible
