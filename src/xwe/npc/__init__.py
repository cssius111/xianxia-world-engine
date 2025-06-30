# npc/__init__.py
"""
NPC系统模块

管理NPC对话、交易和互动。
"""

from .dialogue_system import DialogueNode, DialogueSystem, DialogueTree
from .npc_manager import NPCBehavior, NPCManager, NPCProfile

__all__ = [
    "DialogueSystem",
    "DialogueTree",
    "DialogueNode",
    "NPCManager",
    "NPCProfile",
    "NPCBehavior",
]
