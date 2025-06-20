"""
XWE V2 Command System

CQRS command handling for the application layer.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class Command(ABC):
    """Base command class."""

    pass


@dataclass
class CommandResult(Generic[T]):
    """Result of command execution."""

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None


class CommandHandler(ABC, Generic[T]):
    """Base command handler interface."""

    @abstractmethod
    async def handle(self, command: Command) -> CommandResult[T]:
        """Handle a command and return result."""
        pass


class CommandBus:
    """Command bus for routing commands to handlers."""

    def __init__(self):
        self._handlers: Dict[type, CommandHandler] = {}

    def register(self, command_type: type, handler: CommandHandler) -> None:
        """Register a handler for a command type."""
        self._handlers[command_type] = handler

    async def execute(self, command: Command) -> CommandResult:
        """Execute a command."""
        handler = self._handlers.get(type(command))
        if not handler:
            return CommandResult(
                success=False, error=f"No handler registered for {type(command).__name__}"
            )

        try:
            return await handler.handle(command)
        except Exception as e:
            return CommandResult(success=False, error=str(e))


# Example commands
@dataclass
class CreateCharacterCommand(Command):
    """Command to create a new character."""

    name: str
    faction: Optional[str] = None
    is_player: bool = False


@dataclass
class StartCombatCommand(Command):
    """Command to start combat."""

    participants: list[str]


@dataclass
class ProcessActionCommand(Command):
    """Command to process a game action."""

    action: str
    args: list[str]


__all__ = [
    "Command",
    "CommandResult",
    "CommandHandler",
    "CommandBus",
    "CreateCharacterCommand",
    "StartCombatCommand",
    "ProcessActionCommand",
]
