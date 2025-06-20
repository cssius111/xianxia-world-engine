"""
命令处理器 - 统一的命令处理框架

负责管理游戏中的所有命令处理，包括：
- 命令注册和路由
- 命令验证和权限
- 中间件支持
- 命令历史和撤销
- 上下文感知的命令处理
"""

import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

from xwe_v2.core.command_parser import CommandParser, CommandType, ParsedCommand
from xwe_v2.core.output import MessageType, OutputManager
from xwe_v2.core.state import GameContext, GameStateManager

logger = logging.getLogger(__name__)


class CommandPriority(Enum):
    """命令优先级"""

    SYSTEM = 100  # 系统命令（最高）
    CRITICAL = 80  # 关键命令
    HIGH = 60  # 高优先级
    NORMAL = 40  # 普通
    LOW = 20  # 低优先级


class CommandResult:
    """命令执行结果"""

    def __init__(
        self,
        success: bool = True,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        continue_processing: bool = True,
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.error = error
        self.continue_processing = continue_processing
        self.timestamp = datetime.now()

    @classmethod
    def success(cls, message: str = "", **data) -> "CommandResult":
        """创建成功结果"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def failure(cls, error: str, continue_processing: bool = False) -> "CommandResult":
        """创建失败结果"""
        return cls(success=False, error=error, continue_processing=continue_processing)

    @classmethod
    def redirect(cls, new_command: str) -> "CommandResult":
        """重定向到新命令"""
        return cls(success=True, data={"redirect": new_command})


@dataclass
class CommandContext:
    """命令执行上下文"""

    command: ParsedCommand
    state_manager: GameStateManager
    output_manager: OutputManager
    raw_input: str
    source: str = "player"  # player, npc, system, script
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_player(self):
        """获取玩家角色"""
        return self.state_manager.get_player()

    def get_current_location(self):
        """获取当前位置"""
        return self.state_manager.get_location()

    def get_game_context(self):
        """获取游戏上下文"""
        return self.state_manager.get_current_context()

    def get_flag(self, key: str, default: Any = None) -> Any:
        """获取游戏标记"""
        return self.state_manager.get_flag(key, default)

    def set_flag(self, key: str, value: Any) -> None:
        """设置游戏标记"""
        self.state_manager.set_flag(key, value)


class CommandHandler(ABC):
    """命令处理器基类"""

    def __init__(
        self,
        name: str,
        command_types: List[CommandType],
        priority: CommandPriority = CommandPriority.NORMAL,
    ):
        self.name = name
        self.command_types = command_types
        self.priority = priority
        self.enabled = True

    @abstractmethod
    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理此命令"""
        pass

    @abstractmethod
    def handle(self, context: CommandContext) -> CommandResult:
        """处理命令"""
        pass

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证命令，返回错误信息或None"""
        return None

    def get_help(self) -> str:
        """获取帮助信息"""
        return f"{self.name}: 处理 {', '.join(ct.value for ct in self.command_types)}"


class Middleware(ABC):
    """中间件基类"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    @abstractmethod
    async def process(self, context: CommandContext, next_handler: Callable) -> CommandResult:
        """处理请求"""
        pass


class CommandProcessor:
    """
    命令处理器主类

    负责管理和执行所有游戏命令
    """

    def __init__(self, state_manager: GameStateManager, output_manager: OutputManager):
        """
        初始化命令处理器

        Args:
            state_manager: 游戏状态管理器
            output_manager: 输出管理器
        """
        self.state_manager = state_manager
        self.output_manager = output_manager
        self.command_parser = CommandParser()

        # 命令处理器注册表
        self.handlers: Dict[CommandType, List[CommandHandler]] = {}
        self.handler_registry: Dict[str, CommandHandler] = {}

        # 中间件
        self.middlewares: List[Middleware] = []

        # 命令历史
        self.command_history: deque = deque(maxlen=100)
        self.undo_stack: deque = deque(maxlen=20)

        # 命令别名
        self.aliases: Dict[str, str] = {}

        # 权限系统
        self.permissions: Dict[str, Set[CommandType]] = {
            "player": set(CommandType),  # 玩家默认拥有所有权限
            "npc": {CommandType.TALK, CommandType.TRADE},  # NPC只能对话和交易
            "system": set(CommandType),  # 系统拥有所有权限
        }

        # 初始化默认处理器
        self._init_default_handlers()

        logger.info("命令处理器初始化完成")

    def register_handler(self, handler: CommandHandler) -> None:
        """
        注册命令处理器

        Args:
            handler: 命令处理器实例
        """
        # 注册到类型映射
        for cmd_type in handler.command_types:
            if cmd_type not in self.handlers:
                self.handlers[cmd_type] = []

            # 按优先级插入
            handlers = self.handlers[cmd_type]
            insert_pos = 0
            for i, h in enumerate(handlers):
                if handler.priority.value > h.priority.value:
                    insert_pos = i
                    break
                insert_pos = i + 1
            handlers.insert(insert_pos, handler)

        # 注册到名称映射
        self.handler_registry[handler.name] = handler

        logger.info(f"注册命令处理器: {handler.name}")

    def unregister_handler(self, name: str) -> None:
        """
        注销命令处理器

        Args:
            name: 处理器名称
        """
        if name in self.handler_registry:
            handler = self.handler_registry.pop(name)

            # 从类型映射中移除
            for cmd_type in handler.command_types:
                if cmd_type in self.handlers:
                    self.handlers[cmd_type] = [h for h in self.handlers[cmd_type] if h.name != name]

            logger.info(f"注销命令处理器: {name}")

    def add_middleware(self, middleware: Middleware) -> None:
        """添加中间件"""
        self.middlewares.append(middleware)
        logger.info(f"添加中间件: {middleware.name}")

    def add_alias(self, alias: str, command: str) -> None:
        """添加命令别名"""
        self.aliases[alias.lower()] = command

    def process_command(self, raw_input: str, source: str = "player") -> CommandResult:
        """
        处理命令（同步接口）

        Args:
            raw_input: 原始输入
            source: 命令来源

        Returns:
            命令执行结果
        """
        # 运行异步方法
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.process_command_async(raw_input, source))
        finally:
            loop.close()

    async def process_command_async(self, raw_input: str, source: str = "player") -> CommandResult:
        """
        处理命令（异步）

        Args:
            raw_input: 原始输入
            source: 命令来源

        Returns:
            命令执行结果
        """
        # 预处理输入
        processed_input = self._preprocess_input(raw_input)

        # 解析命令
        parsed_command = self.command_parser.parse(processed_input)

        # 创建上下文
        context = CommandContext(
            command=parsed_command,
            state_manager=self.state_manager,
            output_manager=self.output_manager,
            raw_input=raw_input,
            source=source,
        )

        # 检查权限
        if not self._check_permission(context):
            return CommandResult.failure("你没有权限执行此命令")

        # 记录历史
        self._record_history(context)

        # 通过中间件处理
        return await self._process_with_middleware(context)

    def _preprocess_input(self, raw_input: str) -> str:
        """预处理输入"""
        # 去除首尾空白
        processed = raw_input.strip()

        # 应用别名
        lower_input = processed.lower()
        for alias, replacement in self.aliases.items():
            if lower_input.startswith(alias):
                processed = replacement + processed[len(alias) :]
                break

        return processed

    def _check_permission(self, context: CommandContext) -> bool:
        """检查权限"""
        source_permissions = self.permissions.get(context.source, set())
        return context.command.command_type in source_permissions

    def _record_history(self, context: CommandContext) -> None:
        """记录命令历史"""
        self.command_history.append(
            {
                "timestamp": datetime.now(),
                "raw_input": context.raw_input,
                "command_type": context.command.command_type,
                "source": context.source,
                "success": None,  # 将在执行后更新
            }
        )

    async def _process_with_middleware(self, context: CommandContext) -> CommandResult:
        """通过中间件处理命令"""

        # 构建中间件链
        async def execute_handler():
            return await self._execute_command(context)

        # 从最后一个中间件开始构建链
        next_handler = execute_handler
        for middleware in reversed(self.middlewares):
            if middleware.enabled:
                # 捕获当前中间件
                current_middleware = middleware
                current_next = next_handler

                async def wrapped_handler():
                    return await current_middleware.process(context, current_next)

                next_handler = wrapped_handler

        # 执行链
        result = await next_handler()

        # 更新历史记录
        if self.command_history:
            self.command_history[-1]["success"] = result.success

        return result

    async def _execute_command(self, context: CommandContext) -> CommandResult:
        """执行命令"""
        command_type = context.command.command_type

        # 处理未知命令
        if command_type == CommandType.UNKNOWN:
            return self._handle_unknown_command(context)

        # 获取该类型的所有处理器
        handlers = self.handlers.get(command_type, [])

        # 找到第一个可以处理的
        for handler in handlers:
            if handler.enabled and handler.can_handle(context):
                # 验证命令
                error = handler.validate(context)
                if error:
                    return CommandResult.failure(error)

                # 执行处理器
                try:
                    result = handler.handle(context)

                    # 如果成功且支持撤销，记录到撤销栈
                    if result.success and hasattr(handler, "undo"):
                        self.undo_stack.append((context, handler))

                    return result

                except Exception as e:
                    logger.error(f"命令处理器 {handler.name} 执行失败: {e}")
                    return CommandResult.failure(f"命令执行失败: {str(e)}")

        # 没有找到合适的处理器
        return CommandResult.failure(f"无法处理命令: {command_type.value}")

    def _handle_unknown_command(self, context: CommandContext) -> CommandResult:
        """处理未知命令"""
        suggestions = self.get_suggestions(context.raw_input)

        if suggestions:
            context.output_manager.warning("无法识别的命令。")
            context.output_manager.info("你是想输入：")
            for suggestion in suggestions[:5]:
                context.output_manager.info(f"  - {suggestion}")
        else:
            context.output_manager.error("无法识别的命令。输入 '帮助' 查看可用命令。")

        return CommandResult.failure("未知命令", continue_processing=True)

    def get_suggestions(self, partial_input: str) -> List[str]:
        """获取命令建议"""
        suggestions = []

        # 从命令解析器获取建议
        parser_suggestions = self.command_parser.suggest_command(partial_input)
        suggestions.extend(parser_suggestions)

        # 从别名中查找
        for alias, command in self.aliases.items():
            if alias.startswith(partial_input.lower()):
                suggestions.append(alias)

        # 从历史中查找
        for entry in list(self.command_history)[-20:]:  # 最近20条
            if entry["raw_input"].startswith(partial_input):
                suggestions.append(entry["raw_input"])

        # 去重并返回
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)

        return unique_suggestions

    def undo_last_command(self) -> CommandResult:
        """撤销上一个命令"""
        if not self.undo_stack:
            return CommandResult.failure("没有可以撤销的命令")

        context, handler = self.undo_stack.pop()

        if hasattr(handler, "undo"):
            try:
                result = handler.undo(context)
                self.output_manager.success("命令已撤销")
                return result
            except Exception as e:
                logger.error(f"撤销命令失败: {e}")
                return CommandResult.failure(f"撤销失败: {str(e)}")

        return CommandResult.failure("该命令不支持撤销")

    def get_help(self, command_type: Optional[CommandType] = None) -> str:
        """获取帮助信息"""
        if command_type:
            # 获取特定命令的帮助
            handlers = self.handlers.get(command_type, [])
            if handlers:
                help_text = f"=== {command_type.value} 命令帮助 ===\n\n"
                for handler in handlers:
                    help_text += handler.get_help() + "\n\n"
                return help_text
            else:
                return f"没有找到 {command_type.value} 命令的帮助信息"

        # 获取所有命令的帮助
        return self.command_parser.get_help_text()

    def get_command_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取命令历史"""
        return list(self.command_history)[-count:]

    def clear_history(self) -> None:
        """清空历史"""
        self.command_history.clear()
        self.undo_stack.clear()

    def _init_default_handlers(self) -> None:
        """初始化默认处理器"""
        # 这里可以注册一些基本的命令处理器
        # 实际的处理器会在 handlers 子模块中实现
        pass


# === 内置中间件 ===


class LoggingMiddleware(Middleware):
    """日志中间件"""

    async def process(self, context: CommandContext, next_handler: Callable) -> CommandResult:
        """记录命令执行"""
        start_time = datetime.now()

        logger.info(f"[{context.source}] 执行命令: {context.raw_input}")

        # 执行下一个处理器
        result = await next_handler()

        # 记录结果
        duration = (datetime.now() - start_time).total_seconds()
        status = "成功" if result.success else "失败"
        logger.info(f"命令执行{status}，耗时: {duration:.3f}秒")

        return result


class ValidationMiddleware(Middleware):
    """验证中间件"""

    async def process(self, context: CommandContext, next_handler: Callable) -> CommandResult:
        """验证命令"""
        # 检查玩家状态
        if not context.player and context.source == "player":
            return CommandResult.failure("游戏尚未开始")

        # 检查游戏上下文
        game_context = context.game_context

        # 战斗中只能使用战斗相关命令
        if game_context == GameContext.COMBAT:
            allowed_in_combat = {
                CommandType.ATTACK,
                CommandType.USE_SKILL,
                CommandType.DEFEND,
                CommandType.FLEE,
                CommandType.USE_ITEM,
                CommandType.STATUS,
            }
            if context.command.command_type not in allowed_in_combat:
                return CommandResult.failure("战斗中无法执行此命令")

        # 对话中限制某些命令
        elif game_context == GameContext.DIALOGUE:
            forbidden_in_dialogue = {CommandType.MOVE, CommandType.ATTACK, CommandType.CULTIVATE}
            if context.command.command_type in forbidden_in_dialogue:
                return CommandResult.failure("对话中无法执行此命令")

        return await next_handler()


class CooldownMiddleware(Middleware):
    """冷却时间中间件"""

    def __init__(self):
        super().__init__("cooldown")
        self.cooldowns: Dict[str, Dict[CommandType, datetime]] = {}
        self.cooldown_times = {
            CommandType.CULTIVATE: 5.0,  # 修炼冷却5秒
            CommandType.USE_SKILL: 2.0,  # 技能冷却2秒
            CommandType.SAVE: 10.0,  # 保存冷却10秒
        }

    async def process(self, context: CommandContext, next_handler: Callable) -> CommandResult:
        """检查冷却时间"""
        cmd_type = context.command.command_type

        # 检查是否需要冷却
        if cmd_type not in self.cooldown_times:
            return await next_handler()

        # 获取用户冷却记录
        user_id = context.source
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = {}

        # 检查冷却
        last_use = self.cooldowns[user_id].get(cmd_type)
        if last_use:
            elapsed = (datetime.now() - last_use).total_seconds()
            cooldown = self.cooldown_times[cmd_type]

            if elapsed < cooldown:
                remaining = cooldown - elapsed
                return CommandResult.failure(f"命令冷却中，请等待 {remaining:.1f} 秒")

        # 执行命令
        result = await next_handler()

        # 如果成功，记录使用时间
        if result.success:
            self.cooldowns[user_id][cmd_type] = datetime.now()

        return result


class RateLimitMiddleware(Middleware):
    """速率限制中间件"""

    def __init__(self, max_commands: int = 10, window: float = 60.0):
        super().__init__("rate_limit")
        self.max_commands = max_commands
        self.window = window  # 时间窗口（秒）
        self.command_times: Dict[str, deque] = {}

    async def process(self, context: CommandContext, next_handler: Callable) -> CommandResult:
        """检查速率限制"""
        user_id = context.source
        now = datetime.now()

        # 初始化用户记录
        if user_id not in self.command_times:
            self.command_times[user_id] = deque()

        times = self.command_times[user_id]

        # 清理过期记录
        while times and (now - times[0]).total_seconds() > self.window:
            times.popleft()

        # 检查是否超过限制
        if len(times) >= self.max_commands:
            return CommandResult.failure(
                f"命令太频繁，请稍后再试（{self.window}秒内最多{self.max_commands}条）"
            )

        # 记录本次命令
        times.append(now)

        # 执行命令
        return await next_handler()


# 导出主要类
__all__ = [
    "CommandProcessor",
    "CommandHandler",
    "CommandContext",
    "CommandResult",
    "CommandPriority",
    "Middleware",
    "LoggingMiddleware",
    "ValidationMiddleware",
    "CooldownMiddleware",
    "RateLimitMiddleware",
]
