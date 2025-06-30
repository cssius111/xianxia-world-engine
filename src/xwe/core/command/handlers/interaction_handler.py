from __future__ import annotations

from ..command_processor import CommandHandler


class InteractionHandler(CommandHandler):
    """Base class for interaction commands."""


class TalkHandler(InteractionHandler):
    commands = ["talk"]


class TradeHandler(InteractionHandler):
    commands = ["trade"]


class PickUpHandler(InteractionHandler):
    commands = ["pickup"]


class InteractionCommandHandler(InteractionHandler):
    commands = ["talk", "trade", "pickup"]
