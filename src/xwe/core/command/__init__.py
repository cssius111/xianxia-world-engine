"""
命令处理模块

提供统一的命令处理框架，支持自然语言解析、命令路由和执行。
"""

from .command_processor import (
    CommandContext,
    CommandHandler,
    CommandPriority,
    CommandProcessor,
    CommandResult,
    CooldownMiddleware,
    LoggingMiddleware,
    Middleware,
    RateLimitMiddleware,
    ValidationMiddleware,
)
from .handlers import (  # 战斗处理器; 移动处理器; 交互处理器; 系统处理器; 信息处理器; 修炼处理器
    AttackHandler,
    BreakthroughHandler,
    CombatCommandHandler,
    CultivateHandler,
    CultivationCommandHandler,
    DefendHandler,
    ExploreHandler,
    FleeHandler,
    HelpHandler,
    InfoHandler,
    InteractionCommandHandler,
    InventoryHandler,
    LearnSkillHandler,
    LoadHandler,
    MapHandler,
    MovementHandler,
    PickUpHandler,
    QuitHandler,
    SaveHandler,
    SkillsHandler,
    StatusHandler,
    SystemCommandHandler,
    TalkHandler,
    TradeHandler,
    UseItemHandler,
    UseSkillHandler,
)

__all__ = [
    # 核心类
    "CommandProcessor",
    "CommandHandler",
    "CommandContext",
    "CommandResult",
    "CommandPriority",
    "Middleware",
    # 中间件
    "LoggingMiddleware",
    "ValidationMiddleware",
    "CooldownMiddleware",
    "RateLimitMiddleware",
    # 组合处理器
    "CombatCommandHandler",
    "InteractionCommandHandler",
    "SystemCommandHandler",
    "CultivationCommandHandler",
    # 具体处理器
    "AttackHandler",
    "DefendHandler",
    "FleeHandler",
    "UseSkillHandler",
    "MovementHandler",
    "ExploreHandler",
    "TalkHandler",
    "TradeHandler",
    "PickUpHandler",
    "SaveHandler",
    "LoadHandler",
    "HelpHandler",
    "QuitHandler",
    "InfoHandler",
    "StatusHandler",
    "InventoryHandler",
    "SkillsHandler",
    "MapHandler",
    "CultivateHandler",
    "LearnSkillHandler",
    "BreakthroughHandler",
    "UseItemHandler",
]
