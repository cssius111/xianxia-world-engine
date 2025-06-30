# xwe/core/roll_system/character_roller.py
"""
角色随机生成器

提供最基本的 Roll 功能，用于创建新的角色初始面板。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random
import json
from pathlib import Path

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
    
    def __init__(self):
        """初始化角色生成器"""
        self.attribute_config = self._load_attribute_config()
        self.remaining_points = 0  # 不留可分配点数
    
    def _load_attribute_config(self) -> Dict:
        """加载属性配置"""
        try:
            config_path = Path(__file__).parent.parent.parent / "data" / "restructured" / "attribute_model.json"
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            # 如果加载失败，返回默认配置
            return {
                "core": ["根骨", "悟性", "神识", "机缘"],
                "advanced": ["体魄", "灵根", "意志", "魅力", "气运"],
                "range": {"min": 1, "max": 10}
            }

    def roll(self) -> RollResult:
        """生成一个新的 ``RollResult``"""
        name = random.choice(ROLL_DATA["names"])
        gender = random.choice(ROLL_DATA["genders"])
        id_data = random.choice(ROLL_DATA["identities"])
        root_data = random.choice(ROLL_DATA["spiritual_roots"])
        destiny_data = random.choice(ROLL_DATA["destinies"])
        talents = random.sample(ROLL_DATA["talents"], k=min(2, len(ROLL_DATA["talents"])))
        system = random.choice(ROLL_DATA["systems"])

        # 全随机：一次性生成全部属性，不留加点入口
        cfg = self.attribute_config
        pool = cfg["core"] + cfg["advanced"]
        attributes = {name: random.randint(cfg["range"]["min"], cfg["range"]["max"]) for name in pool}
        
        # 计算衍生属性（保留兼容性）
        base_formulas = cfg.get("base_attributes", {})
        
        # 添加一些基础属性以保持兼容
        attributes["attack"] = 10 + attributes.get("体魄", 5) * 2 + attributes.get("神识", 5)
        attributes["defense"] = 5 + attributes.get("体魄", 5) + attributes.get("根骨", 5)
        attributes["health"] = 100 + attributes.get("根骨", 5) * 20 + attributes.get("体魄", 5) * 10
        attributes["mana"] = 50 + attributes.get("灵根", 5) * 15 + attributes.get("悟性", 5) * 5
        attributes["speed"] = 10 + attributes.get("根骨", 5) // 2 + attributes.get("悟性", 5) // 2
        
        # 保留原有的一些属性以保持兼容
        attributes["comprehension"] = attributes.get("悟性", 5)
        attributes["luck"] = attributes.get("机缘", 5)
        attributes["constitution"] = attributes.get("根骨", 5)
        attributes["charm"] = attributes.get("魅力", 5)

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
