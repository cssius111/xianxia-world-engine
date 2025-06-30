from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.xwe.core.game_core import GameState
from src.xwe.services import ServiceBase
from src.xwe.services import ServiceContainer


@dataclass
class CommandResult:
    success: bool
    message: str = ""


class IGameService(ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def process_command(self, command: str) -> CommandResult:
        raise NotImplementedError


class GameService(ServiceBase["GameService"], IGameService):
    def __init__(self, container: ServiceContainer) -> None:
        super().__init__(container)
        self.state = GameState()

    def start(self) -> None:
        self.logger.debug("Game started")

    def stop(self) -> None:
        self.logger.debug("Game stopped")

    def process_command(self, command: str) -> CommandResult:
        self.logger.debug("Processing command: %s", command)
        return CommandResult(success=True, message="Command processed")

    def _do_initialize(self) -> None:
        self.logger.debug("GameService initialized")

    def _do_shutdown(self) -> None:
        self.logger.debug("GameService shutdown")
