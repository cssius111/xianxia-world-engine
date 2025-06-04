# 这是xwe.core包的__init__.py文件
"""
XWE核心游戏系统模块
"""

from .data_loader import DataLoader
from .attributes import AttributeSystem, CharacterAttributes
from .character import Character
from .inventory import Inventory
from .skills import SkillSystem, Skill
from .combat import CombatSystem, CombatResult
from .ai import AIController
from .status import StatusEffect, StatusEffectManager
from .command_parser import CommandParser
from .game_core import GameCore

__all__ = [
    'DataLoader',
    'AttributeSystem',
    'CharacterAttributes',
    'Character',
    'Inventory',
    'SkillSystem',
    'Skill',
    'CombatSystem',
    'CombatResult',
    'AIController',
    'StatusEffect',
    'StatusEffectManager',
    'CommandParser',
    'GameCore',
]