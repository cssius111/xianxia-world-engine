from __future__ import annotations

from ..command_processor import CommandHandler


class InfoHandler(CommandHandler):
    """Base class for information commands."""


class StatusHandler(InfoHandler):
    commands = ["status"]


class InventoryHandler(InfoHandler):
    commands = ["inventory"]


class SkillsHandler(InfoHandler):
    commands = ["skills"]


class MapHandler(InfoHandler):
    commands = ["map"]
