"""
叙事系统
动态生成故事内容和任务
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class StoryPhase(Enum):
    """故事阶段"""
    INTRODUCTION = "introduction"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"


@dataclass
class StoryNode:
    """故事节点"""
    id: str
    phase: StoryPhase
    content: str
    choices: List[Dict[str, Any]] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    consequences: Dict[str, Any] = field(default_factory=dict)
    next_nodes: List[str] = field(default_factory=list)


@dataclass
class Quest:
    """任务"""
    id: str
    name: str
    description: str
    story_arc: str  # 所属故事线
    objectives: List[Dict[str, Any]] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    is_main: bool = False
    is_completed: bool = False


class NarrativeSystem:
    """
    叙事系统管理器
    
    管理游戏的故事线、任务生成和剧情发展
    """
    
    def __init__(self):
        self.story_arcs: Dict[str, Dict[str, Any]] = {}
        self.active_stories: Dict[str, str] = {}  # player_id -> current_node_id
        self.story_nodes: Dict[str, StoryNode] = {}
        self.quests: Dict[str, Quest] = {}
        self.player_choices: Dict[str, List[Dict[str, Any]]] = {}  # 玩家选择历史
        
        # 初始化一些基础故事线
        self._init_base_stories()
        
    def _init_base_stories(self) -> None:
        """初始化基础故事线"""
        # 主线：修仙之路
        main_arc = {
            "id": "main_cultivation",
            "name": "道心之路",
            "description": "从凡人到仙人的漫长旅程",
            "phases": ["凡人觉醒", "初入修行", "道心考验", "突破瓶颈", "飞升之机"]
        }
        self.story_arcs["main_cultivation"] = main_arc
        
        # 支线：门派恩怨
        faction_arc = {
            "id": "faction_conflict", 
            "name": "正邪之争",
            "description": "正道与魔道的千年恩怨",
            "phases": ["初遇纷争", "选择立场", "深入调查", "最终对决"]
        }
        self.story_arcs["faction_conflict"] = faction_arc
        
        # 创建一些初始节点
        self._create_initial_nodes()
        
    def _create_initial_nodes(self) -> None:
        """创建初始故事节点"""
        # 主线开始节点
        start_node = StoryNode(
            id="main_start",
            phase=StoryPhase.INTRODUCTION,
            content="你是一个普通的凡人，某日偶然获得了一本修仙功法...",
            choices=[
                {
                    "text": "立即开始修炼",
                    "consequence": {"eager": True},
                    "next": "main_first_cultivation"
                },
                {
                    "text": "先调查功法来源",
                    "consequence": {"cautious": True},
                    "next": "main_investigate_origin"
                }
            ]
        )
        self.story_nodes["main_start"] = start_node
        
    def start_story_arc(self, player_id: str, arc_id: str) -> Optional[StoryNode]:
        """
        开始一个故事线
        
        Args:
            player_id: 玩家ID
            arc_id: 故事线ID
            
        Returns:
            第一个故事节点
        """
        if arc_id not in self.story_arcs:
            return None
        
        # 找到起始节点
        start_node_id = f"{arc_id}_start"
        if start_node_id in self.story_nodes:
            self.active_stories[player_id] = start_node_id
            
            # 初始化玩家选择历史
            if player_id not in self.player_choices:
                self.player_choices[player_id] = []
                
            return self.story_nodes[start_node_id]
        
        return None
    
    def make_choice(self, player_id: str, choice_index: int) -> Optional[StoryNode]:
        """
        做出故事选择
        
        Args:
            player_id: 玩家ID
            choice_index: 选择索引
            
        Returns:
            下一个故事节点
        """
        current_node_id = self.active_stories.get(player_id)
        if not current_node_id:
            return None
        
        current_node = self.story_nodes.get(current_node_id)
        if not current_node or choice_index >= len(current_node.choices):
            return None
        
        choice = current_node.choices[choice_index]
        
        # 记录选择
        self.player_choices[player_id].append({
            "node_id": current_node_id,
            "choice": choice["text"],
            "consequences": choice.get("consequence", {})
        })
        
        # 获取下一个节点
        next_node_id = choice.get("next")
        if next_node_id and next_node_id in self.story_nodes:
            self.active_stories[player_id] = next_node_id
            return self.story_nodes[next_node_id]
        
        return None
    
    def generate_dynamic_quest(self, player_level: int, location: str, 
                             faction: Optional[str] = None) -> Quest:
        """
        动态生成任务
        
        Args:
            player_level: 玩家等级
            location: 当前位置
            faction: 玩家门派
            
        Returns:
            生成的任务
        """
        # 任务模板
        quest_templates = [
            {
                "type": "hunt",
                "name": "清剿{monster}",
                "description": "附近的{monster}作乱，需要清理",
                "objectives": [{"type": "kill", "target": "{monster}", "count": 5}],
                "reward_base": 100
            },
            {
                "type": "gather",
                "name": "采集{item}",
                "description": "需要收集一些{item}用于炼丹",
                "objectives": [{"type": "collect", "item": "{item}", "count": 10}],
                "reward_base": 80
            },
            {
                "type": "escort",
                "name": "护送商队",
                "description": "护送商队安全到达目的地",
                "objectives": [{"type": "escort", "from": location, "to": "目的地"}],
                "reward_base": 150
            }
        ]
        
        # 根据等级选择合适的模板
        template = random.choice(quest_templates)
        
        # 填充具体内容
        monsters = ["妖狼", "毒蛇", "邪修", "山贼"]
        items = ["灵草", "妖丹", "矿石", "灵木"]
        
        quest_data = template.copy()
        quest_data["name"] = quest_data["name"].format(
            monster=random.choice(monsters),
            item=random.choice(items)
        )
        quest_data["description"] = quest_data["description"].format(
            monster=random.choice(monsters),
            item=random.choice(items)
        )
        
        # 根据等级调整奖励
        rewards = {
            "exp": quest_data["reward_base"] * player_level,
            "gold": quest_data["reward_base"] // 2 * player_level,
            "reputation": 10
        }
        
        # 创建任务
        quest_id = f"quest_{len(self.quests) + 1}"
        quest = Quest(
            id=quest_id,
            name=quest_data["name"],
            description=quest_data["description"],
            story_arc="side_quest",
            objectives=quest_data["objectives"],
            rewards=rewards,
            is_main=False
        )
        
        self.quests[quest_id] = quest
        return quest
    
    def update_quest_progress(self, quest_id: str, objective_index: int, 
                            progress: int) -> bool:
        """
        更新任务进度
        
        Args:
            quest_id: 任务ID
            objective_index: 目标索引
            progress: 进度增量
            
        Returns:
            任务是否完成
        """
        quest = self.quests.get(quest_id)
        if not quest or objective_index >= len(quest.objectives):
            return False
        
        objective = quest.objectives[objective_index]
        current = objective.get("progress", 0)
        objective["progress"] = current + progress
        
        # 检查是否所有目标都完成
        all_complete = all(
            obj.get("progress", 0) >= obj.get("count", 1)
            for obj in quest.objectives
        )
        
        if all_complete:
            quest.is_completed = True
            
        return all_complete
    
    def get_story_summary(self, player_id: str) -> Dict[str, Any]:
        """获取玩家的故事进展摘要"""
        choices = self.player_choices.get(player_id, [])
        
        # 分析选择倾向
        tendencies = {
            "aggressive": 0,
            "cautious": 0,
            "diplomatic": 0,
            "curious": 0
        }
        
        for choice in choices:
            consequences = choice.get("consequences", {})
            for key in tendencies:
                if key in consequences:
                    tendencies[key] += 1
        
        # 当前故事状态
        current_node_id = self.active_stories.get(player_id)
        current_phase = None
        if current_node_id and current_node_id in self.story_nodes:
            current_phase = self.story_nodes[current_node_id].phase.value
        
        return {
            "total_choices": len(choices),
            "tendencies": tendencies,
            "current_phase": current_phase,
            "active_quests": sum(1 for q in self.quests.values() 
                               if not q.is_completed),
            "completed_quests": sum(1 for q in self.quests.values() 
                                  if q.is_completed)
        }
    
    def generate_story_event(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        根据上下文生成故事事件
        
        Args:
            context: 包含玩家状态、位置等信息的上下文
            
        Returns:
            生成的事件
        """
        events = [
            {
                "id": "mysterious_stranger",
                "name": "神秘来客",
                "description": "一位神秘的修士出现在你面前...",
                "choices": ["交谈", "警惕观察", "直接离开"],
                "weight": 0.3
            },
            {
                "id": "ancient_ruins",
                "name": "古迹发现", 
                "description": "你发现了一处隐藏的古代遗迹...",
                "choices": ["立即探索", "做好准备再来", "通知他人"],
                "weight": 0.2
            },
            {
                "id": "moral_dilemma",
                "name": "道德抉择",
                "description": "你遇到了一个需要做出艰难选择的情况...",
                "choices": ["坚持正义", "利益优先", "寻找折中"],
                "weight": 0.25
            }
        ]
        
        # 根据权重选择事件
        weights = [e["weight"] for e in events]
        chosen_event = random.choices(events, weights=weights)[0]
        
        return chosen_event
