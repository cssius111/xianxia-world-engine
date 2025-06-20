# 服务层配置
# 这个文件定义了服务层的配置选项

# 日志配置
LOG_SERVICE_CONFIG = {
    "max_logs": 10000,
    "log_file_rotation": True,
    "log_to_file": True,
    "log_directory": "logs",
}

# 事件配置
EVENT_DISPATCHER_CONFIG = {
    "max_event_history": 10000,
    "enable_async_events": True,
    "event_timeout": 5.0,
}

# 命令引擎配置
COMMAND_ENGINE_CONFIG = {
    "enable_natural_language": True,
    "command_cache_size": 100,
    "command_history_size": 100,
}

# 服务生命周期配置
SERVICE_LIFETIME_CONFIG = {
    "game_service": "singleton",
    "player_service": "singleton",
    "combat_service": "singleton",
    "command_engine": "singleton",
    "event_dispatcher": "singleton",
    "log_service": "singleton",
}
