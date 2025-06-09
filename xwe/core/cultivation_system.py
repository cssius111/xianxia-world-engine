"""
修炼系统优化实现
使用数据驱动的方式处理境界突破和修炼逻辑
"""

import random
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from .data_manager import DM
from .formula_engine import formula_engine, calculate

logger = logging.getLogger(__name__)


class CultivationSystem:
    """
    数据驱动的修炼系统
    从JSON配置加载所有境界数据和突破逻辑
    """
    
    def __init__(self):
        self.realm_data = None
        self.formula_engine = formula_engine
        self._load_cultivation_data()
    
    def _load_cultivation_data(self):
        """加载修炼相关数据"""
        try:
            self.realm_data = DM.load("cultivation_realm")
            self.spiritual_root_data = DM.load("spiritual_root")
            logger.info("Cultivation data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load cultivation data: {e}")
            raise
    
    def get_realm_info(self, realm_id: str) -> Optional[Dict[str, Any]]:
        """获取境界信息"""
        for realm in self.realm_data["realms"]:
            if realm["id"] == realm_id:
                return realm
        return None
    
    def get_next_realm(self, current_realm_id: str) -> Optional[Dict[str, Any]]:
        """获取下一个境界"""
        realms = self.realm_data["realms"]
        for i, realm in enumerate(realms):
            if realm["id"] == current_realm_id and i < len(realms) - 1:
                return realms[i + 1]
        return None
    
    def calculate_cultivation_speed(self, player) -> float:
        """
        计算修炼速度
        使用公式: cultivation_speed
        """
        # 获取灵根品质系数
        spiritual_root_quality = self._get_spiritual_root_quality(player)
        
        # 构建计算上下文
        context = {
            "base_speed": 1.0,
            "spiritual_root_quality": spiritual_root_quality,
            "comprehension": getattr(player.attributes, "comprehension", 50) / 100,
            "environment_bonus": self._get_environment_bonus(player),
            "technique_efficiency": self._get_technique_efficiency(player)
        }
        
        # 使用公式引擎计算
        speed = calculate("cultivation_speed", **context)
        
        logger.debug(f"Cultivation speed calculated: {speed}")
        return speed
    
    def attempt_breakthrough(self, player) -> Dict[str, Any]:
        """
        尝试突破境界
        返回突破结果
        """
        result = {
            "success": False,
            "message": "",
            "effects": {},
            "penalties": {}
        }
        
        # 获取当前境界信息
        current_realm = self.get_realm_info(player.realm)
        if not current_realm:
            result["message"] = "无效的境界"
            return result
        
        # 获取下一境界
        next_realm = self.get_next_realm(player.realm)
        if not next_realm:
            result["message"] = "已达到最高境界"
            return result
        
        # 检查突破条件
        requirements = current_realm.get("breakthrough_requirements", {}).get("to_next_realm", {})
        if not self._check_breakthrough_requirements(player, requirements):
            result["message"] = "未满足突破条件"
            return result
        
        # 计算突破成功率
        success_rate = self._calculate_breakthrough_chance(player, current_realm, next_realm)
        
        # 尝试突破
        roll = random.random()
        if roll < success_rate:
            # 突破成功
            result["success"] = True
            result["message"] = f"突破成功！从{current_realm['name']}晋升到{next_realm['name']}！"
            
            # 更新玩家境界
            player.realm = next_realm["id"]
            player.realm_level = 1
            
            # 应用境界提升效果
            self._apply_realm_benefits(player, next_realm)
            result["effects"] = {
                "new_realm": next_realm["name"],
                "lifespan_bonus": next_realm.get("lifespan_bonus", 0),
                "power_multiplier": next_realm.get("power_multiplier", 1.0)
            }
            
            # 记录突破次数
            player.cultivation["breakthrough_count"] = player.cultivation.get("breakthrough_count", 0) + 1
            
        else:
            # 突破失败
            result["message"] = f"突破失败！冲击{next_realm['name']}时遭受反噬"
            
            # 应用失败惩罚
            penalty = self._apply_breakthrough_penalty(player, current_realm)
            result["penalties"] = penalty
            
            # 记录失败次数
            player.cultivation["failure_count"] = player.cultivation.get("failure_count", 0) + 1
        
        # 触发相关事件
        self._trigger_breakthrough_event(player, result)
        
        return result
    
    def cultivate(self, player, duration_hours: int = 1) -> Dict[str, Any]:
        """
        进行修炼
        返回修炼结果
        """
        results = {
            "duration": duration_hours,
            "exp_gained": 0,
            "insights": [],
            "resource_consumed": {},
            "special_events": []
        }
        
        # 计算修炼速度
        cultivation_speed = self.calculate_cultivation_speed(player)
        
        # 基础经验获取
        realm_info = self.get_realm_info(player.realm)
        base_exp = realm_info.get("power_multiplier", 1.0) * 10
        
        for hour in range(duration_hours):
            # 计算每小时经验
            hour_exp = base_exp * cultivation_speed * (1 + random.random() * 0.2)
            
            # 检查顿悟
            if self._check_enlightenment(player):
                enlightenment = self._generate_enlightenment(player)
                results["insights"].append(enlightenment)
                hour_exp *= enlightenment.get("exp_multiplier", 1.5)
            
            # 检查特殊事件
            if random.random() < 0.05:  # 5%概率触发特殊事件
                event = self._generate_cultivation_event(player)
                results["special_events"].append(event)
                hour_exp *= event.get("exp_modifier", 1.0)
            
            # 累计经验
            results["exp_gained"] += hour_exp
            
            # 消耗资源
            mana_cost = 10 * cultivation_speed
            stamina_cost = 5 * cultivation_speed
            
            player.resources["mana"] = max(0, player.resources.get("mana", 0) - mana_cost)
            player.resources["stamina"] = max(0, player.resources.get("stamina", 0) - stamina_cost)
            
            results["resource_consumed"]["mana"] = results["resource_consumed"].get("mana", 0) + mana_cost
            results["resource_consumed"]["stamina"] = results["resource_consumed"].get("stamina", 0) + stamina_cost
        
        # 应用经验
        player.exp += results["exp_gained"]
        player.cultivation["total_hours"] = player.cultivation.get("total_hours", 0) + duration_hours
        
        return results
    
    def _get_spiritual_root_quality(self, player) -> float:
        """获取灵根品质系数"""
        spiritual_root = player.spiritual_root
        if not spiritual_root:
            return 0.5
        
        # 从spiritual_root.json获取品质数据
        root_data = self.spiritual_root_data.get("spiritual_roots", {})
        quality_map = {
            "heavenly": 2.0,
            "supreme": 1.8,
            "superior": 1.5,
            "high": 1.2,
            "medium": 1.0,
            "low": 0.8,
            "inferior": 0.5
        }
        
        return quality_map.get(spiritual_root.get("quality", "medium"), 1.0)
    
    def _get_environment_bonus(self, player) -> float:
        """获取环境加成"""
        # TODO: 从地图系统获取当前位置的灵气浓度
        location = player.current_location
        if not location:
            return 0.0
        
        # 临时实现
        environment_bonuses = {
            "spiritual_mountain": 0.5,
            "sect_cultivation_room": 0.3,
            "normal": 0.0,
            "city": -0.2
        }
        
        return environment_bonuses.get(location.type, 0.0)
    
    def _get_technique_efficiency(self, player) -> float:
        """获取功法效率"""
        # TODO: 从技能系统获取当前修炼功法
        technique = player.cultivation_technique
        if not technique:
            return 0.5
        
        # 功法与境界匹配度
        if technique.get("tier", 1) >= getattr(player, "realm_level", 1):
            return technique.get("efficiency", 1.0)
        else:
            # 低级功法修炼高境界效率降低
            return technique.get("efficiency", 1.0) * 0.7
    
    def _check_breakthrough_requirements(self, player, requirements: Dict[str, Any]) -> bool:
        """检查突破条件"""
        # 检查灵力
        if "spiritual_power" in requirements:
            if player.resources.get("spiritual_power", 0) < requirements["spiritual_power"]:
                return False
        
        # 检查感悟
        if "comprehension" in requirements:
            if player.attributes.get("comprehension", 0) / 100 < requirements["comprehension"]:
                return False
        
        # 检查特殊物品
        if "special_items" in requirements:
            for item in requirements["special_items"]:
                if not player.has_item(item):
                    return False
        
        # 检查特殊条件
        if "special_condition" in requirements:
            # TODO: 实现特殊条件检查
            pass
        
        return True
    
    def _calculate_breakthrough_chance(self, player, current_realm: Dict, next_realm: Dict) -> float:
        """
        计算突破成功率
        使用公式: breakthrough_chance
        """
        # 获取基础成功率
        base_rates = self.realm_data["breakthrough_mechanics"]["base_success_rates"]
        tier_key = f"{current_realm['id']}_to_{next_realm['id']}"
        base_rate = base_rates.get(tier_key, 0.1)
        
        # 构建计算上下文
        context = {
            "base_rate": base_rate,
            "comprehension": player.attributes.get("comprehension", 50) / 100,
            "willpower": player.attributes.get("willpower", 50),
            "spiritual_root_quality": self._get_spiritual_root_quality(player),
            "failure_count": player.cultivation.get("failure_count", 0),
            "special_items": 1 if player.has_item("breakthrough_pill") else 0
        }
        
        # 使用公式引擎计算
        success_rate = calculate("breakthrough_chance", **context)
        
        # 应用上限
        max_rate = self.realm_data["breakthrough_mechanics"].get("max_rate", 0.95)
        success_rate = min(success_rate, max_rate)
        
        logger.debug(f"Breakthrough chance calculated: {success_rate}")
        return success_rate
    
    def _apply_realm_benefits(self, player, realm: Dict[str, Any]):
        """应用境界提升的好处"""
        benefits = realm.get("level_benefits", {}).get("per_level", {})
        
        for attr, value in benefits.items():
            if isinstance(value, str) and value.startswith("+"):
                # 增加属性
                amount = int(value[1:])
                if attr == "all_attributes":
                    for attribute in ["strength", "agility", "intelligence", "vitality"]:
                        player.attributes[attribute] = player.attributes.get(attribute, 0) + amount
                elif attr.startswith("max_"):
                    resource = attr[4:]  # 去掉"max_"前缀
                    player.resources[f"max_{resource}"] = player.resources.get(f"max_{resource}", 0) + amount
                else:
                    player.attributes[attr] = player.attributes.get(attr, 0) + amount
        
        # 应用寿命加成
        lifespan_bonus = realm.get("lifespan_bonus", 0)
        if lifespan_bonus:
            player.lifespan = player.lifespan + lifespan_bonus
        
        # 解锁新能力
        abilities = realm.get("abilities", [])
        for ability in abilities:
            player.unlock_ability(ability)
    
    def _apply_breakthrough_penalty(self, player, realm: Dict[str, Any]) -> Dict[str, Any]:
        """应用突破失败的惩罚"""
        penalties = {}
        
        # 根据失败次数决定惩罚严重程度
        failure_count = player.cultivation.get("failure_count", 0)
        
        if failure_count < 3:
            # 轻微反噬
            damage = random.randint(20, 40)
            player.resources["health"] -= damage
            penalties["health_damage"] = damage
            
            # 损失部分修为
            exp_loss = player.exp * 0.1
            player.exp = max(0, player.exp - exp_loss)
            penalties["exp_loss"] = exp_loss
            
        elif failure_count < 6:
            # 中度反噬
            damage = random.randint(40, 70)
            player.resources["health"] -= damage
            penalties["health_damage"] = damage
            
            # 境界倒退风险
            if random.random() < 0.3:
                player.realm_level = max(1, player.realm_level - 1)
                penalties["realm_regression"] = True
            
            # 道伤
            player.add_status_effect("dao_injury", duration=7200)  # 7200秒
            penalties["dao_injury"] = True
            
        else:
            # 严重反噬
            damage = random.randint(70, 90)
            player.resources["health"] -= damage
            penalties["health_damage"] = damage
            
            # 可能直接死亡
            if player.resources["health"] <= 0:
                penalties["death"] = True
            else:
                # 严重道伤
                player.add_status_effect("severe_dao_injury", duration=86400)  # 24小时
                penalties["severe_dao_injury"] = True
        
        return penalties
    
    def _check_enlightenment(self, player) -> bool:
        """
        检查是否触发顿悟
        使用公式: enlightenment_chance
        """
        context = {
            "comprehension": player.attributes.get("comprehension", 50) / 100,
            "meditation_level": player.skills.get("meditation", {}).get("level", 0),
            "environment_spiritual_density": 1.0 + self._get_environment_bonus(player),
            "mental_state": self._get_mental_state(player),
            "random_factor": random.random()
        }
        
        chance = calculate("enlightenment_chance", **context)
        return random.random() < chance
    
    def _get_mental_state(self, player) -> float:
        """获取精神状态系数"""
        # 基础值
        state = 1.0
        
        # 负面状态影响
        if player.has_status_effect("dao_injury"):
            state *= 0.5
        if player.has_status_effect("mental_demon"):
            state *= 0.3
        
        # 正面状态加成
        if player.has_status_effect("clear_mind"):
            state *= 1.5
        if player.has_status_effect("meditation_bonus"):
            state *= 1.2
        
        return state
    
    def _generate_enlightenment(self, player) -> Dict[str, Any]:
        """生成顿悟事件"""
        enlightenments = [
            {
                "name": "剑意初悟",
                "description": "在修炼中突然对剑道有了新的理解",
                "exp_multiplier": 3.0,
                "skill_bonus": {"sword_mastery": 1}
            },
            {
                "name": "天地感应",
                "description": "与天地灵气产生共鸣，修炼速度大增",
                "exp_multiplier": 5.0,
                "permanent_bonus": {"cultivation_speed": 0.1}
            },
            {
                "name": "道心通明",
                "description": "心境突破，道心变得更加坚定",
                "exp_multiplier": 2.0,
                "attribute_bonus": {"willpower": 5, "comprehension": 3}
            }
        ]
        
        enlightenment = random.choice(enlightenments)
        enlightenment["timestamp"] = datetime.now().isoformat()
        enlightenment["type"] = "enlightenment"
        
        # 应用永久加成
        if "permanent_bonus" in enlightenment:
            for key, value in enlightenment["permanent_bonus"].items():
                player.cultivation[key] = player.cultivation.get(key, 0) + value
        
        if "attribute_bonus" in enlightenment:
            for attr, value in enlightenment["attribute_bonus"].items():
                player.attributes[attr] = player.attributes.get(attr, 0) + value
        
        if "skill_bonus" in enlightenment:
            for skill, level in enlightenment["skill_bonus"].items():
                player.improve_skill(skill, level)
        
        return enlightenment
    
    def _generate_cultivation_event(self, player) -> Dict[str, Any]:
        """生成修炼事件"""
        events = DM.get("event_template.cultivation_events", [])
        
        # 如果没有配置事件，使用默认事件
        if not events:
            events = [
                {
                    "name": "灵气潮汐",
                    "description": "突然感受到浓郁的天地灵气涌来",
                    "exp_modifier": 2.0,
                    "type": "positive"
                },
                {
                    "name": "心魔侵扰",
                    "description": "修炼中心魔突现，影响修炼效率",
                    "exp_modifier": 0.5,
                    "type": "negative",
                    "effect": {"status": "mental_demon", "duration": 3600}
                }
            ]
        
        event = random.choice(events)
        event["timestamp"] = datetime.now().isoformat()
        
        # 应用事件效果
        if "effect" in event:
            effect = event["effect"]
            if "status" in effect:
                player.add_status_effect(effect["status"], effect.get("duration", 3600))
        
        return event
    
    def _trigger_breakthrough_event(self, player, result: Dict[str, Any]):
        """触发突破相关事件"""
        # TODO: 与事件系统集成
        event_data = {
            "type": "breakthrough_attempt",
            "player": player.id,
            "success": result["success"],
            "timestamp": datetime.now().isoformat()
        }
        
        if result["success"]:
            event_data["new_realm"] = result["effects"].get("new_realm")
        else:
            event_data["penalties"] = result["penalties"]
        
        # 发送事件到事件系统
        # self.engine.events.emit("breakthrough_event", event_data)
        logger.info(f"Breakthrough event: {event_data}")
    
    def get_realm_suppression(self, attacker_realm: str, defender_realm: str) -> float:
        """
        计算境界压制效果
        使用公式: realm_suppression
        """
        attacker_info = self.get_realm_info(attacker_realm)
        defender_info = self.get_realm_info(defender_realm)
        
        if not attacker_info or not defender_info:
            return 0.0
        
        tier_difference = attacker_info["tier"] - defender_info["tier"]
        if tier_difference <= 0:
            return 0.0
        
        # 使用配置的公式
        formula = self.realm_data["realm_suppression"]["formula"]
        suppression = self.formula_engine.evaluate(
            formula.replace("tier_difference", str(tier_difference)),
            {}
        )
        
        return min(suppression, 0.9)  # 最高90%压制


# 全局实例
cultivation_system = CultivationSystem()

# 导出便捷函数
def cultivate(player, hours: int = 1) -> Dict[str, Any]:
    """修炼的便捷函数"""
    return cultivation_system.cultivate(player, hours)

def attempt_breakthrough(player) -> Dict[str, Any]:
    """突破的便捷函数"""
    return cultivation_system.attempt_breakthrough(player)

def get_cultivation_speed(player) -> float:
    """获取修炼速度的便捷函数"""
    return cultivation_system.calculate_cultivation_speed(player)
