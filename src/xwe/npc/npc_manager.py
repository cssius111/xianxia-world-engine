from __future__ import annotations

"""Basic NPC management utilities."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.xwe.core.character import Character
from .dialogue_system import DialogueNode, DialogueSystem, DialogueTree


@dataclass
class NPCProfile:
    """NPC profile information."""

    id: str
    name: str
    title: str = ""
    home_location: str = ""
    is_merchant: bool = False
    dialogue_tree: Optional[DialogueTree] = None


@dataclass
class NPCBehavior:
    """Placeholder for NPC behavior configuration."""

    id: str
    description: str = ""


class NPCManager:
    """Manager for NPC profiles and interactions."""

    def __init__(self, dialogue_system: DialogueSystem) -> None:
        self.dialogue_system = dialogue_system
        self.npc_profiles: Dict[str, NPCProfile] = {}
        self.npc_relationships: Dict[str, Dict[str, int]] = {}
        self.npc_locations: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # NPC profile/character utilities
    # ------------------------------------------------------------------
    def add_profile(self, profile: NPCProfile) -> None:
        """Register an NPC profile."""
        self.npc_profiles[profile.id] = profile
        if profile.dialogue_tree:
            self.dialogue_system.register_dialogue_tree(profile.id, profile.dialogue_tree)

    def create_npc_character(self, npc_id: str, template: Dict) -> Optional[Character]:
        """Create an NPC Character from a template."""
        if npc_id not in self.npc_profiles:
            return None
        character = Character.from_template(template)
        return character

    def set_npc_location(self, npc_id: str, location: str) -> None:
        """Set the current location for an NPC."""
        self.npc_locations[npc_id] = location

    def get_npc_profile(self, npc_id: str) -> Optional[NPCProfile]:
        """Retrieve an NPC profile by ID."""
        return self.npc_profiles.get(npc_id)

    def get_available_npcs(self, location: str, player_id: str) -> List[Dict]:
        """List NPCs available at a location."""
        result = []
        for npc_id, profile in self.npc_profiles.items():
            if self.npc_locations.get(npc_id) == location:
                result.append(
                    {
                        "id": npc_id,
                        "name": profile.name,
                        "title": profile.title,
                        "is_merchant": profile.is_merchant,
                        "relationship": self.get_relationship(player_id, npc_id),
                    }
                )
        return result

    # ------------------------------------------------------------------
    # Dialogue helpers
    # ------------------------------------------------------------------
    def start_dialogue(self, player_id: str, npc_id: str, game_time: Optional[int] = None) -> Optional[DialogueNode]:
        """Begin dialogue with an NPC."""
        if player_id not in self.npc_relationships:
            self.npc_relationships[player_id] = {}
        self.npc_relationships[player_id].setdefault(npc_id, 0)
        return self.dialogue_system.start_dialogue(player_id, npc_id)

    def get_relationship(self, player_id: str, npc_id: str) -> int:
        """Return the relationship score between player and NPC."""
        return self.npc_relationships.get(player_id, {}).get(npc_id, 0)
