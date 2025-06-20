"""
XWE V2 Character Attributes

Domain models for character attributes.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CharacterAttributes:
    """Character attributes in v2 format."""

    # Basic attributes
    strength: int = 10
    agility: int = 10
    intelligence: int = 10
    constitution: int = 10

    # Combat attributes
    attack_power: int = 10
    defense: int = 5

    # Resources
    max_health: int = 100
    current_health: int = 100
    max_mana: int = 50
    current_mana: int = 50
    max_stamina: int = 100
    current_stamina: int = 100

    # Cultivation
    cultivation_level: int = 1
    realm_name: str = "聚气期"
    realm_level: int = 1

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary format."""
        return {
            "strength": self.strength,
            "agility": self.agility,
            "intelligence": self.intelligence,
            "constitution": self.constitution,
            "attack_power": self.attack_power,
            "defense": self.defense,
            "max_health": self.max_health,
            "current_health": self.current_health,
            "max_mana": self.max_mana,
            "current_mana": self.current_mana,
            "max_stamina": self.max_stamina,
            "current_stamina": self.current_stamina,
            "cultivation_level": self.cultivation_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "CharacterAttributes":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


class AttributeSystem:
    """System for managing character attributes."""

    def calculate_derived_attributes(self, attrs: CharacterAttributes) -> None:
        """Calculate derived attributes based on base attributes."""
        # Health based on constitution
        attrs.max_health = 100 + (attrs.constitution * 10)

        # Mana based on intelligence
        attrs.max_mana = 50 + (attrs.intelligence * 5)

        # Stamina based on constitution and strength
        attrs.max_stamina = 100 + ((attrs.constitution + attrs.strength) * 3)

        # Attack based on strength
        attrs.attack_power = 10 + (attrs.strength * 2)

        # Defense based on constitution
        attrs.defense = 5 + attrs.constitution
