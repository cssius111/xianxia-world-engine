"""
叙事系统
动态生成故事内容和任务
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
from datetime import datetime


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


@dataclass
class Achievement:
    """成就"""
    id: str
    name: str
    description: str
    icon: str = "🏆"
    points: int = 10
    unlocked: bool = False
    unlock_time: Optional[datetime] = None
    hidden: bool = False
    

@dataclass
class StoryEvent:
    """故事事件"""
    id: str
    title: str
    description: str
    event_type: str
    choices: List[Dict[str, Any]] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Any] = field(default_factory=dict)
    

class AchievementSystem:
    """成就系统"""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.player_achievements: Dict[str, List[str]] = {}
        self._init_achievements()
        
    def _init_achievements(self):
        """初始化成就列表"""
        base_achievements = [
            Achievement("first_cultivation", "初入修行", "第一次成功修炼"),
            Achievement("first_combat", "初战告捷", "赢得第一场战斗"),
            Achievement("first_quest", "任务达人", "完成第一个任务"),
            Achievement("realm_breakthrough", "境界突破", "成功突破一个大境界", points=50),
            Achievement("treasure_hunter", "寻宝者", "发现10件宝物", points=30),
        ]
        
        for achievement in base_achievements:
            self.achievements[achievement.id] = achievement
            
    def unlock_achievement(self, player_id: str, achievement_id: str) -> Optional[Achievement]:
        """解锁成就"""
        if achievement_id not in self.achievements:
            return None
            
        achievement = self.achievements[achievement_id]
        if achievement.unlocked:
            return None
            
        achievement.unlocked = True
        achievement.unlock_time = datetime.now()
        
        if player_id not in self.player_achievements:
            self.player_achievements[player_id] = []
        self.player_achievements[player_id].append(achievement_id)
        
        return achievement
        
    def get_player_achievements(self, player_id: str) -> List[Achievement]:
        """获取玩家成就"""
        achievement_ids = self.player_achievements.get(player_id, [])
        return [self.achievements[aid] for aid in achievement_ids if aid in self.achievements]


class NarrativeEventSystem:
    """叙事事件系统"""
    
    def __init__(self):
        self.events: Dict[str, StoryEvent] = {}
        self.event_history: Dict[str, List[str]] = {}
        self._init_events()
        
    def _init_events(self):
        """初始化事件"""
        events = [
            StoryEvent(
                "encounter_master",
                "偶遇高人",
                "你在山路上遇到一位仙风道骨的老者...",
                "encounter",
                choices=[
                    {"text": "恭敬行礼", "effect": "positive"},
                    {"text": "默默走过", "effect": "neutral"},
                    {"text": "上前攀谈", "effect": "varies"}
                ]
            ),
            StoryEvent(
                "ancient_tomb",
                "古墓惊魂",
                "你发现了一座隐藏的古墓...",
                "exploration",
                requirements={"level": 10},
                choices=[
                    {"text": "深入探索", "effect": "danger"},
                    {"text": "小心查看", "effect": "safe"},
                    {"text": "离开此地", "effect": "none"}
                ]
            )
        ]
        
        for event in events:
            self.events[event.id] = event
            
    def trigger_event(self, event_id: str, player_id: str) -> Optional[StoryEvent]:
        """触发事件"""
        if event_id not in self.events:
            return None
            
        event = self.events[event_id]
        
        if player_id not in self.event_history:
            self.event_history[player_id] = []
        self.event_history[player_id].append(event_id)
        
        return event


class StoryBranchManager:
    """故事分支管理器"""
    
    def __init__(self):
        self.branches: Dict[str, Dict[str, Any]] = {}
        self.player_branches: Dict[str, str] = {}
        
    def create_branch(self, branch_id: str, branch_data: Dict[str, Any]):
        """创建故事分支"""
        self.branches[branch_id] = branch_data
        
    def set_player_branch(self, player_id: str, branch_id: str):
        """设置玩家当前分支"""
        if branch_id in self.branches:
            self.player_branches[player_id] = branch_id
            
    def get_player_branch(self, player_id: str) -> Optional[str]:
        """获取玩家当前分支"""
        return self.player_branches.get(player_id)


class OpeningEventGenerator:
    """开场事件生成器"""
    
    def __init__(self):
        self.opening_templates = [
            {
                "id": "village_birth",
                "title": "山村少年",
                "description": "你出生在一个偏远的小山村，从小就对修仙充满向往...",
                "starting_items": ["粗布衣衫", "干粮"],
                "starting_stats": {"constitution": 1, "wisdom": 0}
            },
            {
                "id": "noble_birth",
                "title": "世家子弟",
                "description": "你是修仙世家的后代，从小就接触修炼...",
                "starting_items": ["精致法袍", "下品灵石x10"],
                "starting_stats": {"constitution": 0, "wisdom": 1}
            },
            {
                "id": "orphan_birth",
                "title": "孤儿出身",
                "description": "你是一个孤儿，在艰苦中磨练出坚强的意志...",
                "starting_items": ["破旧衣物", "神秘玉佩"],
                "starting_stats": {"constitution": 2, "wisdom": -1}
            }
        ]
        
    def generate_opening(self, choice: Optional[str] = None) -> Dict[str, Any]:
        """生成开场"""
        if choice and any(t["id"] == choice for t in self.opening_templates):
            template = next(t for t in self.opening_templates if t["id"] == choice)
        else:
            template = random.choice(self.opening_templates)
            
        return template.copy()


# 全局实例
achievement_system = AchievementSystem()
narrative_event_system = NarrativeEventSystem()
story_branch_manager = StoryBranchManager()
opening_generator = OpeningEventGenerator()


def check_and_display_achievements(player_id: str, action: str, context: Dict[str, Any]) -> List[Achievement]:
    """检查并显示成就"""
    unlocked = []
    
    # 根据动作检查成就
    if action == "first_cultivation" and context.get("success"):
        achievement = achievement_system.unlock_achievement(player_id, "first_cultivation")
        if achievement:
            unlocked.append(achievement)
            
    elif action == "combat_victory" and context.get("first_time"):
        achievement = achievement_system.unlock_achievement(player_id, "first_combat")
        if achievement:
            unlocked.append(achievement)
            
    elif action == "quest_complete" and context.get("first_time"):
        achievement = achievement_system.unlock_achievement(player_id, "first_quest")
        if achievement:
            unlocked.append(achievement)
            
    return unlocked


def create_immersive_opening(player_name: str, birth_choice: Optional[str] = None) -> Dict[str, Any]:
    """创建沉浸式开场"""
    opening = opening_generator.generate_opening(birth_choice)
    
    # 添加个性化内容
    opening["personalized_intro"] = f"{player_name}，{opening['description']}"
    
    # 生成初始任务
    opening["initial_quest"] = {
        "name": "修仙之路的开始",
        "description": "找到村中的老者，了解如何开始修炼",
        "objectives": [{"type": "talk", "target": "村中老者"}]
    }
    
    return opening


# 全局叙事系统实例
narrative_system = NarrativeSystem()
