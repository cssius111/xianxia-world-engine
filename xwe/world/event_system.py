# world/event_system.py
"""
事件系统

管理世界事件、区域事件和随机遭遇。
"""

import logging
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import json
from pathlib import Path

# 为避免循环依赖，这里不直接导入 Inventory 类型，而是按需检查

# 缓存的物品ID列表，用于随机奖励
_ITEM_IDS: List[str] = []


def _load_item_ids() -> List[str]:
    """加载物品模板并返回物品ID列表"""
    global _ITEM_IDS
    if _ITEM_IDS:
        return _ITEM_IDS

    try:
        data_path = Path(__file__).resolve().parents[1] / "data" / "restructured" / "item_template.json"
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _ITEM_IDS = [item.get("id") for item in data.get("item_templates", []) if item.get("id")]
    except Exception as e:
        logger.error(f"读取物品模板失败: {e}")
        _ITEM_IDS = []
    return _ITEM_IDS

logger = logging.getLogger(__name__)


class EventType(Enum):
    """事件类型"""
    WORLD = "world"          # 世界事件（影响整个游戏世界）
    REGIONAL = "regional"    # 区域事件（影响特定区域）
    ENCOUNTER = "encounter"  # 遭遇事件（随机遭遇）
    QUEST = "quest"         # 任务事件
    SPECIAL = "special"     # 特殊事件


class EventTrigger(Enum):
    """事件触发条件类型"""
    TIME = "time"           # 时间触发
    LOCATION = "location"   # 位置触发
    ACTION = "action"       # 行动触发
    CONDITION = "condition" # 条件触发
    RANDOM = "random"       # 随机触发


@dataclass
class EventCondition:
    """事件触发条件"""
    trigger_type: EventTrigger
    params: Dict[str, Any] = field(default_factory=dict)
    
    def check(self, context: Dict[str, Any]) -> bool:
        """检查条件是否满足"""
        if self.trigger_type == EventTrigger.TIME:
            # 检查时间条件
            current_time = context.get('game_time', 0)
            required_time = self.params.get('time', 0)
            return current_time >= required_time
            
        elif self.trigger_type == EventTrigger.LOCATION:
            # 检查位置条件
            current_location = context.get('location', '')
            required_location = self.params.get('location', '')
            return current_location == required_location
            
        elif self.trigger_type == EventTrigger.ACTION:
            # 检查行动条件
            last_action = context.get('last_action', '')
            required_action = self.params.get('action', '')
            return last_action == required_action
            
        elif self.trigger_type == EventTrigger.CONDITION:
            # 检查自定义条件
            condition_func = self.params.get('condition_func')
            if callable(condition_func):
                return condition_func(context)
                
        elif self.trigger_type == EventTrigger.RANDOM:
            # 随机触发
            chance = self.params.get('chance', 0.1)
            return random.random() < chance
            
        return False


@dataclass
class EventChoice:
    """事件选项"""
    id: str
    text: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    consequences: Dict[str, Any] = field(default_factory=dict)
    
    def is_available(self, context: Dict[str, Any]) -> bool:
        """检查选项是否可用"""
        # 检查等级要求
        if 'min_level' in self.requirements:
            player_level = context.get('player_level', 0)
            if player_level < self.requirements['min_level']:
                return False
        
        # 检查物品要求
        if 'required_items' in self.requirements:
            inventory = context.get('inventory')
            if inventory is None:
                inventory = context.get('player_inventory')
            if inventory is None:
                return False
            required = self.requirements['required_items']
            for item_id in required:
                if hasattr(inventory, 'has'):
                    if not inventory.has(item_id):
                        return False
                elif isinstance(inventory, dict):
                    if inventory.get(item_id, 0) <= 0:
                        return False
                else:
                    return False
        
        # 检查属性要求
        if 'min_attributes' in self.requirements:
            player_attrs = context.get('player_attributes', {})
            for attr, min_val in self.requirements['min_attributes'].items():
                if player_attrs.get(attr, 0) < min_val:
                    return False
        
        return True


