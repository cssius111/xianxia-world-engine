# xwe/core/roll_system/character_roller.py
"""
角色随机生成器

提供最基本的 Roll 功能，用于创建新的角色初始面板。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random

from .roll_data import ROLL_DATA


@dataclass
class RollResult:
    """一次 Roll 的结果"""

    name: str
    gender: str
    identity: str
    identity_desc: str
    attributes: Dict[str, int]
    spiritual_root_type: str
    spiritual_root_elements: List[str]
    spiritual_root_desc: str
    destiny: str
    destiny_rarity: str
    destiny_desc: str
    destiny_effects: List[str] = field(default_factory=list)
    talents: List[Dict[str, str]] = field(default_factory=list)
    system: Optional[Dict[str, any]] = None
    combat_power: int = 0
    overall_rating: str = ""
    special_tags: List[str] = field(default_factory=list)


class CharacterRoller:
    """最基础的角色生成器"""

    def roll(self) -> RollResult:
        """生成一个新的 ``RollResult``"""
        name = random.choice(ROLL_DATA["names"])
        gender = random.choice(ROLL_DATA["genders"])
        id_data = random.choice(ROLL_DATA["identities"])
        root_data = random.choice(ROLL_DATA["spiritual_roots"])
        destiny_data = random.choice(ROLL_DATA["destinies"])
        talents = random.sample(ROLL_DATA["talents"], k=min(2, len(ROLL_DATA["talents"])))
        system = random.choice(ROLL_DATA["systems"])

        attributes = {
            "attack": random.randint(10, 20),
            "defense": random.randint(5, 15),
            "health": random.randint(100, 200),
            "mana": random.randint(50, 100),
            "speed": random.randint(5, 15),
            "comprehension": random.randint(5, 15),
            "luck": random.randint(5, 15),
            "constitution": random.randint(5, 15),
            "charm": random.randint(5, 15),
        }

        combat_power = (
            attributes["attack"]
            + attributes["defense"]
            + attributes["health"] // 10
        )

        overall_rating = "S" if combat_power >= 50 else "A" if combat_power >= 35 else "B"

        return RollResult(
            name=name,
            gender=gender,
            identity=id_data["name"],
            identity_desc=id_data["desc"],
            attributes=attributes,
            spiritual_root_type=root_data["type"],
            spiritual_root_elements=root_data["elements"],
            spiritual_root_desc=root_data["desc"],
            destiny=destiny_data["name"],
            destiny_rarity=destiny_data["rarity"],
            destiny_desc=destiny_data["desc"],
            destiny_effects=destiny_data.get("effects", []),
            talents=talents,
            system=system,
            combat_power=combat_power,
            overall_rating=overall_rating,
            special_tags=[],
        )
