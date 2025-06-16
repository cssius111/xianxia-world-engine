# npc/__init__.py
"""
NPC系统模块

管理NPC对话、交易和互动。
"""

from .dialogue_system import DialogueSystem, DialogueTree, DialogueNode
from .npc_manager import NPCManager, NPCProfile, NPCBehavior
from .trading_system import TradingSystem
from .emotion_system import EmotionSystem, EmotionType, PersonalityTrait
from .memory_system import MemorySystem, Memory, MemoryType
from .enhanced_dialogue import EnhancedDialogueSystem, DialogueContext

__all__ = [
    'DialogueSystem', 'DialogueTree', 'DialogueNode',
    'NPCManager', 'NPCProfile', 'NPCBehavior',
    'TradingSystem',
    'EmotionSystem', 'EmotionType', 'PersonalityTrait',
    'MemorySystem', 'Memory', 'MemoryType',
    'EnhancedDialogueSystem', 'DialogueContext'
]
