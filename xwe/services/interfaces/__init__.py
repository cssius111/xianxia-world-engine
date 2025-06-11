"""
服务接口汇总
提供所有服务接口的统一导入点
"""

# 核心服务接口
from .game_service import IGameService, GameState, CommandResult
from .player_service import IPlayerService, PlayerData, PlayerStatus
from .save_service import ISaveService, SaveInfo, SaveData, SaveType
from .world_service import IWorldService, Location, LocationType, Weather, TimeOfDay, WorldEvent, ExplorationResult
from .combat_service import ICombatService, CombatState, Combatant, CombatAction, CombatResult, CombatType, ActionType, DamageType
from .cultivation_service import ICultivationService, CultivationRealm, CultivationType, SpiritualRoot, CultivationTechnique, CultivationResult, BreakthroughInfo, Tribulation

# 已在主services目录的接口
from ..command_engine import ICommandEngine, CommandContext, CommandResult as CmdResult, ICommandHandler
from ..event_dispatcher import IEventDispatcher, EventStatistics
from ..log_service import ILogService, LogEntry, LogFilter, LogLevel

# 导出所有接口
__all__ = [
    # Game Service
    'IGameService',
    'GameState',
    'CommandResult',
    
    # Player Service
    'IPlayerService',
    'PlayerData',
    'PlayerStatus',
    
    # Save Service
    'ISaveService',
    'SaveInfo',
    'SaveData',
    'SaveType',
    
    # World Service
    'IWorldService',
    'Location',
    'LocationType',
    'Weather',
    'TimeOfDay',
    'WorldEvent',
    'ExplorationResult',
    
    # Combat Service
    'ICombatService',
    'CombatState',
    'Combatant',
    'CombatAction',
    'CombatResult',
    'CombatType',
    'ActionType',
    'DamageType',
    
    # Cultivation Service
    'ICultivationService',
    'CultivationRealm',
    'CultivationType',
    'SpiritualRoot',
    'CultivationTechnique',
    'CultivationResult',
    'BreakthroughInfo',
    'Tribulation',
    
    # Command Engine
    'ICommandEngine',
    'CommandContext',
    'CmdResult',
    'ICommandHandler',
    
    # Event Dispatcher
    'IEventDispatcher',
    'EventStatistics',
    
    # Log Service
    'ILogService',
    'LogEntry',
    'LogFilter',
    'LogLevel',
]


# 服务接口类型映射
SERVICE_INTERFACES = {
    'game': IGameService,
    'player': IPlayerService,
    'save': ISaveService,
    'world': IWorldService,
    'combat': ICombatService,
    'cultivation': ICultivationService,
    'command': ICommandEngine,
    'event': IEventDispatcher,
    'log': ILogService,
}


def get_service_interface(service_name: str):
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
