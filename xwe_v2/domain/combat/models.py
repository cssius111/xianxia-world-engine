"""
XWE V2 Combat System

Domain models for combat mechanics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class DamageType(Enum):
    """Types of damage in combat."""

    PHYSICAL = "physical"
    MAGICAL = "magical"
    TRUE = "true"  # Ignores defense
    ELEMENTAL = "elemental"


class CombatState(Enum):
    """States of combat."""

    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    ENDED = "ended"


@dataclass
class CombatAction:
    """Represents a single combat action."""

    actor_id: str
    target_id: str
    action_type: str  # "attack", "skill", "defend", etc.
    skill_id: Optional[str] = None
    damage: float = 0.0
    damage_type: DamageType = DamageType.PHYSICAL
    effects: List[str] = field(default_factory=list)


@dataclass
class CombatResult:
    """Result of a combat action."""

    success: bool
    damage_dealt: float = 0.0
    healing_done: float = 0.0
    effects_applied: List[str] = field(default_factory=list)
    message: str = ""


class CombatSystem:
    """Core combat system logic."""

    def __init__(self):
        self.state = CombatState.PREPARING
        self.participants: Dict[str, Dict] = {}  # participant_id -> stats
        self.turn_order: List[str] = []
        self.current_turn: int = 0
        self.combat_log: List[str] = []

    def add_participant(self, participant_id: str, stats: Dict) -> None:
        """Add a participant to combat."""
        self.participants[participant_id] = stats

    def remove_participant(self, participant_id: str) -> None:
        """Remove a participant from combat."""
        self.participants.pop(participant_id, None)
        if participant_id in self.turn_order:
            self.turn_order.remove(participant_id)

    def start_combat(self) -> None:
        """Initialize combat and determine turn order."""
        if not self.participants:
            raise ValueError("Cannot start combat without participants")

        # Calculate turn order based on agility/speed
        self.turn_order = sorted(
            self.participants.keys(),
            key=lambda p: self.participants[p].get("agility", 0),
            reverse=True,
        )
        self.current_turn = 0
        self.state = CombatState.IN_PROGRESS
        self.combat_log.append("战斗开始！")

    def get_current_actor(self) -> Optional[str]:
        """Get the current actor's ID."""
        if self.state != CombatState.IN_PROGRESS or not self.turn_order:
            return None
        return self.turn_order[self.current_turn % len(self.turn_order)]

    def process_action(self, action: CombatAction) -> CombatResult:
        """Process a combat action."""
        if self.state != CombatState.IN_PROGRESS:
            return CombatResult(success=False, message="Combat not in progress")

        # Validate action
        if action.actor_id != self.get_current_actor():
            return CombatResult(success=False, message="Not your turn")

        if action.target_id not in self.participants:
            return CombatResult(success=False, message="Invalid target")

        # Calculate damage
        actor_stats = self.participants[action.actor_id]
        target_stats = self.participants[action.target_id]

        base_damage = action.damage or actor_stats.get("attack_power", 10)
        defense = target_stats.get("defense", 0)

        # Apply damage type modifiers
        if action.damage_type == DamageType.TRUE:
            final_damage = base_damage
        else:
            final_damage = max(1, base_damage - defense)

        # Apply damage
        target_stats["current_health"] = max(
            0, target_stats.get("current_health", 100) - final_damage
        )

        # Log action
        self.combat_log.append(
            f"{action.actor_id} 对 {action.target_id} 造成了 {final_damage} 点伤害"
        )

        # Check if target is defeated
        if target_stats["current_health"] <= 0:
            self.combat_log.append(f"{action.target_id} 被击败了！")
            self.remove_participant(action.target_id)

        # Check win condition
        self._check_combat_end()

        # Advance turn
        if self.state == CombatState.IN_PROGRESS:
            self.current_turn += 1

        return CombatResult(
            success=True, damage_dealt=final_damage, message=f"造成 {final_damage} 点伤害"
        )

    def _check_combat_end(self) -> None:
        """Check if combat should end."""
        # Get unique teams/factions
        teams = set()
        for participant_id, stats in self.participants.items():
            teams.add(stats.get("team", participant_id))

        # Combat ends when only one team remains
        if len(teams) <= 1:
            self.state = CombatState.ENDED
            if teams:
                winner = next(iter(teams))
                self.combat_log.append(f"战斗结束！{winner} 获胜！")
            else:
                self.combat_log.append("战斗结束！平局！")

    def end_combat(self) -> None:
        """Forcefully end combat."""
        self.state = CombatState.ENDED
        self.combat_log.append("战斗被中断！")

    def get_combat_status(self) -> Dict:
        """Get current combat status."""
        return {
            "state": self.state.value,
            "current_actor": self.get_current_actor(),
            "participants": list(self.participants.keys()),
            "turn": self.current_turn,
            "log": self.combat_log[-10:],  # Last 10 log entries
        }


# Global combat system instance (for compatibility)
combat_system = CombatSystem()
