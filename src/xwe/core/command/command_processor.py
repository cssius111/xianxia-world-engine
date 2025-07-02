from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List
import logging

logger = logging.getLogger("xwe.command")


@dataclass
class CommandContext:
    """Context information for command execution."""

    command: str
    args: dict | None = None


@dataclass
class CommandResult:
    """Result returned by a command handler."""

    success: bool
    message: str = ""


class CommandPriority(Enum):
    """Simple command priority enumeration."""

    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()


class Middleware:
    """Base middleware class."""

    def before_handle(self, ctx: CommandContext) -> None:  # pragma: no cover - simple hook
        pass

    def after_handle(self, ctx: CommandContext, result: CommandResult) -> None:  # pragma: no cover - simple hook
        pass


class LoggingMiddleware(Middleware):
    def before_handle(self, ctx: CommandContext) -> None:  # pragma: no cover - simple log
        logger.debug(f"[Middleware] 即将执行 {ctx.command} args={ctx.args}")

    def after_handle(self, ctx: CommandContext, result: CommandResult) -> None:  # pragma: no cover - simple log
        logger.debug(
            f"[Middleware] {ctx.command} 执行结果: {result.success} - {result.message}"
        )


class ValidationMiddleware(Middleware):
    pass


class CooldownMiddleware(Middleware):
    pass


class RateLimitMiddleware(Middleware):
    pass


class CommandHandler:
    """Base class for command handlers."""

    commands: List[str] = []

    def handle(self, ctx: CommandContext) -> CommandResult:  # pragma: no cover - simple placeholder
        logger.debug(
            f"[Handler:{self.__class__.__name__}] 接收到命令 {ctx.command} args={ctx.args}"
        )
        try:
            if ctx.command in self.commands:
                result = CommandResult(True, f"Executed {ctx.command}")
            else:
                result = CommandResult(False, "")
            logger.debug(
                f"[Handler:{self.__class__.__name__}] 返回: {result.success} - {result.message}"
            )
            return result
        except Exception:
            logger.exception(f"[Handler:{self.__class__.__name__}] 执行异常")
            return CommandResult(False, "")


class CommandProcessor:
    """Minimal command processor that dispatches commands to handlers."""

    def __init__(self) -> None:
        self.handlers: List[CommandHandler] = []
        self.middlewares: List[Middleware] = []

    def add_handler(self, handler: CommandHandler) -> None:
        self.handlers.append(handler)

    def add_middleware(self, middleware: Middleware) -> None:
        self.middlewares.append(middleware)

    def process(self, ctx: CommandContext) -> CommandResult:
        for middleware in self.middlewares:
            middleware.before_handle(ctx)
        for handler in self.handlers:
            result = handler.handle(ctx)
            if result.success:
                for middleware in self.middlewares:
                    middleware.after_handle(ctx, result)
                return result
        result = CommandResult(False, "Command not handled")
        for middleware in self.middlewares:
            middleware.after_handle(ctx, result)
        return result
