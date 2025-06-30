# xwe/core/__init__.py
"""核心模块"""

# 延迟导入以避免循环依赖
_game_core = None
_character = None
_cultivation_system = None

def __getattr__(name):
    global _game_core, _character, _cultivation_system
    
    if name == "GameCore":
        if _game_core is None:
            from src.xwe.core.game_core import GameCore as _GameCore
            _game_core = _GameCore
        return _game_core
    
    elif name == "Character":
        if _character is None:
            from src.xwe.core.character import Character as _Character
            _character = _Character
        return _character
    
    elif name == "CultivationSystem":
        if _cultivation_system is None:
            from src.xwe.core.cultivation_system import CultivationSystem as _CultivationSystem
            _cultivation_system = _CultivationSystem
        return _cultivation_system
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["GameCore", "Character", "CultivationSystem"]
