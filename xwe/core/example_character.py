"""
Example character module for testing migration.
"""

from xwe.core.attributes import CharacterAttributes
from xwe.core.inventory import Inventory


class ExampleCharacter:
    """Example character class to test migration."""

    def __init__(self, name: str):
        self.name = name
        self.attributes = CharacterAttributes()
        self.inventory = Inventory()
        self.level = 1

    def get_status(self) -> str:
        """Get character status."""
        return f"{self.name} - Level {self.level}"

    def level_up(self) -> None:
        """Level up the character."""
        self.level += 1
        self.attributes.strength += 2
        self.attributes.constitution += 1
