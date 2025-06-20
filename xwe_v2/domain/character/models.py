from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Attribute:
    name: str
    value: int

    def __init__(self, name: str, value: int = 0):
        self.name = name
        self.value = value


@dataclass
class Character:
    name: str
    level: int
    attributes: List[Attribute]
    faction: Optional[str] = None

    def get_attribute(self, name: str) -> Optional[int]:
        for attr in self.attributes:
            if attr.name == name:
                return attr.value
        return None

    def is_alive(self) -> bool:
        return self.get_attribute("HP") is None or self.get_attribute("HP") > 0
