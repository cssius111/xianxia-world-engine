from __future__ import annotations

import logging

from ..command_processor import CommandContext, CommandHandler, CommandResult


logger = logging.getLogger(__name__)


class InfoHandler(CommandHandler):
    """Base class for information commands."""


class StatusHandler(InfoHandler):
    commands = ["status"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("StatusHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("StatusHandler result: %s", result)
        return result


class InventoryHandler(InfoHandler):
    commands = ["inventory"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("InventoryHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("InventoryHandler result: %s", result)
        return result


class SkillsHandler(InfoHandler):
    commands = ["skills"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("SkillsHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("SkillsHandler result: %s", result)
        return result


class MapHandler(InfoHandler):
    commands = ["map"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("MapHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("MapHandler result: %s", result)
        return result
