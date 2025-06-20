# immersive_event_system.py
"""
沉浸式分步事件系统
每个事件都需要玩家交互才能推进，增强剧情感和参与感
"""

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class SpecialEventHandler:
    """处理特殊事件的简单助手"""

    @staticmethod
    def handle_cultivation_event(
        event_system: "ImmersiveEventSystem", context: Dict[str, Any], duration: int
    ) -> int:
        """简化的修炼事件处理"""
        exp = duration * 50
        event_system.current_context = {"event_effects": {"exp": exp}}
        return exp


class EventType(Enum):
    """事件类型"""

    STORY = "story"  # 剧情事件
    BATTLE = "battle"  # 战斗事件
    CHOICE = "choice"  # 选择事件
    REWARD = "reward"  # 奖励事件
    ROLL = "roll"  # Roll事件
    DIALOGUE = "dialogue"  # 对话事件
    DISCOVERY = "discovery"  # 发现事件
    SPECIAL = "special"  # 特殊事件


@dataclass
class EventChoice:
    """事件选项"""

    id: str
    text: str
    consequence: Optional[str] = None  # 选择后果ID
    requirements: Dict[str, Any] = field(default_factory=dict)  # 选择条件
    effects: Dict[str, Any] = field(default_factory=dict)  # 选择效果


@dataclass
class EventStep:
    """事件步骤"""

    id: str
    type: EventType
    title: str
    content: str
    choices: List[EventChoice] = field(default_factory=list)
    auto_continue: bool = False  # 是否自动继续
    delay: float = 0.0  # 延迟时间
    effects: Dict[str, Any] = field(default_factory=dict)
    next_step: Optional[str] = None  # 下一步ID


