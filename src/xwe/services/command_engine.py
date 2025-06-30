from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from src.xwe.services import ServiceBase
from src.xwe.services import ServiceContainer


@dataclass
class CommandContext:
    command: str
    args: Dict[str, Any] | None = None


@dataclass
class CommandResult:
    success: bool
    message: str = ""


class ICommandHandler(ABC):
    @abstractmethod
    def handle(self, ctx: CommandContext) -> CommandResult:
        raise NotImplementedError


class ICommandEngine(ABC):
    @abstractmethod
    def register_handler(self, handler: ICommandHandler) -> None:
        raise NotImplementedError

    @abstractmethod
    def execute(self, ctx: CommandContext) -> CommandResult:
        raise NotImplementedError


class CommandEngine(ServiceBase["CommandEngine"], ICommandEngine):
    def __init__(self, container: ServiceContainer) -> None:
        super().__init__(container)
        self._handlers: List[ICommandHandler] = []

    def register_handler(self, handler: ICommandHandler) -> None:
        self.logger.debug("Registering command handler %s", handler)
        self._handlers.append(handler)

    def execute(self, ctx: CommandContext) -> CommandResult:
        for handler in self._handlers:
            try:
                result = handler.handle(ctx)
                if result.success:
                    return result
            except Exception as exc:  # pragma: no cover - simple wrapper
                self.logger.error("Handler error: %s", exc)
        return CommandResult(success=False, message="Unhandled command")

    def _do_initialize(self) -> None:
        self.logger.debug("CommandEngine initialized")

    def _do_shutdown(self) -> None:
        self.logger.debug("CommandEngine shutdown")
