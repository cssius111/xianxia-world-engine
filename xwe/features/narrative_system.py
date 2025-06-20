"""
沉浸式叙事与事件系统
- 开局事件
- 天赋逆转
- 成就系统
- 剧情分支
"""

import json
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """事件类型"""

    OPENING = "opening"  # 开局事件
    RANDOM = "random"  # 随机事件
    STORY = "story"  # 剧情事件
    ACHIEVEMENT = "achievement"  # 成就事件
    SPECIAL = "special"  # 特殊事件


class TalentReversal(Enum):
    """天赋逆转类型"""

    WASTE_TO_GENIUS = "waste_to_genius"  # 废材逆袭
    CURSE_TO_BLESSING = "curse_to_blessing"  # 诅咒化福
    ORDINARY_TO_SPECIAL = "ordinary_to_special"  # 平凡觉醒
    WEAK_TO_STRONG = "weak_to_strong"  # 弱者变强
    UNLUCKY_TO_LUCKY = "unlucky_to_lucky"  # 霉运转运


@dataclass
class StoryEvent:
    """剧情事件"""

    id: str
    name: str
    description: str
    event_type: EventType
    choices: List[Dict[str, Any]] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Any] = field(default_factory=dict)
    weight: int = 10  # 权重，用于随机选择
    one_time: bool = True  # 是否一次性事件

    def check_requirements(self, player_data: Dict[str, Any]) -> bool:
        """检查事件要求"""
        for key, value in self.requirements.items():
            if key == "level_min" and player_data.get("level", 1) < value:
                return False
            elif key == "level_max" and player_data.get("level", 1) > value:
                return False
            elif key == "has_item" and value not in player_data.get("items", []):
                return False
            elif key == "has_talent" and value not in player_data.get("talents", []):
                return False
        return True


@dataclass
class Achievement:
    """成就"""

    id: str
    name: str
    description: str
    category: str
    points: int = 10
    hidden: bool = False
    icon: str = "🏆"
    requirements: Dict[str, Any] = field(default_factory=dict)
    rewards: Dict[str, Any] = field(default_factory=dict)

    def check_completion(self, player_stats: Dict[str, Any]) -> bool:
        """检查成就是否完成"""
        for key, value in self.requirements.items():
            if key == "kills" and player_stats.get("total_kills", 0) < value:
                return False
            elif key == "deaths" and player_stats.get("total_deaths", 0) < value:
                return False
            elif key == "level" and player_stats.get("level", 1) < value:
                return False
            elif key == "cultivation_time" and player_stats.get("cultivation_time", 0) < value:
                return False
            elif key == "items_collected" and len(player_stats.get("items", [])) < value:
                return False
        return True