class ImmersiveEventSystem:
    def __init__(self, output_handler=None) -> None:
        self.output_handler = output_handler
        self.events = self._init_events()
        self.current_event = None
        self.current_step = None
        self.event_history = []
        self.event_callbacks = {}
        self.player_choices = {}

    def _init_events(self) -> Dict[str, List[EventStep]]:
        """初始化事件库"""
        events = {
            "first_cultivation_event": [
                EventStep(
                    id="meditation_start",
                    type=EventType.STORY,
                    title="初次修炼",
                    content="""
你按照所学的方法，盘膝而坐，双手结印。

深吸一口气，开始尝试感应天地灵气...

渐渐地，你感觉到周围有一种神秘的能量在流动。
那是一种难以言喻的感觉，如同春风拂面，又似暖流涌动。
                    """,
                    auto_continue=False,
                    next_step="sensing_qi",
                ),
                EventStep(
                    id="sensing_qi",
                    type=EventType.CHOICE,
                    title="感应灵气",
                    content="""
突然，你感应到了三股不同的灵气流：

一股纯净温和，如春风细雨
一股炽热狂暴，似烈火燎原
一股深邃神秘，若深渊幽潭

你决定尝试吸纳哪一股灵气？
                    """,
                    choices=[
                        EventChoice(
                            id="pure_qi",
                            text="纯净温和的灵气",
                            effects={"qi_type": "pure", "exp": 50},
                        ),
                        EventChoice(
                            id="fierce_qi",
                            text="炽热狂暴的灵气",
                            effects={"qi_type": "fire", "exp": 60, "damage": 10},
                        ),
                        EventChoice(
                            id="mysterious_qi",
                            text="深邃神秘的灵气",
                            effects={"qi_type": "mystery", "exp": 40, "special": True},
                        ),
                    ],
                ),
                EventStep(
                    id="cultivation_result",
                    type=EventType.REWARD,
                    title="修炼结果",
                    content="",  # 动态生成
                    auto_continue=False,
                ),
            ],
            "random_encounter": [
                EventStep(
                    id="encounter_intro",
                    type=EventType.STORY,
                    title="意外遭遇",
                    content="""
探索中，你突然听到前方传来一阵骚动。

透过树林的缝隙，你看到一个身影正在与什么东西对峙。
走近一看，原来是一位年轻的女修士正在与一只妖兽对峙。

女修士似乎受了伤，情况不太妙...
                    """,
                    choices=[
                        EventChoice(
                            id="help_fight", text="立即出手相助", consequence="join_battle"
                        ),
                        EventChoice(id="observe", text="先观察情况", consequence="observe_scene"),
                        EventChoice(id="leave", text="悄悄离开", consequence="leave_scene"),
                    ],
                )
            ],
            "treasure_discovery": [
                EventStep(
                    id="find_cave",
                    type=EventType.DISCOVERY,
                    title="神秘洞府",
                    content="""
你在山壁上发现了一个隐蔽的洞口。
洞口被藤蔓遮掩，若不是灵气波动异常，很难发现。

洞内深处似乎有微弱的光芒闪烁...
                    """,
                    choices=[
                        EventChoice(
                            id="enter_carefully",
                            text="小心翼翼地进入",
                            requirements={"courage": 50},
                        ),
                        EventChoice(
                            id="throw_stone", text="先扔块石头试探", consequence="test_danger"
                        ),
                        EventChoice(
                            id="mark_location",
                            text="做个标记，以后再来",
                            effects={"marked_location": "mysterious_cave"},
                        ),
                    ],
                )
            ],
        }

        return events

    def trigger_event(self, event_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """触发事件"""
        if event_id not in self.events:
            return False

        self.current_event = event_id
        self.current_step = 0
        self.player_choices[event_id] = []

        # 保存上下文
        self.current_context = context or {}

        return True

    def get_current_step(self) -> Optional[EventStep]:
        """获取当前步骤"""
        if not self.current_event or self.current_step is None:
            return None

        steps = self.events[self.current_event]
        if self.current_step >= len(steps):
            return None

        return steps[self.current_step]

    def make_choice(self, choice_index: int) -> Tuple[bool, Optional[str]]:
        """做出选择"""
        current_step = self.get_current_step()
        if not current_step or not current_step.choices:
            return False, "当前没有可选项"

        if choice_index < 0 or choice_index >= len(current_step.choices):
            return False, "无效的选择"

        choice = current_step.choices[choice_index]

        # 检查需求
        if not self._check_requirements(choice.requirements):
            return False, "不满足选择条件"

        # 记录选择
        self.player_choices[self.current_event].append(choice.id)

        # 应用效果
        self._apply_effects(choice.effects)

        # 处理后果
        if choice.consequence:
            # 查找对应的步骤
            for i, step in enumerate(self.events[self.current_event]):
                if step.id == choice.consequence:
                    self.current_step = i
                    return True, None
            # 如果在当前事件中找不到，可能是触发新事件
            if choice.consequence in self.events:
                self.trigger_event(choice.consequence, self.current_context)
                return True, None

        # 默认进入下一步
        self.current_step += 1
        return True, None

    def auto_continue(self) -> bool:
        """自动继续到下一步"""
        current_step = self.get_current_step()
        if not current_step:
            return False

        if current_step.auto_continue:
            if current_step.delay > 0:
                time.sleep(current_step.delay)

            if current_step.next_step:
                # 跳转到指定步骤
                for i, step in enumerate(self.events[self.current_event]):
                    if step.id == current_step.next_step:
                        self.current_step = i
                        return True
            else:
                # 默认下一步
                self.current_step += 1

        return False

    def is_event_complete(self) -> bool:
        """检查事件是否完成"""
        if not self.current_event:
            return True

        steps = self.events[self.current_event]
        return self.current_step >= len(steps)

    def complete_event(self) -> None:
        """完成当前事件"""
        if self.current_event:
            # 记录历史
            self.event_history.append(
                {
                    "event_id": self.current_event,
                    "choices": self.player_choices.get(self.current_event, []),
                    "timestamp": time.time(),
                }
            )

            # 触发回调
            if self.current_event in self.event_callbacks:
                self.event_callbacks[self.current_event](
                    self.player_choices.get(self.current_event, [])
                )

        # 清理状态
        self.current_event = None
        self.current_step = None
        self.current_context = None

    def _check_requirements(self, requirements: Dict[str, Any]) -> bool:
        """检查需求是否满足"""
        if not requirements:
            return True

        # 这里需要根据实际游戏状态检查
        # 示例实现
        for key, value in requirements.items():
            if key == "courage":
                # 检查勇气值
                player_courage = self.current_context.get("player_courage", 100)
                if player_courage < value:
                    return False

        return True

    def _apply_effects(self, effects: Dict[str, Any]) -> None:
        """应用效果"""
        if not effects:
            return

        # 这里需要根据实际游戏系统应用效果
        # 将效果存储在上下文中，供游戏核心处理
        if "event_effects" not in self.current_context:
            self.current_context["event_effects"] = {}

        self.current_context["event_effects"].update(effects)

    def register_callback(self, event_id: str, callback: Callable) -> None:
        """注册事件完成回调"""
        self.event_callbacks[event_id] = callback

    def get_event_context(self) -> Dict[str, Any]:
        """获取当前事件上下文"""
        return self.current_context or {}

    def format_current_step(self) -> str:
        """格式化当前步骤的显示"""
        step = self.get_current_step()
        if not step:
            return ""

        output = []

        # 标题
        output.append(f"\n{'='*50}")
        output.append(f"【{step.title}】")
        output.append(f"{'='*50}\n")

        # 内容（特殊处理某些类型）
        if step.type == EventType.REWARD and step.id == "cultivation_result":
            # 动态生成修炼结果
            effects = self.current_context.get("event_effects", {})
            qi_type = effects.get("qi_type", "unknown")
            exp = effects.get("exp", 0)

            if qi_type == "pure":
                content = f"""
灵气缓缓流入你的经脉，温和而持久。
你感觉身体变得更加轻盈，神识也更加清明。

获得修为：{exp}点
体质略有提升！
"""
            elif qi_type == "fire":
                damage = effects.get("damage", 0)
                content = f"""
炽热的灵气如同烈火般涌入体内！
你感觉浑身燥热，但力量也在快速增长。

获得修为：{exp}点
受到反噬伤害：{damage}点
攻击力提升！
"""
            elif qi_type == "mystery":
                content = f"""
神秘的灵气在你体内游走，带来了意想不到的变化...
你感觉自己似乎触碰到了某种深奥的法则。

获得修为：{exp}点
你的悟性得到了提升！
获得特殊感悟：「天地玄机」
"""
            else:
                content = step.content

            output.append(content)
        else:
            output.append(step.content)

        # 选项
        if step.choices:
            output.append("\n" + "-" * 40)
            for i, choice in enumerate(step.choices, 1):
                # 检查是否满足条件
                if self._check_requirements(choice.requirements):
                    output.append(f"{i}. {choice.text}")
                else:
                    output.append(f"{i}. {choice.text} [条件不足]")

        return "\n".join(output)
