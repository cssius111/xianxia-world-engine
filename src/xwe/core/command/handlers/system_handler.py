from __future__ import annotations

import logging

from ..command_processor import CommandContext, CommandHandler, CommandResult


logger = logging.getLogger(__name__)


class SystemHandler(CommandHandler):
    """Base class for system commands."""


class SaveHandler(SystemHandler):
    commands = ["save"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("SaveHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("SaveHandler result: %s", result)
        return result


class LoadHandler(SystemHandler):
    commands = ["load"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("LoadHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("LoadHandler result: %s", result)
        return result


class HelpHandler(SystemHandler):
    commands = ["help"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("HelpHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("HelpHandler result: %s", result)
        return result


class QuitHandler(SystemHandler):
    commands = ["quit"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("QuitHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("QuitHandler result: %s", result)
        return result


class SystemCommandHandler(SystemHandler):
    commands = ["help", "save", "load", "quit"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("SystemCommandHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("SystemCommandHandler result: %s", result)
        return result