class OpeningEventGenerator:
    """开局事件生成器"""

    def __init__(self) -> None:
        self.opening_events = [
            StoryEvent(
                id="mysterious_elder",
                name="神秘长老",
                description="你在山脚下遇到一位神秘的长老，他似乎在等待着什么...",
                event_type=EventType.OPENING,
                choices=[
                    {
                        "text": "上前询问",
                        "effects": {"talent": "慧眼识珠", "item": "神秘玉佩"},
                        "next_text": "长老微笑着递给你一块玉佩：'有缘人，这是你的机缘。'",
                    },
                    {
                        "text": "绕道而行",
                        "effects": {"attribute": {"luck": -1}},
                        "next_text": "你错过了一个改变命运的机会...",
                    },
                    {
                        "text": "偷偷观察",
                        "effects": {"skill": "敛息术"},
                        "next_text": "你学会了隐藏气息的技巧。",
                    },
                ],
            ),
            StoryEvent(
                id="family_heritage",
                name="家族传承",
                description="整理父母遗物时，你发现了一本泛黄的古籍...",
                event_type=EventType.OPENING,
                choices=[
                    {
                        "text": "立即翻阅",
                        "effects": {"skill": "家传功法", "attribute": {"comprehension": 2}},
                        "next_text": "原来这是失传已久的家族功法！",
                    },
                    {
                        "text": "小心收好",
                        "effects": {"item": "神秘古籍", "attribute": {"luck": 1}},
                        "next_text": "你决定找个安全的地方再研究。",
                    },
                ],
            ),
            StoryEvent(
                id="heavenly_disaster",
                name="天降横祸",
                description="一道雷电突然劈下，正中你的身体！",
                event_type=EventType.OPENING,
                choices=[
                    {
                        "text": "拼命抵抗",
                        "effects": {"talent": "雷电之体", "attribute": {"constitution": 3}},
                        "next_text": "你竟然在雷劫中觉醒了特殊体质！",
                    },
                    {
                        "text": "顺其自然",
                        "effects": {"talent": "天道庇护", "attribute": {"luck": 5}},
                        "next_text": "雷电似乎在改造你的身体...",
                    },
                ],
            ),
            StoryEvent(
                id="system_awakening",
                name="系统觉醒",
                description="一个机械的声音在你脑海中响起：'检测到宿主，系统启动中...'",
                event_type=EventType.OPENING,
                choices=[
                    {
                        "text": "接受系统",
                        "effects": {"system": "修仙辅助系统", "daily_reward": True},
                        "next_text": "【叮！修仙辅助系统绑定成功！】",
                    },
                    {
                        "text": "拒绝系统",
                        "effects": {"talent": "道心坚定", "attribute": {"willpower": 10}},
                        "next_text": "你选择了依靠自己的力量！",
                    },
                ],
            ),
            StoryEvent(
                id="past_life_memory",
                name="前世记忆",
                description="一阵剧痛后，陌生的记忆涌入脑海...",
                event_type=EventType.OPENING,
                choices=[
                    {
                        "text": "接受记忆",
                        "effects": {"talent": "转世仙人", "skills": ["仙人指路", "前世秘法"]},
                        "next_text": "原来你前世是一位大能！",
                    },
                    {
                        "text": "抗拒记忆",
                        "effects": {"talent": "今生无悔", "attribute": {"willpower": 5}},
                        "next_text": "你选择活在当下！",
                    },
                ],
            ),
        ]

        self.talent_reversals = {
            TalentReversal.WASTE_TO_GENIUS: {
                "name": "废材逆袭",
                "description": "所有人都说你是废物，但你不信命！",
                "trigger_condition": lambda p: p.get("talent_level", 0) < 3,
                "effects": {"talent_boost": 10, "special_skill": "逆天改命", "title": "逆袭者"},
            },
            TalentReversal.CURSE_TO_BLESSING: {
                "name": "诅咒化福",
                "description": "身负诅咒的你，将诅咒转化为力量！",
                "trigger_condition": lambda p: "curse" in p.get("debuffs", []),
                "effects": {
                    "remove_debuffs": True,
                    "special_talent": "诅咒免疫",
                    "attribute": {"all": 2},
                },
            },
            TalentReversal.ORDINARY_TO_SPECIAL: {
                "name": "平凡觉醒",
                "description": "平凡的你，在生死关头觉醒了隐藏的力量！",
                "trigger_condition": lambda p: p.get("health_percent", 1.0) < 0.1,
                "effects": {"awakening": True, "hidden_bloodline": True, "full_heal": True},
            },
        }

    def generate_opening_event(self, player_data: Dict[str, Any]) -> Optional[StoryEvent]:
        """生成开局事件"""
        # 根据玩家数据筛选合适的事件
        available_events = [
            event for event in self.opening_events if event.check_requirements(player_data)
        ]

        if not available_events:
            return None

        # 根据权重随机选择
        weights = [event.weight for event in available_events]
        return random.choices(available_events, weights=weights)[0]

    def check_talent_reversal(self, player_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检查是否触发天赋逆转"""
        for reversal_type, reversal_data in self.talent_reversals.items():
            if reversal_data["trigger_condition"](player_data):
                return {
                    "type": reversal_type,
                    "name": reversal_data["name"],
                    "description": reversal_data["description"],
                    "effects": reversal_data["effects"],
                }
        return None


class AchievementSystem:
    """成就系统"""

    def __init__(self) -> None:
        self.achievements = self._init_achievements()
        self.unlocked_achievements = set()
        self.achievement_points = 0
        self.achievement_callbacks = []

    def _init_achievements(self) -> Dict[str, Achievement]:
        """初始化成就列表"""
        achievements = [
            # 战斗成就
            Achievement(
                id="first_blood",
                name="初战告捷",
                description="赢得第一场战斗",
                category="combat",
                points=10,
                icon="⚔️",
                requirements={"kills": 1},
                rewards={"exp": 100, "title": "初出茅庐"},
            ),
            Achievement(
                id="monster_slayer",
                name="妖兽杀手",
                description="击败100只妖兽",
                category="combat",
                points=50,
                icon="🗡️",
                requirements={"kills": 100},
                rewards={"exp": 1000, "item": "妖兽精血"},
            ),
            Achievement(
                id="undefeated",
                name="不败传说",
                description="连续赢得50场战斗不失败",
                category="combat",
                points=100,
                icon="👑",
                requirements={"win_streak": 50},
                rewards={"title": "不败战神", "skill": "战神领域"},
            ),
            # 修炼成就
            Achievement(
                id="cultivation_beginner",
                name="踏入修行",
                description="第一次修炼",
                category="cultivation",
                points=10,
                icon="🧘",
                requirements={"cultivation_count": 1},
                rewards={"exp": 50},
            ),
            Achievement(
                id="breakthrough_master",
                name="突破达人",
                description="成功突破10次境界",
                category="cultivation",
                points=50,
                icon="💫",
                requirements={"breakthrough_count": 10},
                rewards={"item": "破境丹", "title": "突破大师"},
            ),
            Achievement(
                id="meditation_master",
                name="入定高手",
                description="累计修炼100小时",
                category="cultivation",
                points=30,
                icon="🏮",
                requirements={"cultivation_time": 360000},  # 秒
                rewards={"attribute": {"comprehension": 5}},
            ),
            # 探索成就
            Achievement(
                id="explorer",
                name="探索者",
                description="探索10个不同的区域",
                category="exploration",
                points=20,
                icon="🗺️",
                requirements={"explored_areas": 10},
                rewards={"item": "探索者地图", "skill": "寻宝术"},
            ),
            Achievement(
                id="treasure_hunter",
                name="寻宝达人",
                description="发现50个宝箱",
                category="exploration",
                points=40,
                icon="💎",
                requirements={"treasures_found": 50},
                rewards={"title": "寻宝大师", "luck": 5},
            ),
            # 社交成就
            Achievement(
                id="social_butterfly",
                name="社交达人",
                description="与20个不同的NPC对话",
                category="social",
                points=20,
                icon="💬",
                requirements={"npcs_talked": 20},
                rewards={"charm": 3, "title": "交际花"},
            ),
            Achievement(
                id="merchant_friend",
                name="商人之友",
                description="完成100次交易",
                category="social",
                points=30,
                icon="💰",
                requirements={"trades_completed": 100},
                rewards={"merchant_discount": 0.1, "title": "贵宾"},
            ),
            # 收集成就
            Achievement(
                id="collector",
                name="收藏家",
                description="收集50种不同的物品",
                category="collection",
                points=30,
                icon="📦",
                requirements={"unique_items": 50},
                rewards={"storage_expansion": 20},
            ),
            Achievement(
                id="skill_master",
                name="技能大师",
                description="学会20个不同的技能",
                category="collection",
                points=40,
                icon="📚",
                requirements={"skills_learned": 20},
                rewards={"skill_points": 5, "title": "博学者"},
            ),
            # 特殊成就
            Achievement(
                id="lucky_one",
                name="天选之子",
                description="触发10次幸运事件",
                category="special",
                points=50,
                icon="🍀",
                hidden=True,
                requirements={"lucky_events": 10},
                rewards={"luck": 10, "title": "幸运儿"},
            ),
            Achievement(
                id="survivor",
                name="九死一生",
                description="从濒死状态恢复10次",
                category="special",
                points=40,
                icon="💀",
                requirements={"near_death_survivals": 10},
                rewards={"talent": "不死之身", "constitution": 5},
            ),
        ]

        return {ach.id: ach for ach in achievements}

    def check_achievements(self, player_stats: Dict[str, Any]) -> List[Achievement]:
        """检查并解锁成就"""
        newly_unlocked = []

        for ach_id, achievement in self.achievements.items():
            if ach_id not in self.unlocked_achievements:
                if achievement.check_completion(player_stats):
                    self.unlock_achievement(achievement)
                    newly_unlocked.append(achievement)

        return newly_unlocked

    def unlock_achievement(self, achievement: Achievement) -> None:
        """解锁成就"""
        self.unlocked_achievements.add(achievement.id)
        self.achievement_points += achievement.points

        # 触发回调
        for callback in self.achievement_callbacks:
            callback(achievement)

        logger.info(f"成就解锁: {achievement.name}")

    def get_achievement_progress(self, achievement_id: str, player_stats: Dict[str, Any]) -> float:
        """获取成就进度"""
        if achievement_id not in self.achievements:
            return 0.0

        achievement = self.achievements[achievement_id]
        progress = 1.0

        for key, required_value in achievement.requirements.items():
            current_value = player_stats.get(key, 0)
            if isinstance(current_value, (int, float)):
                progress = min(progress, current_value / required_value)

        return progress

    def get_achievement_info(self) -> Dict[str, Any]:
        """获取成就信息"""
        return {
            "total_achievements": len(self.achievements),
            "unlocked_count": len(self.unlocked_achievements),
            "total_points": self.achievement_points,
            "categories": {
                "combat": len([a for a in self.achievements.values() if a.category == "combat"]),
                "cultivation": len(
                    [a for a in self.achievements.values() if a.category == "cultivation"]
                ),
                "exploration": len(
                    [a for a in self.achievements.values() if a.category == "exploration"]
                ),
                "social": len([a for a in self.achievements.values() if a.category == "social"]),
                "collection": len(
                    [a for a in self.achievements.values() if a.category == "collection"]
                ),
                "special": len([a for a in self.achievements.values() if a.category == "special"]),
            },
        }


class StoryBranchManager:
    """剧情分支管理器"""

    def __init__(self) -> None:
        self.story_flags = {}  # 剧情标记
        self.story_branches = {}  # 剧情分支
        self.current_branch = "main"  # 当前分支
        self.branch_history = []  # 分支历史

    def set_flag(self, flag_name: str, value: Any = True) -> None:
        """设置剧情标记"""
        self.story_flags[flag_name] = value
        logger.debug(f"剧情标记设置: {flag_name} = {value}")

    def get_flag(self, flag_name: str, default: Optional[Any] = None) -> Any:
        """获取剧情标记"""
        return self.story_flags.get(flag_name, default)

    def check_conditions(self, conditions: Dict[str, Any]) -> bool:
        """检查条件是否满足"""
        for flag, expected_value in conditions.items():
            if self.get_flag(flag) != expected_value:
                return False
        return True

    def add_branch(self, branch_id: str, branch_data: Dict[str, Any]) -> None:
        """添加剧情分支"""
        self.story_branches[branch_id] = branch_data

    def switch_branch(self, branch_id: str) -> None:
        """切换剧情分支"""
        if branch_id in self.story_branches:
            self.branch_history.append(self.current_branch)
            self.current_branch = branch_id
            logger.info(f"切换到剧情分支: {branch_id}")

    def get_current_events(self) -> List[StoryEvent]:
        """获取当前分支的事件"""
        branch = self.story_branches.get(self.current_branch, {})
        return branch.get("events", [])


class NarrativeEventSystem:
    """叙事事件系统"""

    def __init__(self) -> None:
        self.event_generator = OpeningEventGenerator()
        self.achievement_system = AchievementSystem()
        self.story_manager = StoryBranchManager()

        # 事件历史
        self.event_history = []
        self.active_events = {}

        # 事件回调
        self.event_callbacks = {
            EventType.OPENING: [],
            EventType.RANDOM: [],
            EventType.STORY: [],
            EventType.ACHIEVEMENT: [],
            EventType.SPECIAL: [],
        }

    def register_callback(self, event_type: EventType, callback: Callable) -> None:
        """注册事件回调"""
        self.event_callbacks[event_type].append(callback)

    def trigger_opening_event(self, player_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """触发开局事件"""
        event = self.event_generator.generate_opening_event(player_data)
        if event:
            self.event_history.append(
                {"event": event, "timestamp": time.time(), "player_choice": None}
            )

            # 触发回调
            for callback in self.event_callbacks[EventType.OPENING]:
                callback(event)

            return {"event": event, "choices": event.choices, "type": "opening"}
        return None

    def process_event_choice(self, event_id: str, choice_index: int) -> Dict[str, Any]:
        """处理事件选择"""
        if event_id not in self.active_events:
            return {"success": False, "message": "事件不存在或已过期"}

        event_data = self.active_events[event_id]
        event = event_data["event"]

        if 0 <= choice_index < len(event.choices):
            choice = event.choices[choice_index]

            # 记录选择
            for hist in self.event_history:
                if hist["event"].id == event_id:
                    hist["player_choice"] = choice_index
                    break

            # 应用效果
            effects = choice.get("effects", {})
            result_text = choice.get("next_text", "你做出了选择。")

            # 设置剧情标记
            if "story_flags" in effects:
                for flag, value in effects["story_flags"].items():
                    self.story_manager.set_flag(flag, value)

            # 移除已处理的事件
            del self.active_events[event_id]

            return {
                "success": True,
                "effects": effects,
                "text": result_text,
                "event_complete": True,
            }

        return {"success": False, "message": "无效的选择"}

    def check_talent_reversal(self, player_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检查天赋逆转"""
        reversal = self.event_generator.check_talent_reversal(player_data)
        if reversal:
            # 创建特殊事件
            special_event = StoryEvent(
                id=f"reversal_{reversal['type'].value}",
                name=reversal["name"],
                description=reversal["description"],
                event_type=EventType.SPECIAL,
                effects=reversal["effects"],
            )

            self.event_history.append(
                {"event": special_event, "timestamp": time.time(), "type": "talent_reversal"}
            )

            return reversal
        return None

    def update_achievements(self, player_stats: Dict[str, Any]) -> List[Achievement]:
        """更新成就"""
        newly_unlocked = self.achievement_system.check_achievements(player_stats)

        for achievement in newly_unlocked:
            # 创建成就事件
            ach_event = StoryEvent(
                id=f"achievement_{achievement.id}",
                name=f"成就解锁：{achievement.name}",
                description=achievement.description,
                event_type=EventType.ACHIEVEMENT,
                effects={"rewards": achievement.rewards},
            )

            # 触发成就回调
            for callback in self.event_callbacks[EventType.ACHIEVEMENT]:
                callback(achievement)

        return newly_unlocked

    def get_narrative_summary(self) -> Dict[str, Any]:
        """获取叙事总结"""
        return {
            "total_events": len(self.event_history),
            "opening_events": len(
                [e for e in self.event_history if e["event"].event_type == EventType.OPENING]
            ),
            "achievements_unlocked": len(self.achievement_system.unlocked_achievements),
            "achievement_points": self.achievement_system.achievement_points,
            "current_story_branch": self.story_manager.current_branch,
            "story_flags": len(self.story_manager.story_flags),
        }


# 便捷接口
narrative_system = NarrativeEventSystem()


def create_immersive_opening(player_data: Dict[str, Any]) -> str:
    """创建沉浸式开场"""
    opening = narrative_system.trigger_opening_event(player_data)
    if opening:
        event = opening["event"]

        text = f"\n{'='*60}\n"
        text += f"【{event.name}】\n\n"
        text += f"{event.description}\n\n"

        for i, choice in enumerate(event.choices):
            text += f"{i+1}. {choice['text']}\n"

        text += f"{'='*60}\n"
        return text

    # 默认开场
    return """
=====================================
你睁开双眼，发现自己站在一片陌生的土地上。
远处山峦叠嶂，云雾缭绕，仿佛仙境一般。
这里就是传说中的玄苍界，一个充满机遇与危险的修仙世界。

你的修仙之路，从这里开始...
=====================================
"""


def check_and_display_achievements(player_stats: Dict[str, Any]) -> List[str]:
    """检查并显示成就"""
    unlocked = narrative_system.update_achievements(player_stats)
    messages = []

    for achievement in unlocked:
        msg = f"\n🏆 成就解锁：{achievement.name}\n"
        msg += f"   {achievement.description}\n"
        msg += f"   获得 {achievement.points} 成就点"

        if achievement.rewards:
            msg += "\n   奖励："
            for reward_type, reward_value in achievement.rewards.items():
                msg += f"\n   • {reward_type}: {reward_value}"

        messages.append(msg)

    return messages


# 兼容旧代码的别名
class NarrativeSystem(NarrativeEventSystem):
    """`NarrativeEventSystem` 的别名，保持向后兼容"""

    pass
