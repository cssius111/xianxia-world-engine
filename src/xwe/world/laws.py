"""World laws data structures and loading utilities."""

from __future__ import annotations
from dataclasses import dataclass, field
import json
import pathlib
from typing import Dict, Any


@dataclass
class WorldLaw:
    """Represents a single world law/rule."""
    
    code: str
    name: str = ""
    description: str = ""
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)


def load_world_laws(path: str | pathlib.Path = "data/world_laws.json") -> Dict[str, WorldLaw]:
    """Load world laws from JSON file.
    
    Args:
        path: Path to the world laws JSON file
        
    Returns:
        Dictionary mapping law codes to WorldLaw instances
    """
    path = pathlib.Path(path)
    
    # Try multiple possible locations
    if not path.exists():
        # Try relative to project root
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        path = project_root / path
    
    if not path.exists():
        # Return default laws if file not found
        return {
            "CROSS_REALM_KILL": WorldLaw(
                code="CROSS_REALM_KILL",
                name="跨境界斩杀限制",
                description="高境界修士不可随意斩杀低境界修士",
                enabled=True,
                params={"max_gap": 2}
            )
        }
    
    with open(path, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    
    laws = {}
    for item in data.get("laws", []):
        law = WorldLaw(**item)
        laws[law.code] = law
    
    return laws
