from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List


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
    pass


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
        if ctx.command in self.commands:
            return CommandResult(True, f"Executed {ctx.command}")
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
