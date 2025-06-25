from __future__ import annotations

from ..command_processor import CommandHandler


class CultivationHandler(CommandHandler):
    """Base class for cultivation related commands."""


class CultivateHandler(CultivationHandler):
    commands = ["cultivate"]


class LearnSkillHandler(CultivationHandler):
    commands = ["learn"]


class BreakthroughHandler(CultivationHandler):
    commands = ["breakthrough"]


class UseItemHandler(CultivationHandler):
    commands = ["use_item"]


class CultivationCommandHandler(CultivationHandler):
    commands = ["cultivate", "learn", "breakthrough", "use_item"]
