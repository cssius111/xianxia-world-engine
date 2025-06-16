"""
事件系统优化实现
使用数据驱动的方式处理游戏事件
"""

import random
import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from xwe.core.data_manager import DM
from xwe.core.formula_engine import formula_engine, evaluate_expression
from xwe.features.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


class EventSystemV3:
    """
    数据驱动的事件系统V3
    从JSON配置加载所有事件定义和触发条件
    """
    
    def __init__(self) -> None:
        self.event_data = {}
        self.active_events = {}
        self.event_history = []
        self.event_handlers = {}
        self.deepseek_client = DeepSeekClient()
        try:
            self.local_events = DM.load("local_events").get("events", [])
        except Exception as e:
            logger.warning(f"Failed to load local events: {e}")
            self.local_events = []
        self._load_event_data()
    
    def _load_event_data(self) -> None:
        """加载事件系统数据"""
        try:
            self.event_data = DM.load("event_template")
            logger.info("Event system data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load event data: {e}")
            raise
    
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event type: {event_type}")
    
    def check_and_trigger_events(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检查并触发符合条件的事件
        
        Args:
            context: 游戏上下文，包含player, location, time等信息
            
        Returns:
            触发的事件列表
        """
        triggered_events = []
        
        # 遍历所有事件
        for event in self.event_data.get("events", []):
            if self._check_event_conditions(event, context):
                # 检查概率
                trigger_chance = event.get("trigger", {}).get("probability", 1.0)
                if random.random() < trigger_chance:
                    # 触发事件
                    event_instance = self._create_event_instance(event, context)
                    triggered_events.append(event_instance)
                    
                    # 记录历史
                    self._record_event(event_instance)
                    
                    # 调用处理器
                    self._call_handlers(event_instance)
        
        return triggered_events
    
    def _check_event_conditions(self, event: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """检查事件触发条件"""
        trigger = event.get("trigger", {})
        trigger_type = trigger.get("type")
        
        # 根据触发类型检查
        if trigger_type == "exploration":
            # 探索触发
            if context.get("action") != "explore":
                return False
            
            # 检查地点类型
            location_types = trigger.get("conditions", {}).get("location_type", [])
            if location_types:
                current_location_type = context.get("location", {}).get("type")
                if current_location_type not in location_types:
                    return False
            
            # 检查境界要求
            min_realm = trigger.get("conditions", {}).get("min_realm")
            if min_realm and not self._check_realm_requirement(context.get("player"), min_realm):
                return False
        
        elif trigger_type == "combat":
            # 战斗触发
            if context.get("action") != "combat":
                return False
            
            combat_result = trigger.get("conditions", {}).get("result")
            if combat_result and context.get("combat_result") != combat_result:
                return False
        
        elif trigger_type == "time":
            # 时间触发
            time_condition = trigger.get("conditions", {}).get("time")
            if time_condition and not self._check_time_condition(time_condition, context.get("game_time")):
                return False
        
        elif trigger_type == "custom":
            # 自定义条件
            custom_formula = trigger.get("custom_formula")
            if custom_formula:
                try:
                    result = evaluate_expression(custom_formula, context)
                    if not result:
                        return False
                except Exception as e:
                    logger.error(f"Error evaluating custom formula: {e}")
                    return False
        
        # 检查前置事件
        prerequisites = event.get("prerequisites", [])
        for prereq in prerequisites:
            if not self._has_completed_event(prereq):
                return False
        
        # 检查冷却时间
        cooldown = event.get("cooldown", 0)
        if cooldown > 0:
            last_trigger = self._get_last_trigger_time(event["id"])
            if last_trigger:
                time_passed = (datetime.now() - last_trigger).total_seconds()
                if time_passed < cooldown:
                    return False
        
        return True
    
    def _check_realm_requirement(self, player, min_realm: str) -> bool:
        """检查境界要求"""
        realm_order = [
            "qi_gathering", "foundation_building", "golden_core",
            "nascent_soul", "deity_transformation", "void_refinement",
            "body_integration", "mahayana", "tribulation_transcendence"
        ]
        
        if not player or not hasattr(player, "realm"):
            return False
        
        try:
            player_realm_index = realm_order.index(player.realm)
            required_realm_index = realm_order.index(min_realm)
            return player_realm_index >= required_realm_index
        except ValueError:
            return False
    
    def _check_time_condition(self, time_condition: str, game_time: Optional[float]) -> bool:
        """检查时间条件"""
        if not game_time:
            return False
        
        # TODO: 实现更复杂的时间条件判断
        # 例如: "day", "night", "full_moon", "new_year" 等
        return True
    
    def _has_completed_event(self, event_id: str) -> bool:
        """检查是否已完成某个事件"""
        return any(e.get("id") == event_id and e.get("completed", False) 
                  for e in self.event_history)
    
    def _get_last_trigger_time(self, event_id: str) -> Optional[datetime]:
        """获取事件上次触发时间"""
        for event in reversed(self.event_history):
            if event.get("id") == event_id:
                timestamp = event.get("timestamp")
                if timestamp:
                    return datetime.fromisoformat(timestamp)
        return None
    
    def _create_event_instance(self, event_template: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """创建事件实例"""
        instance = {
            "id": event_template["id"],
            "name": event_template["name"],
            "description": self._process_description(event_template["description"], context),
            "type": event_template.get("type", "generic"),
            "timestamp": datetime.now().isoformat(),
            "choices": [],
            "context": context.copy()
        }
        
        # 处理选项
        for choice in event_template.get("choices", []):
            if self._check_choice_requirements(choice, context):
                processed_choice = {
                    "id": choice.get("id", choice["text"]),
                    "text": choice["text"],
                    "outcomes": choice.get("outcomes", [])
                }
                instance["choices"].append(processed_choice)
        
        # 如果没有可用选项，添加默认选项
        if not instance["choices"]:
            instance["choices"].append({
                "id": "continue",
                "text": "继续",
                "outcomes": []
            })
        
        return instance
    
    def _process_description(self, description: str, context: Dict[str, Any]) -> str:
        """处理描述文本，替换变量"""
        # 简单的变量替换
        if context.get("player"):
            description = description.replace("{player_name}", context["player"].name)
            description = description.replace("{player_realm}", context["player"].realm)
        
        if context.get("location"):
            description = description.replace("{location_name}", context["location"].get("name", "未知地点"))
        
        return description
    
    def _check_choice_requirements(self, choice: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """检查选项要求"""
        requirements = choice.get("requirements", {})
        
        if not requirements:
            return True
        
        player = context.get("player")
        if not player:
            return False
        
        # 检查属性要求
        for attr, required_value in requirements.items():
            if attr in ["strength", "agility", "intelligence", "constitution"]:
                if getattr(player.attributes, attr, 0) < required_value:
                    return False
            elif attr == "realm":
                if not self._check_realm_requirement(player, required_value):
                    return False
            elif attr == "item":
                if not player.has_item(required_value):
                    return False
        
        return True
    
    def process_choice(self, event_instance: Dict[str, Any], choice_id: str) -> Dict[str, Any]:
        """
        处理玩家选择
        
        Returns:
            选择的结果
        """
        # 找到选择
        choice = None
        for c in event_instance["choices"]:
            if c["id"] == choice_id:
                choice = c
                break
        
        if not choice:
            return {"success": False, "message": "无效的选择"}
        
        # 处理结果
        outcomes = choice.get("outcomes", [])
        if not outcomes:
            return {"success": True, "message": "你做出了选择"}
        
        # 根据权重选择结果
        total_weight = sum(o.get("weight", 1.0) for o in outcomes)
        rand = random.random() * total_weight
        
        current_weight = 0
        selected_outcome = None
        for outcome in outcomes:
            current_weight += outcome.get("weight", 1.0)
            if rand <= current_weight:
                selected_outcome = outcome
                break
        
        if not selected_outcome:
            selected_outcome = outcomes[0]
        
        # 应用结果
        result = self._apply_outcome(selected_outcome, event_instance["context"])
        
        # 标记事件完成
        event_instance["completed"] = True
        event_instance["choice_made"] = choice_id
        event_instance["outcome"] = selected_outcome
        
        return result
    
    def _apply_outcome(self, outcome: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """应用事件结果"""
        result = {
            "success": True,
            "type": outcome["type"],
            "message": outcome.get("text", ""),
            "effects": []
        }
        
        player = context.get("player")
        if not player:
            return result
        
        outcome_type = outcome["type"]
        
        if outcome_type == "reward":
            # 奖励
            rewards = outcome.get("rewards", {})
            
            # 经验奖励
            if "experience" in rewards:
                exp = rewards["experience"]
                if isinstance(exp, str) and exp.endswith("%"):
                    # 百分比经验
                    percentage = float(exp[:-1]) / 100
                    exp = int(player.exp_needed * percentage)
                player.gain_experience(exp)
                result["effects"].append(f"获得 {exp} 点经验")
            
            # 物品奖励
            if "items" in rewards:
                for item_id in rewards["items"]:
                    player.add_item(item_id)
                    result["effects"].append(f"获得物品: {item_id}")
            
            # 属性奖励
            if "attributes" in rewards:
                for attr, value in rewards["attributes"].items():
                    setattr(player.attributes, attr, 
                           getattr(player.attributes, attr, 0) + value)
                    result["effects"].append(f"{attr} +{value}")
        
        elif outcome_type == "combat":
            # 触发战斗
            enemy_id = outcome.get("enemy")
            result["message"] = f"你遭遇了 {enemy_id}！"
            result["combat_trigger"] = enemy_id
        
        elif outcome_type == "status":
            # 添加状态
            status = outcome.get("status", {})
            status_name = status.get("name")
            duration = status.get("duration", 3600)
            player.add_status_effect(status_name, duration)
            result["effects"].append(f"获得状态: {status_name}")
        
        elif outcome_type == "teleport":
            # 传送
            destination = outcome.get("destination")
            result["teleport_to"] = destination
            result["message"] = f"你被传送到了 {destination}"
        
        elif outcome_type == "information":
            # 信息/剧情
            result["message"] = outcome.get("text", "你获得了一些信息")
        
        return result
    
    def _record_event(self, event_instance: Dict[str, Any]) -> None:
        """记录事件到历史"""
        self.event_history.append(event_instance)
        
        # 限制历史记录数量
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]
    
    def _call_handlers(self, event_instance: Dict[str, Any]) -> None:
        """调用事件处理器"""
        event_type = event_instance.get("type", "generic")
        
        # 调用特定类型的处理器
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_instance)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
        
        # 调用通用处理器
        if "all" in self.event_handlers:
            for handler in self.event_handlers["all"]:
                try:
                    handler(event_instance)
                except Exception as e:
                    logger.error(f"Error in generic event handler: {e}")
    
    def get_active_events(self) -> List[Dict[str, Any]]:
        """获取当前激活的事件"""
        return [e for e in self.event_history 
                if not e.get("completed", False) 
                and (datetime.now() - datetime.fromisoformat(e["timestamp"])).total_seconds() < 3600]
    
    def get_event_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取事件历史"""
        return self.event_history[-limit:]

    def _validate_event(self, event: Dict[str, Any]) -> bool:
        """校验事件结构是否符合 event_schema.md"""
        required = {"id", "name", "description", "type", "category", "effect"}
        if not isinstance(event, dict):
            return False
        if not required.issubset(event.keys()):
            return False
        effect = event.get("effect")
        if not isinstance(effect, dict) or "type" not in effect:
            return False
        return True

    def generate_event(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成单个事件，优先使用 DeepSeek API"""
        if self.deepseek_client.api_key:
            try:
                event = self.deepseek_client.generate_event(context)
                if self._validate_event(event):
                    return event
            except Exception as e:
                logger.warning(f"DeepSeek event generation failed: {e}")

        if not self.local_events:
            try:
                self.local_events = DM.load("local_events").get("events", [])
            except Exception as e:
                logger.error(f"Failed to load fallback events: {e}")
                return {}

        return random.choice(self.local_events) if self.local_events else {}
    
    def create_custom_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建自定义事件"""
        event_instance = {
            "id": event_data.get("id", f"custom_{len(self.event_history)}"),
            "name": event_data.get("name", "自定义事件"),
            "description": event_data.get("description", ""),
            "type": "custom",
            "timestamp": datetime.now().isoformat(),
            "choices": event_data.get("choices", []),
            "custom_data": event_data
        }
        
        self._record_event(event_instance)
        self._call_handlers(event_instance)
        
        return event_instance


# 全局实例
event_system = EventSystemV3()

# 导出便捷函数
def trigger_events(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """触发事件的便捷函数"""
    return event_system.check_and_trigger_events(context)

def process_event_choice(event: Dict[str, Any], choice_id: str) -> Dict[str, Any]:
    """处理事件选择的便捷函数"""
    return event_system.process_choice(event, choice_id)

def register_event_handler(event_type: str, handler: Callable) -> None:
    """注册事件处理器的便捷函数"""
    event_system.register_handler(event_type, handler)
