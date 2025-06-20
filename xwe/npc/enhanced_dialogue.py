# npc/enhanced_dialogue.py
"""
增强版对话系统

整合情感、记忆和智能理解的对话系统。
"""

import logging
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..core.nlp.nlp_processor import NLPProcessor
from .dialogue_system import DialogueNode, DialogueNodeType, DialogueSystem
from .emotion_system import EmotionSystem, EmotionType
from .memory_system import MemorySystem

logger = logging.getLogger(__name__)


@dataclass
class DialogueContext:
    """对话上下文"""

    player_id: str
    npc_id: str
    npc_name: str

    # 玩家信息
    player_level: int = 1
    player_faction: str = ""
    player_reputation: int = 0

    # NPC信息
    npc_level: int = 1
    npc_faction: str = ""
    npc_role: str = ""

    # 关系信息
    relationship: int = 0
    first_meeting: bool = True

    # 情感状态
    current_emotion: str = "neutral"
    emotion_intensity: float = 0.5
    emotion_modifiers: Dict[str, Any] = field(default_factory=dict)

    # 记忆上下文
    memory_context: str = ""
    recent_memories: List[Any] = field(default_factory=list)

    # 对话历史
    dialogue_history: List[Tuple[str, str]] = field(default_factory=list)  # (speaker, text)

    # 动态数据
    flags: Dict[str, bool] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    rewards: List[Dict[str, Any]] = field(default_factory=list)

    # 游戏时间
    game_time: int = 0


class DialogueGenerator:
    """对话生成器"""

    def __init__(self) -> None:
        """初始化对话生成器"""
        # 对话模板
        self.greeting_templates = {
            EmotionType.HAPPY: [
                "哈哈，{player_name}道友，真是好久不见！",
                "太好了，{player_name}道友来了！",
                "见到道友真是高兴啊！",
            ],
            EmotionType.NEUTRAL: [
                "{player_name}道友，有何贵干？",
                "道友来访，不知有何事？",
                "道友好。",
            ],
            EmotionType.ANGRY: ["哼，你还敢来？", "又是你，有事快说。", "你来做什么？"],
            EmotionType.SAD: [
                "唉，{player_name}道友啊...",
                "道友来了...有事吗？",
                "最近心情不太好...",
            ],
        }

        self.farewell_templates = {
            EmotionType.HAPPY: ["道友慢走，欢迎再来！", "期待下次再见！", "祝道友修行顺利！"],
            EmotionType.NEUTRAL: ["告辞。", "道友慢走。", "后会有期。"],
            EmotionType.ANGRY: ["走吧走吧。", "别再来烦我了。", "哼。"],
        }

        # 话题响应模板
        self.topic_responses = {
            "修炼": {
                "positive": "修炼一途，最重要的是心境。道友若能保持本心，必能有所成就。",
                "neutral": "修炼之事，各有缘法，强求不得。",
                "negative": "你这种人，谈什么修炼？",
            },
            "交易": {
                "positive": "道友想要什么，尽管开口，咱们都是老朋友了。",
                "neutral": "要买什么？我这里货物齐全。",
                "negative": "你的灵石够吗？",
            },
            "消息": {
                "positive": "说起最近的消息，我倒是听说了一些有趣的事...",
                "neutral": "最近坊市还算太平，没什么特别的。",
                "negative": "我凭什么告诉你？",
            },
        }

    def generate_greeting(self, context: DialogueContext) -> str:
        """生成问候语"""
        emotion = EmotionType[context.current_emotion.upper()]
        templates = self.greeting_templates.get(
            emotion, self.greeting_templates[EmotionType.NEUTRAL]
        )

        # 选择模板
        template = random.choice(templates)

        # 根据记忆调整
        if not context.first_meeting and context.memory_context:
            if "老朋友" in context.memory_context:
                template = "老朋友，" + template
            elif "见过几面" in context.memory_context:
                template = template.replace("道友", "")

        # 格式化
        greeting = template.format(
            player_name=context.player_id.replace("player_", ""), npc_name=context.npc_name
        )

        return greeting

    def generate_response(
        self, context: DialogueContext, player_input: str, intent: Optional[str] = None
    ) -> str:
        """生成响应"""
        # 基于情感状态调整语气
        relationship_factor = (context.relationship + 100) / 200  # 归一化到0-1

        # 识别话题
        topic = self._identify_topic(player_input, intent)

        # 获取基础响应
        if topic in self.topic_responses:
            if relationship_factor > 0.7:
                response = self.topic_responses[topic]["positive"]
            elif relationship_factor < 0.3:
                response = self.topic_responses[topic]["negative"]
            else:
                response = self.topic_responses[topic]["neutral"]
        else:
            response = self._generate_generic_response(context)

        # 添加情感色彩
        response = self._add_emotion_color(response, context)

        # 添加记忆相关内容
        if context.recent_memories:
            memory_addon = self._generate_memory_reference(context.recent_memories[0])
            if memory_addon:
                response += f" {memory_addon}"

        return response

    def _identify_topic(self, text: str, intent: str = None) -> Optional[str]:
        """识别话题"""
        topic_keywords = {
            "修炼": ["修炼", "修行", "境界", "突破", "功法"],
            "交易": ["买", "卖", "交易", "商品", "灵石", "价格"],
            "消息": ["消息", "最近", "听说", "发生", "新闻"],
        }

        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic

        return intent

    def _generate_generic_response(self, context: DialogueContext) -> str:
        """生成通用响应"""
        if context.relationship > 50:
            return "道友所言甚是有理。"
        elif context.relationship < -50:
            return "哼，随你怎么说。"
        else:
            return "原来如此。"

    def _add_emotion_color(self, response: str, context: DialogueContext) -> str:
        """添加情感色彩"""
        emotion = EmotionType[context.current_emotion.upper()]

        emotion_prefixes = {
            EmotionType.HAPPY: ["哈哈，", "太好了，", ""],
            EmotionType.ANGRY: ["哼！", "可恶，", ""],
            EmotionType.SAD: ["唉，", "可惜，", ""],
            EmotionType.SURPRISED: ["哦？", "什么？", "这..."],
            EmotionType.EXCITED: ["太棒了！", "真是的！", ""],
        }

        if emotion in emotion_prefixes and context.emotion_intensity > 0.7:
            prefix = random.choice(emotion_prefixes[emotion])
            if prefix and not response.startswith(prefix):
                response = prefix + response

        return response

    def _generate_memory_reference(self, memory: Any) -> Optional[str]:
        """生成记忆相关的话语"""
        memory_refs = ["记得上次{event}的事吗？", "说起来，之前{event}...", "想起{event}的时候..."]

        # 简化记忆内容作为事件
        event = "我们见面"  # 默认
        if hasattr(memory, "content"):
            # 提取关键词
            if "交易" in memory.content:
                event = "交易"
            elif "任务" in memory.content:
                event = "那个任务"
            elif "帮助" in memory.content:
                event = "你帮助我"

        template = random.choice(memory_refs)
        return template.format(event=event)


