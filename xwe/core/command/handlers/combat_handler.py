from __future__ import annotations

from ..command_processor import CommandContext, CommandHandler, CommandResult


class CombatHandler(CommandHandler):
    """Base handler for combat related commands."""


class AttackHandler(CombatHandler):
    commands = ["attack"]


class DefendHandler(CombatHandler):
    commands = ["defend"]


class FleeHandler(CombatHandler):
    commands = ["flee"]


class UseSkillHandler(CombatHandler):
    commands = ["use_skill"]


class CombatCommandHandler(CombatHandler):
    commands = ["attack", "defend", "flee", "use_skill"]
