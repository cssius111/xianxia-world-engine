from __future__ import annotations

"""Simple dialogue system for NPC interactions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class DialogueNodeType(Enum):
    """Types of dialogue nodes."""

    TEXT = "text"
    CHOICE = "choice"


@dataclass
class DialogueNode:
    """A single node in a dialogue tree."""

    id: str
    text: str
    speaker: str = "npc"
    type: DialogueNodeType = DialogueNodeType.TEXT
    children: List["DialogueNode"] = field(default_factory=list)
    next_node: Optional["DialogueNode"] = None
    action: Optional[str] = None


class DialogueTree:
    """Container for a dialogue tree."""

    def __init__(self, root: DialogueNode) -> None:
        self.root = root


class Dialogue:
    """Represents an active dialogue between a player and an NPC."""

    def __init__(self, player_id: str, npc_id: str, tree: DialogueTree) -> None:
        self.player_id = player_id
        self.npc_id = npc_id
        self.tree = tree
        self.current_node = tree.root

    def get_available_choices(self, context: Optional[Dict] = None) -> List[DialogueNode]:
        """Return available choice nodes for the current state."""
        if self.current_node.type is DialogueNodeType.CHOICE:
            return self.current_node.children
        return []

    def advance(self, context: Optional[Dict] = None, choice_id: Optional[str] = None) -> Optional[DialogueNode]:
        """Advance the dialogue using an optional choice identifier."""
        if self.current_node.type is DialogueNodeType.CHOICE and choice_id:
            for child in self.current_node.children:
                if child.id == choice_id:
                    self.current_node = child
                    return child
        elif self.current_node.next_node:
            self.current_node = self.current_node.next_node
            return self.current_node
        return None


class DialogueSystem:
    """Manages NPC dialogue trees and active dialogues."""

    def __init__(self) -> None:
        self.dialogue_trees: Dict[str, DialogueTree] = {}
        self.active_dialogues: Dict[str, Dialogue] = {}

    def register_dialogue_tree(self, npc_id: str, tree: DialogueTree) -> None:
        """Register a dialogue tree for an NPC."""
        self.dialogue_trees[npc_id] = tree

    def start_dialogue(self, player_id: str, npc_id: str) -> Optional[DialogueNode]:
        """Begin a dialogue and return the first node."""
        tree = self.dialogue_trees.get(npc_id)
        if not tree:
            return None
        dialogue = Dialogue(player_id, npc_id, tree)
        self.active_dialogues[player_id] = dialogue
        return dialogue.current_node

    def get_active_dialogue(self, player_id: str) -> Optional[Dialogue]:
        """Retrieve the active dialogue for a player."""
        return self.active_dialogues.get(player_id)

    def advance_dialogue(self, player_id: str, context: Dict, choice_id: Optional[str] = None) -> Optional[DialogueNode]:
        """Advance the player's active dialogue."""
        dialogue = self.active_dialogues.get(player_id)
        if not dialogue:
            return None
        next_node = dialogue.advance(context, choice_id)
        if not next_node:
            self.end_dialogue(player_id)
        return next_node

    def end_dialogue(self, player_id: str) -> None:
        """End and remove a player's active dialogue."""
        self.active_dialogues.pop(player_id, None)
