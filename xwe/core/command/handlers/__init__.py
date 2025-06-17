"""
基础命令处理器集合
"""

from .combat_handler import CombatHandler, AttackHandler, DefendHandler, FleeHandler, UseSkillHandler
from .movement_handler import MovementHandler, ExploreHandler
from .interaction_handler import InteractionHandler, TalkHandler, TradeHandler
from .system_handler import SystemHandler, SaveHandler, LoadHandler, HelpHandler
from .info_handler import InfoHandler, StatusHandler, InventoryHandler, SkillsHandler, MapHandler

__all__ = [
    # 战斗处理器
    'CombatHandler',
    'AttackHandler',
    'DefendHandler',
    'FleeHandler',
    'UseSkillHandler',
    
    # 移动处理器
    'MovementHandler',
    'ExploreHandler',
    
    # 交互处理器
    'InteractionHandler',
    'TalkHandler',
    'TradeHandler',
    
    # 系统处理器
    'SystemHandler',
    'SaveHandler',
    'LoadHandler',
    'HelpHandler',
    
    # 信息处理器
    'InfoHandler',
    'StatusHandler',
    'InventoryHandler',
    'SkillsHandler',
    'MapHandler',
]
