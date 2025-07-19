"""Combat helper mixins used by GameCore."""

from typing import Any, Optional

from src.xwe.core.character import Character
from src.xwe.core.combat import CombatAction, CombatActionType, CombatState
from src.xwe.core.command_parser import ParsedCommand, CommandType


class CombatMixin:
    def _find_combat_target(self, combat_state: CombatState, target_name: str) -> Optional[Character]:
        for char in combat_state.participants.values():
            if target_name in char.name and char.is_alive:
                return char
        return None

    def _process_combat_command(self, command: ParsedCommand) -> None:  # pragma: no cover - simplified
        pass

    def _process_combat_command_v2(self, cmd_type: str, params: dict) -> None:  # pragma: no cover - simplified
        pass