@dataclass
class WorldEvent:
    """世界事件"""
    id: str
    name: str
    type: EventType
    description: str
    
    # 触发条件
    conditions: List[EventCondition] = field(default_factory=list)
    
    # 事件内容
    intro_text: str = ""
    choices: List[EventChoice] = field(default_factory=list)
    
    # 事件属性
    priority: int = 0
    repeatable: bool = False
    max_occurrences: int = 1
    occurrences: int = 0
    
    # 事件影响
    effects: Dict[str, Any] = field(default_factory=dict)
    
    # 额外数据
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def can_trigger(self, context: Dict[str, Any]) -> bool:
        """检查事件是否可以触发"""
        # 检查是否已达到最大触发次数
        if not self.repeatable and self.occurrences >= self.max_occurrences:
            return False
        
        # 检查所有触发条件
        for condition in self.conditions:
            if not condition.check(context):
                return False
        
        return True
    
    def trigger(self) -> None:
        """触发事件"""
        self.occurrences += 1
        logger.info(f"触发事件: {self.name}")
    
    def get_available_choices(self, context: Dict[str, Any]) -> List[EventChoice]:
        """获取可用选项"""
        return [choice for choice in self.choices if choice.is_available(context)]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'description': self.description,
            'priority': self.priority,
            'repeatable': self.repeatable,
            'occurrences': self.occurrences,
            'max_occurrences': self.max_occurrences
        }


