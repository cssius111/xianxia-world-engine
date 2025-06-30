from __future__ import annotations

from ..command_processor import CommandHandler


class SystemHandler(CommandHandler):
    """Base class for system commands."""


class SaveHandler(SystemHandler):
    commands = ["save"]


class LoadHandler(SystemHandler):
    commands = ["load"]


class HelpHandler(SystemHandler):
    commands = ["help"]


class QuitHandler(SystemHandler):
    commands = ["quit"]


class SystemCommandHandler(SystemHandler):
    commands = ["help", "save", "load", "quit"]
