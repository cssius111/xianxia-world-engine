"""
XWE V2 Status Effect System

Domain models for character status effects.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class StatusEffectType(Enum):
    """Types of status effects."""

    BUFF = "buff"
    DEBUFF = "debuff"
    DOT = "dot"  # Damage over time
    HOT = "hot"  # Heal over time
    CONTROL = "control"  # Stun, freeze, etc.


@dataclass
class StatusEffect:
    """Represents a status effect on a character."""

    name: str
    effect_type: StatusEffectType
    duration: int  # in turns/ticks
    strength: float = 1.0
    description: str = ""

    def tick(self) -> bool:
        """
        Process one tick of the effect.
        Returns True if effect has expired.
        """
        self.duration -= 1
        return self.duration <= 0


class StatusEffectManager:
    """Manages status effects for a character."""

    def __init__(self):
        self.effects: Dict[str, StatusEffect] = {}

    def add_effect(self, effect: StatusEffect) -> None:
        """Add or refresh a status effect."""
        if effect.name in self.effects:
            # Refresh duration
            existing = self.effects[effect.name]
            existing.duration = max(existing.duration, effect.duration)
            existing.strength = max(existing.strength, effect.strength)
        else:
            self.effects[effect.name] = effect

    def remove_effect(self, name: str) -> None:
        """Remove a status effect."""
        self.effects.pop(name, None)

    def has_effect(self, name: str) -> bool:
        """Check if a status effect is active."""
        return name in self.effects

    def get_effect(self, name: str) -> Optional[StatusEffect]:
        """Get a status effect by name."""
        return self.effects.get(name)

    def update(self) -> List[str]:
        """
        Update all effects (tick down durations).
        Returns list of expired effect names.
        """
        expired = []
        for name, effect in list(self.effects.items()):
            if effect.tick():
                expired.append(name)
                del self.effects[name]
        return expired

    def clear_all(self) -> None:
        """Remove all status effects."""
        self.effects.clear()

    def get_effects_by_type(self, effect_type: StatusEffectType) -> List[StatusEffect]:
        """Get all effects of a specific type."""
        return [e for e in self.effects.values() if e.effect_type == effect_type]