class EventSystem:
    """
    事件系统
    
    管理和处理游戏中的各种事件。
    """
    
    def __init__(self):
        """初始化事件系统"""
        self.events: Dict[str, WorldEvent] = {}
        self.active_events: List[str] = []
        self.event_history: List[Dict[str, Any]] = []
        self.event_handlers: Dict[str, Callable] = {}
        
        # 初始化默认事件
        self._init_default_events()
        
        logger.info("事件系统初始化")
    
    def _init_default_events(self) -> None:
        """初始化默认事件"""
        # 妖兽袭击事件
        beast_attack = WorldEvent(
            id="beast_attack",
            name="妖兽袭击",
            type=EventType.ENCOUNTER,
            description="一只饥饿的妖兽向你扑来！",
            conditions=[
                EventCondition(
                    EventTrigger.LOCATION,
                    {'location_type': 'wilderness'}
                ),
                EventCondition(
                    EventTrigger.RANDOM,
                    {'chance': 0.15}
                )
            ],
            intro_text="你在荒野中行走时，突然从草丛中跳出一只低阶妖兽，"
                      "它双眼发红，显然已经饿了很久。",
            choices=[
                EventChoice(
                    id="fight",
                    text="与妖兽战斗",
                    consequences={'start_combat': 'low_beast'}
                ),
                EventChoice(
                    id="flee",
                    text="立即逃跑",
                    requirements={'min_attributes': {'agility': 10}},
                    consequences={'stamina_cost': 20}
                ),
                EventChoice(
                    id="intimidate",
                    text="释放威压震慑妖兽",
                    requirements={'min_level': 5},
                    consequences={'reputation': 5}
                )
            ],
            repeatable=True,
            max_occurrences=999
        )
        self.register_event(beast_attack)
        
        # 发现宝物事件
        find_treasure = WorldEvent(
            id="find_treasure",
            name="发现宝物",
            type=EventType.ENCOUNTER,
            description="你发现了一个隐藏的宝箱！",
            conditions=[
                EventCondition(
                    EventTrigger.ACTION,
                    {'action': 'explore'}
                ),
                EventCondition(
                    EventTrigger.RANDOM,
                    {'chance': 0.05}
                )
            ],
            intro_text="在探索过程中，你注意到一块奇怪的石头。"
                      "移开石头后，你发现了一个古老的储物袋！",
            choices=[
                EventChoice(
                    id="open",
                    text="打开储物袋",
                    consequences={'add_random_item': True}
                ),
                EventChoice(
                    id="check_trap",
                    text="先检查是否有陷阱",
                    requirements={'min_attributes': {'intelligence': 12}},
                    consequences={'safe_open': True}
                )
            ],
            repeatable=True,
            max_occurrences=999
        )
        self.register_event(find_treasure)
        
        # 神秘商人事件
        mysterious_merchant = WorldEvent(
            id="mysterious_merchant",
            name="神秘商人",
            type=EventType.SPECIAL,
            description="一位神秘的商人出现在你面前",
            conditions=[
                EventCondition(
                    EventTrigger.LOCATION,
                    {'location_type': 'market'}
                ),
                EventCondition(
                    EventTrigger.RANDOM,
                    {'chance': 0.1}
                )
            ],
            intro_text="一位身穿黑袍的神秘商人悄悄靠近你，"
                      "低声说道：'年轻人，我这里有些特别的东西...'",
            choices=[
                EventChoice(
                    id="browse",
                    text="查看商品",
                    consequences={'open_special_shop': True}
                ),
                EventChoice(
                    id="ask_info",
                    text="询问消息",
                    requirements={'spirit_stones': 50},
                    consequences={'gain_info': True, 'cost_stones': 50}
                ),
                EventChoice(
                    id="leave",
                    text="礼貌拒绝",
                    consequences={}
                )
            ],
            repeatable=True,
            max_occurrences=999
        )
        self.register_event(mysterious_merchant)
    
    def register_event(self, event: WorldEvent) -> None:
        """注册事件"""
        self.events[event.id] = event
        logger.debug(f"注册事件: {event.name}")
    
    def load_events_from_file(self, filepath: str) -> None:
        """从文件加载事件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for event_data in data.get('events', []):
                try:
                    conditions = [
                        EventCondition(
                            EventTrigger(cond.get('type')),
                            cond.get('params', {})
                        )
                        for cond in event_data.get('conditions', [])
                    ]
                    choices = [
                        EventChoice(
                            id=c.get('id'),
                            text=c.get('text', ''),
                            requirements=c.get('requirements', {}),
                            consequences=c.get('consequences', {})
                        )
                        for c in event_data.get('choices', [])
                    ]

                    event = WorldEvent(
                        id=event_data.get('id'),
                        name=event_data.get('name', ''),
                        type=EventType(event_data.get('type', 'world')),
                        description=event_data.get('description', ''),
                        conditions=conditions,
                        intro_text=event_data.get('intro_text', ''),
                        choices=choices,
                        priority=event_data.get('priority', 0),
                        repeatable=event_data.get('repeatable', False),
                        max_occurrences=event_data.get('max_occurrences', 1),
                        effects=event_data.get('effects', {}),
                        extra_data=event_data.get('extra_data', {})
                    )
                    self.register_event(event)
                except Exception as e:
                    logger.error(f"解析事件失败: {e}")

            logger.info(f"从文件加载了 {len(data.get('events', []))} 个事件")

        except Exception as e:
            logger.error(f"加载事件文件失败: {e}")
    
    def check_triggers(self, context: Dict[str, Any]) -> List[WorldEvent]:
        """
        检查所有可触发的事件
        
        Args:
            context: 游戏上下文
            
        Returns:
            可触发的事件列表
        """
        triggered_events = []
        
        for event in self.events.values():
            if event.can_trigger(context):
                triggered_events.append(event)
        
        # 按优先级排序
        triggered_events.sort(key=lambda e: e.priority, reverse=True)
        
        return triggered_events
    
    def trigger_event(self, event_id: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        触发指定事件
        
        Args:
            event_id: 事件ID
            context: 游戏上下文
            
        Returns:
            事件结果
        """
        event = self.events.get(event_id)
        if not event:
            logger.error(f"事件不存在: {event_id}")
            return None
        
        if not event.can_trigger(context):
            logger.warning(f"事件无法触发: {event_id}")
            return None
        
        # 触发事件
        event.trigger()
        
        # 记录到历史
        self.event_history.append({
            'event_id': event_id,
            'timestamp': context.get('game_time', 0),
            'location': context.get('location', '')
        })
        
        # 获取可用选项
        available_choices = event.get_available_choices(context)
        
        result = {
            'event': event,
            'intro_text': event.intro_text,
            'choices': available_choices,
            'effects': event.effects
        }
        
        # 调用自定义处理器
        if event_id in self.event_handlers:
            handler_result = self.event_handlers[event_id](event, context)
            result.update(handler_result)
        
        return result
    
    def handle_choice(self, event_id: str, choice_id: str, 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理事件选择
        
        Args:
            event_id: 事件ID
            choice_id: 选项ID
            context: 游戏上下文
            
        Returns:
            选择结果
        """
        event = self.events.get(event_id)
        if not event:
            return {'success': False, 'message': '事件不存在'}
        
        # 查找选项
        choice = None
        for c in event.choices:
            if c.id == choice_id:
                choice = c
                break
        
        if not choice:
            return {'success': False, 'message': '选项不存在'}
        
        # 检查选项是否可用
        if not choice.is_available(context):
            return {'success': False, 'message': '条件不满足'}
        
        # 处理选择后果
        result = {
            'success': True,
            'consequences': choice.consequences,
            'message': ''
        }
        
        # 应用后果
        for consequence, value in choice.consequences.items():
            if consequence == 'start_combat':
                result['start_combat'] = value
                result['message'] = '战斗开始！'
                
            elif consequence == 'stamina_cost':
                result['stamina_cost'] = value
                result['message'] = f'消耗了{value}点体力'
                
            elif consequence == 'add_random_item':
                item_ids = _load_item_ids()
                if item_ids:
                    item_id = random.choice(item_ids)
                    quantity = 1 if isinstance(value, bool) else int(value)
                    inventory = context.get('inventory')
                    if inventory is None:
                        inventory = context.get('player_inventory')
                    if inventory is not None and hasattr(inventory, 'add'):
                        inventory.add(item_id, quantity)
                    result['obtained_item'] = item_id
                    result['message'] = f'你获得了{item_id}x{quantity}！'
                else:
                    result['message'] = '你获得了一些物品！'
                
            elif consequence == 'reputation':
                result['reputation_change'] = value
                result['message'] = f'声望提升了{value}点！'
        
        return result
    
    def register_handler(self, event_id: str, handler: Callable) -> None:
        """
        注册事件处理器
        
        Args:
            event_id: 事件ID
            handler: 处理函数
        """
        self.event_handlers[event_id] = handler
    
    def get_event_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取事件历史"""
        return self.event_history[-limit:]
    
    def clear_event(self, event_id: str) -> None:
        """清除事件触发次数"""
        event = self.events.get(event_id)
        if event:
            event.occurrences = 0


# 预定义的事件数据
DEFAULT_EVENTS = {
    "events": [
        {
            "id": "sect_recruitment",
            "name": "宗门招收弟子",
            "type": "special",
            "description": "青云宗正在招收新弟子",
            "conditions": [
                {"type": "time", "params": {"min_time": 10}},
                {"type": "location", "params": {"location": "qingyun_city"}}
            ],
            "intro_text": "你看到青云宗在城中设立了招收弟子的摊位，"
                        "一位身穿青色道袍的执事正在测试前来报名的散修。",
            "choices": [
                {
                    "id": "apply",
                    "text": "上前报名",
                    "requirements": {"min_level": 3},
                    "consequences": {"start_quest": "join_sect"}
                },
                {
                    "id": "observe",
                    "text": "在旁观察",
                    "consequences": {"gain_info": "sect_requirements"}
                }
            ]
        }
    ]
}