class EnhancedDialogueSystem:
    """增强版对话系统"""

    def __init__(
        self,
        dialogue_system: DialogueSystem,
        emotion_system: EmotionSystem,
        memory_system: MemorySystem,
        nlp_processor: Optional[NLPProcessor] = None,
    ):
        """
        初始化增强版对话系统

        Args:
            dialogue_system: 基础对话系统
            emotion_system: 情感系统
            memory_system: 记忆系统
            nlp_processor: NLP处理器（可选）
        """
        self.dialogue_system = dialogue_system
        self.emotion_system = emotion_system
        self.memory_system = memory_system
        self.nlp_processor = nlp_processor

        self.dialogue_generator = DialogueGenerator()
        self.active_contexts: Dict[str, DialogueContext] = {}

        # 意图映射
        self.intent_to_dialogue = {
            "greeting": ["greeting", "start"],
            "farewell": ["goodbye", "leave"],
            "trade": ["buy", "sell", "shop", "trade"],
            "quest": ["quest", "task", "mission"],
            "chat": ["chat", "talk", "gossip", "news"],
            "help": ["help", "advice", "guide"],
        }

        logger.info("增强版对话系统初始化")

    def start_dialogue(
        self,
        player_id: str,
        npc_id: str,
        npc_info: Dict[str, Any],
        player_info: Dict[str, Any],
        game_time: int = 0,
    ) -> Tuple[Optional[DialogueNode], DialogueContext]:
        """
        开始对话

        Returns:
            (对话节点, 对话上下文)
        """
        # 创建对话上下文
        context = self._create_dialogue_context(player_id, npc_id, npc_info, player_info, game_time)
        self.active_contexts[player_id] = context

        # 触发情绪反应
        if context.first_meeting:
            self.emotion_system.trigger_emotion(npc_id, EmotionType.HAPPY, 0.6, "first_meeting")
        else:
            self.emotion_system.trigger_emotion(npc_id, EmotionType.HAPPY, 0.3, "greeting")

        # 记录记忆
        if context.first_meeting:
            self.memory_system.create_memory(
                npc_id,
                player_id,
                "first_meeting",
                game_time=game_time,
                player_name=player_id,
                impression="有些陌生" if context.relationship < 20 else "还不错",
            )

        # 获取基础对话节点
        node = self.dialogue_system.start_dialogue(player_id, npc_id)

        # 如果有节点，根据上下文修改文本
        if node:
            node = self._enhance_dialogue_node(node, context)

        return node, context

    def process_player_input(
        self, player_id: str, input_text: str
    ) -> Tuple[Optional[DialogueNode], DialogueContext]:
        """
        处理玩家输入（自然语言）

        Returns:
            (对话节点, 对话上下文)
        """
        context = self.active_contexts.get(player_id)
        if not context:
            logger.warning(f"没有活跃的对话上下文: {player_id}")
            return None, None

        # 记录对话历史
        context.dialogue_history.append(("player", input_text))

        # 使用NLP理解意图
        intent = None

        if self.nlp_processor:
            try:
                nlp_result = self.nlp_processor.parse(input_text)
                intent = nlp_result.get("intent")
                _ = nlp_result.get("entities", {})
            except Exception:
                logger.warning("NLP处理失败，使用关键词匹配")

        # 如果没有NLP或处理失败，使用简单的关键词匹配
        if not intent:
            intent = self._simple_intent_detection(input_text)

        # 查找匹配的对话选项
        choice_id = self._match_dialogue_choice(player_id, intent, input_text)

        if choice_id:
            # 使用标准对话流程
            node = self.dialogue_system.advance_dialogue(player_id, context.__dict__, choice_id)
        else:
            # 生成动态响应
            node = self._generate_dynamic_response(context, input_text, intent)

        # 更新情绪
        self._update_emotion_from_input(context, input_text, intent)

        # 增强节点
        if node:
            node = self._enhance_dialogue_node(node, context)
            context.dialogue_history.append((node.speaker, node.text))

        return node, context

    def advance_dialogue(
        self, player_id: str, choice_id: str
    ) -> Tuple[Optional[DialogueNode], DialogueContext]:
        """
        推进对话（使用选项ID）

        Returns:
            (对话节点, 对话上下文)
        """
        context = self.active_contexts.get(player_id)
        if not context:
            return None, None

        # 推进对话
        node = self.dialogue_system.advance_dialogue(player_id, context.__dict__, choice_id)

        # 增强节点
        if node:
            node = self._enhance_dialogue_node(node, context)
            context.dialogue_history.append((node.speaker, node.text))

        # 检查对话是否结束
        if self.dialogue_system.get_active_dialogue(player_id) is None:
            self._end_dialogue(player_id)

        return node, context

    def _create_dialogue_context(
        self,
        player_id: str,
        npc_id: str,
        npc_info: Dict[str, Any],
        player_info: Dict[str, Any],
        game_time: int = 0,
    ) -> DialogueContext:
        """创建对话上下文"""
        # 获取记忆
        memory_profile = self.memory_system.get_memory_profile(npc_id, player_id)
        first_meeting = not memory_profile or not memory_profile.get("first_meeting")

        # 获取情感状态
        emotion_state = self.emotion_system.get_emotion_state(npc_id)
        emotion_modifiers = self.emotion_system.get_dialogue_modifiers(npc_id)

        # 创建上下文
        context = DialogueContext(
            player_id=player_id,
            npc_id=npc_id,
            npc_name=npc_info.get("name", "NPC"),
            player_level=player_info.get("level", 1),
            player_faction=player_info.get("faction", ""),
            player_reputation=player_info.get("reputation", 0),
            npc_level=npc_info.get("level", 1),
            npc_faction=npc_info.get("faction", ""),
            npc_role=npc_info.get("role", ""),
            relationship=npc_info.get("relationship", 0),
            first_meeting=first_meeting,
            current_emotion=emotion_state.current_emotion.value if emotion_state else "neutral",
            emotion_intensity=emotion_state.emotion_intensity if emotion_state else 0.5,
            emotion_modifiers=emotion_modifiers,
            game_time=game_time,
        )

        # 添加记忆上下文
        if memory_profile:
            context.memory_context = self.memory_system.generate_memory_context(npc_id, player_id)
            context.recent_memories = memory_profile.get("recent_events", [])

        return context

    def _enhance_dialogue_node(self, node: DialogueNode, context: DialogueContext) -> DialogueNode:
        """增强对话节点（添加情感和记忆）"""
        # 根据情感调整文本
        if node.type == DialogueNodeType.TEXT:
            # 替换占位符
            node.text = node.text.format(
                player_name=context.player_id.replace("player_", ""),
                npc_name=context.npc_name,
                **context.variables,
            )

            # 添加情感前缀
            if context.emotion_intensity > 0.7:
                node.text = self.dialogue_generator._add_emotion_color(node.text, context)

        return node

    def _simple_intent_detection(self, text: str) -> Optional[str]:
        """简单的意图检测"""
        text_lower = text.lower()

        intent_keywords = {
            "greeting": ["你好", "您好", "见过", "认识一下"],
            "farewell": ["再见", "告辞", "走了", "拜拜"],
            "trade": ["买", "卖", "多少钱", "价格", "交易"],
            "quest": ["任务", "委托", "帮忙", "需要做什么"],
            "chat": ["聊聊", "最近", "消息", "听说"],
            "help": ["帮助", "指点", "教教", "怎么"],
        }

        for intent, keywords in intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent

        return None

    def _match_dialogue_choice(self, player_id: str, intent: str, input_text: str) -> Optional[str]:
        """匹配对话选项"""
        tree = self.dialogue_system.get_active_dialogue(player_id)
        if not tree:
            return None

        context = self.active_contexts.get(player_id)
        if not context:
            return None

        # 获取可用选项
        choices = tree.get_available_choices(context.__dict__)

        if not choices:
            return None

        # 基于意图匹配
        if intent and intent in self.intent_to_dialogue:
            intent_keywords = self.intent_to_dialogue[intent]
            for choice in choices:
                choice_lower = choice.id.lower()
                if any(keyword in choice_lower for keyword in intent_keywords):
                    return choice.id

        # 基于文本相似度匹配
        input_lower = input_text.lower()
        best_match = None
        best_score = 0

        for choice in choices:
            choice_text_lower = choice.text.lower()

            # 计算简单的相似度
            score = 0
            words = input_lower.split()
            for word in words:
                if word in choice_text_lower:
                    score += 1

            if score > best_score:
                best_score = score
                best_match = choice.id

        if best_score > 0:
            return best_match

        return None

    def _generate_dynamic_response(
        self, context: DialogueContext, input_text: str, intent: str
    ) -> DialogueNode:
        """生成动态响应节点"""
        # 生成响应文本
        response_text = self.dialogue_generator.generate_response(context, input_text, intent)

        # 创建动态节点
        node = DialogueNode(
            id=f"dynamic_{len(context.dialogue_history)}",
            type=DialogueNodeType.TEXT,
            speaker=context.npc_name,
            text=response_text,
        )

        # 根据意图决定是否结束对话
        if intent == "farewell":
            node.type = DialogueNodeType.END
            self._end_dialogue(context.player_id)

        return node

    def _update_emotion_from_input(
        self, context: DialogueContext, input_text: str, intent: str
    ) -> None:
        """根据玩家输入更新NPC情绪"""
        # 检测情感触发词
        triggers = {
            "praise": ["厉害", "了不起", "高明", "佩服"],
            "insult": ["蠢", "笨", "无能", "废物"],
            "gift": ["送", "给你", "礼物", "赠送"],
            "threat": ["杀了你", "找死", "敢", "威胁"],
        }

        input_lower = input_text.lower()
        triggered = None

        for trigger, keywords in triggers.items():
            if any(keyword in input_lower for keyword in keywords):
                triggered = trigger
                break

        if triggered:
            self.emotion_system.trigger_emotion(
                context.npc_id,
                triggered,
                {"relationship": context.relationship, "player_level": context.player_level},
            )

            # 更新上下文中的情绪
            emotion_state = self.emotion_system.get_emotion_state(context.npc_id)
            if emotion_state:
                context.current_emotion = emotion_state.current_emotion.value
                context.emotion_intensity = emotion_state.emotion_intensity

    def _end_dialogue(self, player_id: str) -> None:
        """结束对话"""
        context = self.active_contexts.get(player_id)
        if context:
            # 创建对话记忆
            if len(context.dialogue_history) > 2:
                self.memory_system.create_memory(
                    context.npc_id,
                    player_id,
                    "dialogue",
                    game_time=context.game_time,
                    player_name=player_id,
                    topic="general",
                )

            # 清理上下文
            del self.active_contexts[player_id]

        # 结束基础对话
        self.dialogue_system.end_dialogue(player_id)

    def get_dialogue_context(self, player_id: str) -> Optional[DialogueContext]:
        """获取当前对话上下文"""
        return self.active_contexts.get(player_id)
