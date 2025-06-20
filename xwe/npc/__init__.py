# npc/__init__.py
"""
NPC系统模块

管理NPC对话、交易和互动。
"""

from .dialogue_system import DialogueNode, DialogueSystem, DialogueTree
from .emotion_system import EmotionSystem, EmotionType, PersonalityTrait
from .enhanced_dialogue import DialogueContext, EnhancedDialogueSystem
from .memory_system import Memory, MemorySystem, MemoryType
from .npc_manager import NPCBehavior, NPCManager, NPCProfile
from .trading_system import TradingSystem

__all__ = [
    "DialogueSystem",
    "DialogueTree",
    "DialogueNode",
    "NPCManager",
    "NPCProfile",
    "NPCBehavior",
    "TradingSystem",
    "EmotionSystem",
    "EmotionType",
    "PersonalityTrait",
    "MemorySystem",
    "Memory",
    "MemoryType",
    "EnhancedDialogueSystem",
    "DialogueContext",
]
