"""
修炼系统
管理角色的修炼进度、境界突破等
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random
import math


class CultivationRealm(Enum):
    """修炼境界"""
    MORTAL = ("凡人", 0, 0)
    QI_REFINING = ("炼气期", 1, 9)
    FOUNDATION = ("筑基期", 10, 19)
    GOLDEN_CORE = ("金丹期", 20, 29)
    NASCENT_SOUL = ("元婴期", 30, 39)
    SOUL_FORMATION = ("化神期", 40, 49)
    VOID_REFINEMENT = ("合体期", 50, 59)
    TRIBULATION = ("大乘期", 60, 69)
    IMMORTAL = ("仙人", 70, 99)
    
    def __init__(self, name: str, min_level: int, max_level: int):
        self.chinese_name = name
        self.min_level = min_level
        self.max_level = max_level


@dataclass
class CultivationTechnique:
    """修炼功法"""
    id: str
    name: str
    description: str
    element: str  # 五行属性
    grade: str    # 功法品级：凡级、玄级、地级、天级、仙级
    exp_multiplier: float
    special_effects: List[str]
    requirements: Dict[str, int]  # 属性要求


class CultivationSystem:
    """
    修炼系统管理器
    
    处理修炼、突破、功法等相关逻辑
    """
    
    def __init__(self):
        self.techniques: Dict[str, CultivationTechnique] = {}
        self.realm_breakthroughs: Dict[str, Dict[str, Any]] = {}
        
        # 初始化基础功法
        self._init_techniques()
        self._init_breakthrough_requirements()
        
    def _init_techniques(self) -> None:
        """初始化修炼功法"""
        # 基础功法
        basic_technique = CultivationTechnique(
            id="basic_qi_refining",
            name="基础炼气诀",
            description="最基础的炼气功法，适合初学者",
            element="neutral",
            grade="凡级",
            exp_multiplier=1.0,
            special_effects=[],
            requirements={}
        )
        self.techniques[basic_technique.id] = basic_technique
        
        # 五行功法
        elements = {
            "fire": ("烈火真诀", "修炼火属性真气，攻击力强大"),
            "water": ("玄水心经", "修炼水属性真气，恢复力出众"),
            "wood": ("青木长生诀", "修炼木属性真气，生命力旺盛"),
            "metal": ("金刚不坏功", "修炼金属性真气，防御力惊人"),
            "earth": ("厚土玄功", "修炼土属性真气，根基稳固")
        }
        
        for element, (name, desc) in elements.items():
            technique = CultivationTechnique(
                id=f"{element}_technique",
                name=name,
                description=desc,
                element=element,
                grade="玄级",
                exp_multiplier=1.5,
                special_effects=[f"{element}_affinity"],
                requirements={"comprehension": 30}
            )
            self.techniques[technique.id] = technique
    
    def _init_breakthrough_requirements(self) -> None:
        """初始化突破要求"""
        self.realm_breakthroughs = {
            "炼气期": {
                "exp_required": 1000,
                "resources": {"spirit_stones": 10},
                "success_rate_base": 0.9,
                "tribulation": False
            },
            "筑基期": {
                "exp_required": 10000,
                "resources": {"spirit_stones": 100, "foundation_pill": 1},
                "success_rate_base": 0.7,
                "tribulation": False
            },
            "金丹期": {
                "exp_required": 100000,
                "resources": {"spirit_stones": 1000, "golden_core_materials": 3},
                "success_rate_base": 0.5,
                "tribulation": True,
                "tribulation_difficulty": 1
            },
            "元婴期": {
                "exp_required": 1000000,
                "resources": {"spirit_stones": 10000, "soul_crystals": 5},
                "success_rate_base": 0.3,
                "tribulation": True,
                "tribulation_difficulty": 3
            }
        }
    
    def calculate_cultivation_exp(self, character: Any, duration: float, 
                                location_bonus: float = 1.0) -> int:
        """
        计算修炼获得的经验
        
        Args:
            character: 角色对象
            duration: 修炼时长（小时）
            location_bonus: 地点加成
            
        Returns:
            获得的修炼经验
        """
        # 基础经验 = 悟性 * 时长 * 10
        base_exp = character.attributes.comprehension * duration * 10
        
        # 功法加成
        technique_multiplier = 1.0
        if hasattr(character, 'cultivation_technique'):
            technique = self.techniques.get(character.cultivation_technique)
            if technique:
                technique_multiplier = technique.exp_multiplier
        
        # 灵根加成
        spiritual_root_bonus = self._calculate_spiritual_root_bonus(character)
        
        # 最终经验
        total_exp = int(base_exp * technique_multiplier * spiritual_root_bonus * location_bonus)
        
        return total_exp
    
    def _calculate_spiritual_root_bonus(self, character: Any) -> float:
        """计算灵根加成"""
        if not hasattr(character, 'spiritual_root'):
            return 1.0
        
        # 灵根纯度越高，加成越大
        root_values = list(character.spiritual_root.values())
        if not root_values:
            return 1.0
        
        # 单灵根最高3倍加成，五灵根1倍
        max_value = max(root_values)
        num_roots = len([v for v in root_values if v > 20])
        
        if num_roots == 1:
            return 1.0 + (max_value / 100) * 2  # 最高3倍
        elif num_roots == 2:
            return 1.0 + (max_value / 100) * 1  # 最高2倍
        else:
            return 1.0 + (max_value / 100) * 0.5  # 最高1.5倍
    
    def attempt_breakthrough(self, character: Any) -> Tuple[bool, str]:
        """
        尝试突破境界
        
        Args:
            character: 角色对象
            
        Returns:
            (是否成功, 结果描述)
        """
        current_realm = self._get_realm_by_level(character.attributes.cultivation_level)
        next_realm = self._get_next_realm(current_realm)
        
        if not next_realm:
            return False, "已达到最高境界"
        
        # 检查突破要求
        requirements = self.realm_breakthroughs.get(next_realm.chinese_name, {})
        
        # 检查经验
        if character.attributes.cultivation_exp < requirements.get("exp_required", 0):
            return False, "修为不足，无法突破"
        
        # 检查资源
        for resource, amount in requirements.get("resources", {}).items():
            if not self._check_resource(character, resource, amount):
                return False, f"缺少突破所需的{resource}"
        
        # 计算成功率
        success_rate = self._calculate_breakthrough_success_rate(character, requirements)
        
        # 尝试突破
        if random.random() < success_rate:
            # 成功突破
            self._apply_breakthrough(character, next_realm)
            
            # 如果有天劫
            if requirements.get("tribulation", False):
                tribulation_result = self._face_tribulation(
                    character, 
                    requirements.get("tribulation_difficulty", 1)
                )
                if not tribulation_result:
                    return False, "突破成功但未能渡过天劫，境界跌落"
            
            return True, f"成功突破到{next_realm.chinese_name}！"
        else:
            # 突破失败
            self._apply_breakthrough_failure(character)
            return False, "突破失败，需要稳固修为后再试"
    
    def _get_realm_by_level(self, level: int) -> Optional[CultivationRealm]:
        """根据等级获取境界"""
        for realm in CultivationRealm:
            if realm.min_level <= level <= realm.max_level:
                return realm
        return None
    
    def _get_next_realm(self, current_realm: CultivationRealm) -> Optional[CultivationRealm]:
        """获取下一个境界"""
        realms = list(CultivationRealm)
        current_index = realms.index(current_realm)
        
        if current_index < len(realms) - 1:
            return realms[current_index + 1]
        return None
    
    def _check_resource(self, character: Any, resource: str, amount: int) -> bool:
        """检查资源是否足够"""
        if resource == "spirit_stones":
            return character.get_total_lingshi() >= amount
        elif hasattr(character.inventory, 'get_item_count'):
            return character.inventory.get_item_count(resource) >= amount
        return False
    
    def _calculate_breakthrough_success_rate(self, character: Any, 
                                           requirements: Dict[str, Any]) -> float:
        """计算突破成功率"""
        base_rate = requirements.get("success_rate_base", 0.5)
        
        # 悟性加成
        comprehension_bonus = character.attributes.comprehension / 200
        
        # 功法品级加成
        technique_bonus = 0
        if hasattr(character, 'cultivation_technique'):
            technique = self.techniques.get(character.cultivation_technique)
            if technique:
                grade_bonuses = {
                    "凡级": 0,
                    "玄级": 0.1,
                    "地级": 0.2,
                    "天级": 0.3,
                    "仙级": 0.5
                }
                technique_bonus = grade_bonuses.get(technique.grade, 0)
        
        # 状态加成
        state_bonus = 0
        if character.attributes.current_health == character.attributes.max_health:
            state_bonus += 0.05
        if character.attributes.current_mana == character.attributes.max_mana:
            state_bonus += 0.05
        
        total_rate = base_rate + comprehension_bonus + technique_bonus + state_bonus
        return min(0.95, max(0.05, total_rate))  # 限制在5%-95%之间
    
    def _apply_breakthrough(self, character: Any, new_realm: CultivationRealm) -> None:
        """应用突破效果"""
        # 提升境界
        character.attributes.cultivation_level = new_realm.min_level
        character.attributes.realm_name = new_realm.chinese_name
        
        # 提升属性
        character.attributes.max_health += 100 * (new_realm.min_level // 10)
        character.attributes.max_mana += 50 * (new_realm.min_level // 10)
        character.attributes.attack_power += 10 * (new_realm.min_level // 10)
        character.attributes.defense += 5 * (new_realm.min_level // 10)
        
        # 恢复状态
        character.attributes.current_health = character.attributes.max_health
        character.attributes.current_mana = character.attributes.max_mana
        
        # 消耗资源
        requirements = self.realm_breakthroughs.get(new_realm.chinese_name, {})
        for resource, amount in requirements.get("resources", {}).items():
            if resource == "spirit_stones":
                character.spend_lingshi(amount)
            else:
                # 消耗物品
                pass
    
    def _apply_breakthrough_failure(self, character: Any) -> None:
        """应用突破失败的惩罚"""
        # 损失部分修为
        character.attributes.cultivation_exp = int(character.attributes.cultivation_exp * 0.9)
        
        # 受到内伤
        character.attributes.current_health = int(character.attributes.max_health * 0.5)
        character.attributes.current_mana = int(character.attributes.max_mana * 0.3)
    
    def _face_tribulation(self, character: Any, difficulty: int) -> bool:
        """
        面对天劫
        
        Args:
            character: 角色
            difficulty: 天劫难度
            
        Returns:
            是否成功渡劫
        """
        # 基础成功率
        base_rate = 0.7 - (difficulty * 0.1)
        
        # 装备加成
        equipment_bonus = 0  # TODO: 根据装备计算
        
        # 最终成功率
        success_rate = base_rate + equipment_bonus
        
        return random.random() < success_rate
    
    def get_cultivation_info(self, character: Any) -> Dict[str, Any]:
        """获取修炼信息"""
        current_realm = self._get_realm_by_level(character.attributes.cultivation_level)
        next_realm = self._get_next_realm(current_realm) if current_realm else None
        
        info = {
            "current_realm": current_realm.chinese_name if current_realm else "凡人",
            "current_level": character.attributes.cultivation_level,
            "cultivation_exp": getattr(character.attributes, 'cultivation_exp', 0),
            "next_realm": next_realm.chinese_name if next_realm else "已达巅峰",
            "can_breakthrough": False,
            "breakthrough_requirements": {}
        }
        
        if next_realm:
            requirements = self.realm_breakthroughs.get(next_realm.chinese_name, {})
            info["breakthrough_requirements"] = requirements
            info["can_breakthrough"] = (
                character.attributes.cultivation_exp >= requirements.get("exp_required", 0)
            )
        
        return info
