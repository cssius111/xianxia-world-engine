"""
XWE V2 Application Layer

This layer contains use cases, commands, queries, and application services.
It orchestrates the domain layer to implement business logic.
"""

__all__ = [
    # Services
    "GameService",
    # Commands
    "Command",
    # Events
    "Event",
    "EventBus",
]


# Placeholder exports until properly implemented
class GameService:
    """Main game service."""

    pass


class Command:
    """Base command class."""

    pass


class Event:
    """Base event class."""

    pass


class EventBus:
    """Event bus for publishing domain events."""

    pass
