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
from .event_system import EventSystem

# 其他可选模块（安全导入）
_optional_modules = {}

try:
    from .data_manager import DataManager
    _optional_modules['DataManager'] = DataManager
except ImportError:
    pass

try:
    from .player_data_manager import PlayerDataManager
    _optional_modules['PlayerDataManager'] = PlayerDataManager
except ImportError:
    pass

try:
    from .formula_engine import FormulaEngine
    _optional_modules['FormulaEngine'] = FormulaEngine
except ImportError:
    pass

try:
    from .cultivation_system import CultivationSystem
    _optional_modules['CultivationSystem'] = CultivationSystem
except ImportError:
    pass

# 将可选模块添加到当前命名空间
for name, module in _optional_modules.items():
    globals()[name] = module

__all__ = [
    # 核心模块
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
    'EventSystem',
] + list(_optional_modules.keys())  # 动态添加可选模块