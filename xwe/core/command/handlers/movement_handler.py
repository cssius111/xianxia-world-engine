from __future__ import annotations

from ..command_processor import CommandHandler


class MovementHandler(CommandHandler):
    """Handle movement commands."""

    commands = ["move"]


class ExploreHandler(CommandHandler):
    """Handle exploration commands."""

    commands = ["explore"]
