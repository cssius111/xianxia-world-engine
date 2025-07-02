from __future__ import annotations

import logging

from ..command_processor import CommandContext, CommandHandler, CommandResult


logger = logging.getLogger(__name__)


class InteractionHandler(CommandHandler):
    """Base class for interaction commands."""


class TalkHandler(InteractionHandler):
    commands = ["talk"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("TalkHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("TalkHandler result: %s", result)
        return result


class TradeHandler(InteractionHandler):
    commands = ["trade"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("TradeHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("TradeHandler result: %s", result)
        return result


class PickUpHandler(InteractionHandler):
    commands = ["pickup"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("PickUpHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("PickUpHandler result: %s", result)
        return result


class InteractionCommandHandler(InteractionHandler):
    commands = ["talk", "trade", "pickup"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("InteractionCommandHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("InteractionCommandHandler result: %s", result)
        return result
