from __future__ import annotations

import logging

from ..command_processor import CommandContext, CommandHandler, CommandResult


logger = logging.getLogger(__name__)


class CultivationHandler(CommandHandler):
    """Base class for cultivation related commands."""


class CultivateHandler(CultivationHandler):
    commands = ["cultivate"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("CultivateHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("CultivateHandler result: %s", result)
        return result


class LearnSkillHandler(CultivationHandler):
    commands = ["learn"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("LearnSkillHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("LearnSkillHandler result: %s", result)
        return result


class BreakthroughHandler(CultivationHandler):
    commands = ["breakthrough"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("BreakthroughHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("BreakthroughHandler result: %s", result)
        return result


class UseItemHandler(CultivationHandler):
    commands = ["use_item"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("UseItemHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("UseItemHandler result: %s", result)
        return result


class CultivationCommandHandler(CultivationHandler):
    commands = ["cultivate", "learn", "breakthrough", "use_item"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("CultivationCommandHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("CultivationCommandHandler result: %s", result)
        return result
