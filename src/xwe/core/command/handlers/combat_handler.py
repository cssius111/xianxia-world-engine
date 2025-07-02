from __future__ import annotations

import logging

from ..command_processor import CommandContext, CommandHandler, CommandResult


logger = logging.getLogger(__name__)


class CombatHandler(CommandHandler):
    """Base handler for combat related commands."""


class AttackHandler(CombatHandler):
    commands = ["attack"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("AttackHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("AttackHandler result: %s", result)
        return result


class DefendHandler(CombatHandler):
    commands = ["defend"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("DefendHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("DefendHandler result: %s", result)
        return result


class FleeHandler(CombatHandler):
    commands = ["flee"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("FleeHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("FleeHandler result: %s", result)
        return result


class UseSkillHandler(CombatHandler):
    commands = ["use_skill"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("UseSkillHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("UseSkillHandler result: %s", result)
        return result


class CombatCommandHandler(CombatHandler):
    commands = ["attack", "defend", "flee", "use_skill"]

    def handle(self, ctx: CommandContext) -> CommandResult:
        logger.info("CombatCommandHandler invoked with ctx=%s", ctx)
        result = super().handle(ctx)
        logger.info("CombatCommandHandler result: %s", result)
        return result
