from typing import Any

"""
服务接口汇总
提供所有服务接口的统一导入点
"""

# 已在主services目录的接口
from src.xwe.services.command_engine import CommandContext
from src.xwe.services.command_engine import CommandResult as CmdResult
from src.xwe.services.command_engine import ICommandEngine, ICommandHandler
from src.xwe.services.event_dispatcher import EventStatistics, IEventDispatcher

# 核心服务接口
from src.xwe.services.game_service import CommandResult, GameState, IGameService
from src.xwe.services.interfaces.combat_service import ICombatService
from src.xwe.services.interfaces.cultivation_service import (
    BreakthroughInfo,
    CultivationRealm,
    CultivationResult,
    CultivationTechnique,
    CultivationType,
    ICultivationService,
    SpiritualRoot,
    Tribulation,
)
from src.xwe.services.interfaces.player_service import IPlayerService, PlayerData
from src.xwe.services.interfaces.save_service import SaveData, SaveInfo, SaveType
from src.xwe.services.interfaces.world_service import IWorldService
from src.xwe.services.log_service import ILogService, LogEntry, LogFilter, LogLevel
from src.xwe.services.save_service import ISaveService

# 导出所有接口
__all__ = [
    # Game Service
    "IGameService",
    "GameState",
    "CommandResult",
    # Player Service
    "IPlayerService",
    "PlayerData",
    # Save Service
    "ISaveService",
    "SaveInfo",
    "SaveData",
    "SaveType",
    # World Service
    "IWorldService",
    # Combat Service
    "ICombatService",
    # Cultivation Service
    "ICultivationService",
    "CultivationRealm",
    "CultivationType",
    "SpiritualRoot",
    "CultivationTechnique",
    "CultivationResult",
    "BreakthroughInfo",
    "Tribulation",
    # Command Engine
    "ICommandEngine",
    "CommandContext",
    "CmdResult",
    "ICommandHandler",
    # Event Dispatcher
    "IEventDispatcher",
    "EventStatistics",
    # Log Service
    "ILogService",
    "LogEntry",
    "LogFilter",
    "LogLevel",
]


# 服务接口类型映射
SERVICE_INTERFACES = {
    "game": IGameService,
    "player": IPlayerService,
    "save": ISaveService,
    "world": IWorldService,
    "combat": ICombatService,
    "cultivation": ICultivationService,
    "command": ICommandEngine,
    "event": IEventDispatcher,
    "log": ILogService,
}


def get_service_interface(service_name: str) -> Any:
    """
    根据服务名称获取接口类型

    Args:
        service_name: 服务名称

    Returns:
        服务接口类型

    Example:
        >>> interface = get_service_interface('player')
        >>> print(interface)
        <class 'IPlayerService'>
    """
    return SERVICE_INTERFACES.get(service_name.lower())
