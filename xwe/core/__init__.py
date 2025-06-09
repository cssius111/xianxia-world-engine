# 这是xwe.core包的__init__.py文件
"""
XWE核心游戏系统模块
"""

from .data_loader import DataLoader
from .attributes import AttributeSystem, CharacterAttributes
from .character import Character
from .skills import SkillSystem, Skill
from .combat import CombatSystem, CombatResult
from .ai import AIController
from .status import StatusEffect, StatusEffectManager
from .command_parser import CommandParser
from .game_core import GameCore

# V3版本新增模块
from .data_manager import DataManager, DM, load_game_data, get_config
from .player_data_manager import PlayerDataManager
from .formula_engine import FormulaEngine, formula_engine, calculate, evaluate_expression
from .cultivation_system import CultivationSystem, cultivation_system, cultivate, attempt_breakthrough
from .combat_system_v3 import CombatSystemV3, Combat, CombatState, combat_system, create_combat
from .event_system_v3 import EventSystemV3, event_system, trigger_events, process_event_choice, register_event_handler
from .npc_system_v3 import NPCSystemV3, NPC, npc_system, create_npc, get_npc, spawn_npcs_for_location

__all__ = [
    'DataLoader',
    'AttributeSystem',
    'CharacterAttributes',
    'Character',
    'SkillSystem',
    'Skill',
    'CombatSystem',
    'CombatResult',
    'AIController',
    'StatusEffect',
    'StatusEffectManager',
    'CommandParser',
    'GameCore',
    # V3版本新增
    'DataManager',
    'PlayerDataManager',
    'DM',
    'load_game_data',
    'get_config',
    'FormulaEngine',
    'formula_engine',
    'calculate',
    'evaluate_expression',
    'CultivationSystem',
    'cultivation_system',
    'cultivate',
    'attempt_breakthrough',
    'CombatSystemV3',
    'Combat',
    'CombatState',
    'combat_system',
    'create_combat',
    # Event System V3
    'EventSystemV3',
    'event_system',
    'trigger_events',
    'process_event_choice',
    'register_event_handler',
    # NPC System V3
    'NPCSystemV3',
    'NPC',
    'npc_system',
    'create_npc',
    'get_npc',
    'spawn_npcs_for_location',
]