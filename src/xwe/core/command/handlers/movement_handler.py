from __future__ import annotations

import logging

from ..command_processor import CommandContext, CommandHandler, CommandResult


logger = logging.getLogger(__name__)


class MovementHandler(CommandHandler):
    """Handle movement commands."""

    commands = ["move"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("MovementHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("MovementHandler result: %s", result)
        return result


class ExploreHandler(CommandHandler):
    """Handle exploration commands."""

    commands = ["explore"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("ExploreHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("ExploreHandler result: %s", result)
        return result
