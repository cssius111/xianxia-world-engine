"""
基础命令处理器集合
"""

from .combat_handler import (
    AttackHandler,
    CombatCommandHandler,
    CombatHandler,
    DefendHandler,
    FleeHandler,
    UseSkillHandler,
)
from .cultivation_handler import (
    BreakthroughHandler,
    CultivateHandler,
    CultivationCommandHandler,
    CultivationHandler,
    LearnSkillHandler,
    UseItemHandler,
)
from .info_handler import (
    InfoHandler,
    InventoryHandler,
    MapHandler,
    SkillsHandler,
    StatusHandler,
)
from .interaction_handler import (
    InteractionCommandHandler,
    InteractionHandler,
    PickUpHandler,
    TalkHandler,
    TradeHandler,
)
from .movement_handler import ExploreHandler, MovementHandler
from .system_handler import (
    HelpHandler,
    LoadHandler,
    QuitHandler,
    SaveHandler,
    SystemCommandHandler,
    SystemHandler,
)

__all__ = [
    # 战斗处理器
    "CombatHandler",
    "AttackHandler",
    "DefendHandler",
    "FleeHandler",
    "UseSkillHandler",
    "CombatCommandHandler",
    # 移动处理器
    "MovementHandler",
    "ExploreHandler",
    # 交互处理器
    "InteractionHandler",
    "TalkHandler",
    "TradeHandler",
    "PickUpHandler",
    "InteractionCommandHandler",
    # 系统处理器
    "SystemHandler",
    "SaveHandler",
    "LoadHandler",
    "HelpHandler",
    "QuitHandler",
    "SystemCommandHandler",
    # 信息处理器
    "InfoHandler",
    "StatusHandler",
    "InventoryHandler",
    "SkillsHandler",
    "MapHandler",
    # 修炼处理器
    "CultivationHandler",
    "CultivateHandler",
    "LearnSkillHandler",
    "BreakthroughHandler",
    "UseItemHandler",
    "CultivationCommandHandler",
]
