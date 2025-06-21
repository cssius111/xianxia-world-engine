# 这是xwe.core包的__init__.py文件
"""
XWE核心游戏系统模块
"""

from typing import Any, Dict

from xwe.core.ai import AIController
from xwe.core.attributes import AttributeSystem, CharacterAttributes
from xwe.core.character import Character
from xwe.core.combat import CombatSystem, combat_system
from xwe.core.command_parser import CommandParser
from xwe.core.data_loader import DataLoader
from xwe.core.event_system import EventSystemV3 as EventSystem
from xwe.core.game_core import GameCore
from xwe.core.skills import Skill, SkillSystem
from xwe.core.status import StatusEffect, StatusEffectManager

# 其他可选模块（安全导入）
_optional_modules: Dict[str, Any] = {}

try:
    from xwe.core.data_manager import DataManager, get_config, load_game_data

    _optional_modules["DataManager"] = DataManager
    _optional_modules["load_game_data"] = load_game_data
    _optional_modules["get_config"] = get_config
except ImportError:
    pass

try:
    from xwe.core.player_data_manager import PlayerDataManager

    _optional_modules["PlayerDataManager"] = PlayerDataManager
except ImportError:
    pass

try:
    from xwe.core.formula_engine import FormulaEngine, calculate, evaluate_expression

    _optional_modules["FormulaEngine"] = FormulaEngine
    _optional_modules["calculate"] = calculate
    _optional_modules["evaluate_expression"] = evaluate_expression
except ImportError:
    pass

try:
    from xwe.core.cultivation_system import CultivationSystem

    _optional_modules["CultivationSystem"] = CultivationSystem
except ImportError:
    pass

from xwe.core.game_core import create_enhanced_game

_optional_modules["create_enhanced_game"] = create_enhanced_game

# 将可选模块添加到当前命名空间
for name, module in _optional_modules.items():
    globals()[name] = module

__all__ = [
    # 核心模块
    "DataLoader",
    "AttributeSystem",
    "CharacterAttributes",
    "Character",
    "SkillSystem",
    "Skill",
    "CombatSystem",
    "AIController",
    "StatusEffect",
    "StatusEffectManager",
    "CommandParser",
    "GameCore",
    "EventSystem",
    "load_game_data",
    "get_config",
    "calculate",
    "evaluate_expression",
    "combat_system",
] + list(
    _optional_modules.keys()
)  # 动态添加可选模块
