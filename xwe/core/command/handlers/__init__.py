"""
基础命令处理器集合
"""

from .combat_handler import (
    CombatHandler, AttackHandler, DefendHandler, FleeHandler, 
    UseSkillHandler, CombatCommandHandler
)
from .movement_handler import MovementHandler, ExploreHandler
from .interaction_handler import (
    InteractionHandler, TalkHandler, TradeHandler, PickUpHandler,
    InteractionCommandHandler
)
from .system_handler import (
    SystemHandler, SaveHandler, LoadHandler, HelpHandler, QuitHandler,
    SystemCommandHandler
)
from .info_handler import (
    InfoHandler, StatusHandler, InventoryHandler, SkillsHandler, MapHandler
)
from .cultivation_handler import (
    CultivationHandler, CultivateHandler, LearnSkillHandler, 
    BreakthroughHandler, UseItemHandler, CultivationCommandHandler
)

__all__ = [
    # 战斗处理器
    'CombatHandler',
    'AttackHandler',
    'DefendHandler',
    'FleeHandler',
    'UseSkillHandler',
    'CombatCommandHandler',
    
    # 移动处理器
    'MovementHandler',
    'ExploreHandler',
    
    # 交互处理器
    'InteractionHandler',
    'TalkHandler',
    'TradeHandler',
    'PickUpHandler',
    'InteractionCommandHandler',
    
    # 系统处理器
    'SystemHandler',
    'SaveHandler',
    'LoadHandler',
    'HelpHandler',
    'QuitHandler',
    'SystemCommandHandler',
    
    # 信息处理器
    'InfoHandler',
    'StatusHandler',
    'InventoryHandler',
    'SkillsHandler',
    'MapHandler',
    
    # 修炼处理器
    'CultivationHandler',
    'CultivateHandler',
    'LearnSkillHandler',
    'BreakthroughHandler',
    'UseItemHandler',
    'CultivationCommandHandler',
]
