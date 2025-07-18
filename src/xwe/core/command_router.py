"""
命令路由器
根据优先级和上下文路由命令，集成 DeepSeek NLP 处理器（可选）
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("xwe.command_router")

# 尝试导入 NLP 模块（可选）
try:
    from .nlp.nlp_processor import DeepSeekNLPProcessor, ParsedCommand

    HAS_NLP = True
except ImportError as e:
    logger.warning(f"NLP 模块导入失败: {e}，将使用传统命令解析")
    HAS_NLP = False

    # 创建一个简单的 ParsedCommand 替代类
    @dataclass
    class ParsedCommand:
        raw: str
        normalized_command: str
        intent: str
        args: Dict[str, Any]
        explanation: str
        confidence: float = 1.0


class CommandPriority(Enum):
    """命令优先级"""

    CRITICAL = 1  # 紧急命令（如逃跑）
    HIGH = 2  # 高优先级
    NORMAL = 3  # 普通优先级
    LOW = 4  # 低优先级


@dataclass
class CommandRoute:
    """命令路由"""

    pattern: str
    handler: str
    priority: CommandPriority = CommandPriority.NORMAL
    contexts: List[str] = None  # 适用的上下文

    def __post_init__(self):
        if self.contexts is None:
            self.contexts = ["*"]  # 默认所有上下文


class CommandRouter:
    """
    命令路由器

    根据当前上下文和优先级路由命令到相应的处理器
    集成 DeepSeek NLP 处理器进行智能命令解析（如果可用）
    """

    def __init__(self, use_nlp: bool = True):
        """
        初始化路由器

        Args:
            use_nlp: 是否启用 NLP 处理器
        """
        self.routes: List[CommandRoute] = []
        self.current_context = "exploration"  # 默认探索模式
        self.use_nlp = use_nlp and HAS_NLP  # 只有在模块可用时才启用
        self._nlp_handler: Optional[Callable[[str, dict], Any]] = None

        # 初始化 NLP 处理器
        if self.use_nlp:
            try:
                self.nlp_processor = DeepSeekNLPProcessor()
                logger.info("DeepSeek NLP 处理器初始化成功")
            except Exception as e:
                logger.warning(f"DeepSeek NLP 处理器初始化失败: {e}，将使用传统解析")
                self.use_nlp = False
                self.nlp_processor = None
        else:
            self.nlp_processor = None
            if use_nlp and not HAS_NLP:
                logger.info("NLP 功能不可用，使用传统命令解析")

        # 初始化默认路由
        self._init_default_routes()

        # 命令映射表（将 NLP 解析的标准命令映射到处理器）
        self.command_handler_map = {
            "探索": "explore",
            "修炼": "cultivate",
            "查看状态": "status",
            "打开背包": "inventory",
            "前往": "move",
            "使用物品": "use_item",
            "使用": "use_item",
            "交谈": "talk",
            "对话": "talk",
            "交易": "trade",
            "攻击": "attack",
            "防御": "defend",
            "逃跑": "flee",
            "突破": "breakthrough",
            "保存": "save",
            "退出": "quit",
            "帮助": "help",
            "未知": "unknown",
        }

    def _init_default_routes(self) -> None:
        """初始化默认路由规则"""
        # 战斗上下文的路由
        self.add_route("逃", "flee", CommandPriority.CRITICAL, ["battle"])
        self.add_route("逃跑", "flee", CommandPriority.CRITICAL, ["battle"])
        self.add_route("攻击", "attack", CommandPriority.HIGH, ["battle"])
        self.add_route("防御", "defend", CommandPriority.HIGH, ["battle"])
        self.add_route("技能", "use_skill", CommandPriority.HIGH, ["battle"])

        # 探索上下文的路由
        self.add_route("移动", "move", CommandPriority.NORMAL, ["exploration"])
        self.add_route("探索", "explore", CommandPriority.NORMAL, ["exploration"])
        self.add_route("对话", "talk", CommandPriority.NORMAL, ["exploration"])
        self.add_route("交易", "trade", CommandPriority.NORMAL, ["exploration"])

        # 通用路由（所有上下文）
        self.add_route("状态", "status", CommandPriority.NORMAL, ["*"])
        self.add_route("背包", "inventory", CommandPriority.NORMAL, ["*"])
        self.add_route("帮助", "help", CommandPriority.LOW, ["*"])
        self.add_route("保存", "save", CommandPriority.LOW, ["*"])

        # 修炼相关
        self.add_route(
            "修炼", "cultivate", CommandPriority.NORMAL, ["exploration", "safe_zone"]
        )
        self.add_route("突破", "breakthrough", CommandPriority.HIGH, ["safe_zone"])

    def add_route(
        self,
        pattern: str,
        handler: str,
        priority: CommandPriority = CommandPriority.NORMAL,
        contexts: List[str] = None,
    ) -> None:
        """
        添加路由规则

        Args:
            pattern: 命令模式
            handler: 处理器名称
            priority: 优先级
            contexts: 适用的上下文列表
        """
        route = CommandRoute(pattern, handler, priority, contexts or ["*"])
        self.routes.append(route)

        # 按优先级排序
        self.routes.sort(key=lambda r: r.priority.value)

    def set_context(self, context: str) -> None:
        """设置当前上下文"""
        self.current_context = context
        logger.debug(f"命令路由器上下文切换到: {context}")

    def set_nlp_handler(self, handler: Callable[[str, dict], Any]) -> None:
        """设置 NLP 失败时的回调处理器"""
        self._nlp_handler = handler

    def route_command(self, input_text: str) -> Tuple[str, Dict[str, Any]]:
        """
        路由命令

        Args:
            input_text: 输入文本

        Returns:
            (命令类型, 参数字典)
        """
        logger.debug("收到命令文本: %s", input_text)
        context = {"current_context": self.current_context}
        # 如果启用了 NLP 处理器，优先使用
        if self.use_nlp and self.nlp_processor:
            logger.debug("使用 NLP 路由")
            try:
                # 使用 NLP 解析
                parsed = self.nlp_processor.parse(input_text, context=context)

                # 处理解析结果
                return self._handle_nlp_result(parsed)

            except Exception as e:
                logger.error(f"NLP 处理失败，回退到备用处理: {e}", exc_info=True)

        else:
            logger.debug("使用传统路由")

        # 如果设置了 NLP 回调处理器，优先使用
        if self._nlp_handler:
            try:
                result = self._nlp_handler(input_text, context)
                if isinstance(result, tuple) and len(result) == 2:
                    return result
                if isinstance(result, dict):
                    return result.get("command_type", "unknown"), result.get(
                        "parameters", {}
                    )
            except Exception as e:
                logger.error(f"备用 NLP 处理器执行失败: {e}")

        # 传统路由匹配
        logger.debug("执行传统路由匹配")
        return self._traditional_route(input_text)

    def _handle_nlp_result(self, parsed: ParsedCommand) -> Tuple[str, Dict[str, Any]]:
        """
        处理 NLP 解析结果

        Args:
            parsed: 解析后的命令对象

        Returns:
            (命令类型, 参数字典)
        """
        # 处理多步命令序列
        if isinstance(parsed.normalized_command, list):
            # 返回第一个命令，后续命令存储在参数中
            commands = parsed.normalized_command
            if commands:
                first_cmd = commands[0]
                handler = self.command_handler_map.get(first_cmd, "unknown")

                params = {
                    "sequence": commands[1:],  # 剩余命令
                    "raw_text": parsed.raw,
                    "explanation": parsed.explanation,
                    "confidence": parsed.confidence,
                }

                # 如果有参数，添加第一个命令的参数
                if isinstance(parsed.args, list) and parsed.args:
                    params.update(parsed.args[0].get("args", {}))

                logger.debug("NLP 路由选择处理器 %s，参数 %s", handler, params)
                return handler, params

        # 处理单个命令
        command = parsed.normalized_command
        handler = self.command_handler_map.get(command, "unknown")

        # 构建参数
        params = parsed.args.copy() if parsed.args else {}
        params.update(
            {
                "raw_text": parsed.raw,
                "intent": parsed.intent,
                "explanation": parsed.explanation,
                "confidence": parsed.confidence,
            }
        )

        # 根据上下文验证命令是否可用
        if not self._is_command_available_in_context(handler):
            allowed = set()
            for route in self.routes:
                if route.handler == handler:
                    allowed.update(route.contexts)
            logger.warning(
                f"命令 {handler} 在当前上下文 {self.current_context} 中不可用，"
                f"允许的上下文: {', '.join(sorted(allowed))}"
            )
            return "context_error", {
                "command": handler,
                "context": self.current_context,
                "message": "命令在当前场景不可用",
            }

        logger.debug("NLP 路由选择处理器 %s，参数 %s", handler, params)
        return handler, params

    def _traditional_route(self, input_text: str) -> Tuple[str, Dict[str, Any]]:
        """
        传统路由匹配

        Args:
            input_text: 输入文本

        Returns:
            (命令类型, 参数字典)
        """
        # 精确匹配路由
        for route in self.routes:
            # 检查上下文
            if "*" not in route.contexts and self.current_context not in route.contexts:
                continue

            # 检查模式匹配
            if input_text.lower().startswith(route.pattern.lower()):
                # 提取参数
                params = self._extract_params(input_text, route.pattern)
                params["raw_text"] = input_text
                logger.debug("传统路由选择处理器 %s，参数 %s", route.handler, params)
                return route.handler, params

        # 默认返回未知命令
        logger.warning("传统路由未找到匹配处理器，返回未知命令")
        return "unknown", {"raw_text": input_text}

    def _is_command_available_in_context(self, handler: str) -> bool:
        """
        检查命令在当前上下文是否可用

        Args:
            handler: 处理器名称

        Returns:
            是否可用
        """
        for route in self.routes:
            if route.handler == handler:
                if "*" in route.contexts or self.current_context in route.contexts:
                    return True
        return True  # 如果没有找到路由，默认允许（兼容新命令）

    def _extract_params(self, input_text: str, pattern: str) -> Dict[str, Any]:
        """提取命令参数"""
        params = {}

        # 移除命令部分，剩下的是参数
        remaining = input_text[len(pattern) :].strip()

        if remaining:
            # 简单处理：第一个词作为目标
            words = remaining.split()
            if words:
                params["target"] = words[0]
                if len(words) > 1:
                    params["extra"] = " ".join(words[1:])

        return params

    def get_available_commands(self) -> List[str]:
        """获取当前上下文下可用的命令"""
        available = []

        for route in self.routes:
            if "*" in route.contexts or self.current_context in route.contexts:
                if route.pattern not in available:
                    available.append(route.pattern)

        return available

    def get_help_text(self) -> str:
        """获取当前上下文的帮助文本"""
        help_lines = ["=== 可用命令 ===\n"]

        # 添加 NLP 提示
        if self.use_nlp and self.nlp_processor:
            help_lines.append("【智能命令解析已启用】")
            help_lines.append("您可以使用自然语言输入命令，例如：")
            help_lines.append("  - '四处看看' → 探索")
            help_lines.append("  - '休息一会儿' → 修炼")
            help_lines.append("  - '去丹药铺' → 移动到丹药铺")
            help_lines.append("")

        # 按优先级分组
        priority_groups = {}
        for route in self.routes:
            if "*" in route.contexts or self.current_context in route.contexts:
                priority = route.priority.name
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append(route.pattern)

        # 显示各优先级的命令
        priority_names = {
            "CRITICAL": "【紧急命令】",
            "HIGH": "【重要命令】",
            "NORMAL": "【常用命令】",
            "LOW": "【其他命令】",
        }

        for priority in ["CRITICAL", "HIGH", "NORMAL", "LOW"]:
            if priority in priority_groups:
                help_lines.append(f"\n{priority_names[priority]}")
                for cmd in priority_groups[priority]:
                    help_lines.append(f"  {cmd}")

        help_lines.append("\n提示：在不同场景下可用的命令会有所不同")

        return "\n".join(help_lines)

    def get_nlp_cache_info(self) -> Optional[Dict]:
        """获取 NLP 处理器缓存信息"""
        if self.use_nlp and self.nlp_processor:
            return self.nlp_processor.get_cache_info()
        return None

    def clear_nlp_cache(self) -> None:
        """清除 NLP 处理器缓存"""
        if self.use_nlp and self.nlp_processor:
            self.nlp_processor.clear_cache()
            logger.info("NLP 处理器缓存已清除")


# 向后兼容的别名
NLPCommandRouter = CommandRouter


def handle_attack(target: str, game: Any) -> Dict[str, Any]:
    """执行攻击指令并返回战斗日志"""
    from .attributes import CharacterAttributes
    from .character import Character, CharacterType
    from .combat import CombatSystem  # local import to avoid circular

    combat_system: CombatSystem = game.combat_system
    player = game.game_state.player

    if not target:
        logger.warning("攻击指令缺少目标")
    if player is None:
        logger.warning("无法执行攻击，player 为 None")

    enemy = Character(
        name=target,
        character_type=CharacterType.MONSTER,
        attributes=CharacterAttributes(),
    )

    result = combat_system.attack(player, enemy)

    # 记录战斗日志
    if hasattr(game.game_state, "logs"):
        game.game_state.logs.append(result.message)

    return {
        "success": result.success,
        "result": result.message,
        "combat_result": {
            "damage": (
                result.damage_dealt.get(enemy.id).damage
                if enemy.id in result.damage_dealt
                else 0
            ),
            "target": enemy.name,
        },
    }
