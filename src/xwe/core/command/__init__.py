"""
命令处理模块

提供统一的命令处理框架，支持自然语言解析、命令路由和执行。
"""

from .command_processor import (
    CommandProcessor,
    CommandHandler,
    CommandContext,
    CommandResult,
    CommandPriority,
    Middleware,
    LoggingMiddleware,
    ValidationMiddleware,
    CooldownMiddleware,
    RateLimitMiddleware
)

from .handlers import (
    # 战斗处理器
    CombatCommandHandler,
    AttackHandler,
    DefendHandler,
    FleeHandler,
    UseSkillHandler,
    
    # 移动处理器
    MovementHandler,
    ExploreHandler,
    
    # 交互处理器
    InteractionCommandHandler,
    TalkHandler,
    TradeHandler,
    PickUpHandler,
    
    # 系统处理器
    SystemCommandHandler,
    SaveHandler,
    LoadHandler,
    HelpHandler,
    QuitHandler,
    
    # 信息处理器
    InfoHandler,
    StatusHandler,
    InventoryHandler,
    SkillsHandler,
    MapHandler,
    
    # 修炼处理器
    CultivationCommandHandler,
    CultivateHandler,
    LearnSkillHandler,
    BreakthroughHandler,
    UseItemHandler,
)

__all__ = [
    # 核心类
    'CommandProcessor',
    'CommandHandler',
    'CommandContext',
    'CommandResult',
    'CommandPriority',
    'Middleware',
    
    # 中间件
    'LoggingMiddleware',
    'ValidationMiddleware',
    'CooldownMiddleware',
    'RateLimitMiddleware',
    
    # 组合处理器
    'CombatCommandHandler',
    'InteractionCommandHandler',
    'SystemCommandHandler',
    'CultivationCommandHandler',
    
    # 具体处理器
    'AttackHandler',
    'DefendHandler',
    'FleeHandler',
    'UseSkillHandler',
    'MovementHandler',
    'ExploreHandler',
    'TalkHandler',
    'TradeHandler',
    'PickUpHandler',
    'SaveHandler',
    'LoadHandler',
    'HelpHandler',
    'QuitHandler',
    'InfoHandler',
    'StatusHandler',
    'InventoryHandler',
    'SkillsHandler',
    'MapHandler',
    'CultivateHandler',
    'LearnSkillHandler',
    'BreakthroughHandler',
    'UseItemHandler',
]
