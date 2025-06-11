"""
游戏相关API
处理游戏核心功能：命令执行、状态查询、日志获取等
"""

from flask import Blueprint, request, session
from typing import Dict, Any, List

from xwe.services import get_service_container, IGameService, ILogService
from xwe.services.log_service import LogFilter
from ..utils import api_response, validate_request
from ..errors import InvalidCommandError, PlayerDeadError, GameNotInitializedError


# 创建蓝图
game_bp = Blueprint('game', __name__)


@game_bp.route('/status', methods=['GET'])
@api_response
def get_game_status():
    """
    获取游戏状态
    
    Returns:
        {
            "initialized": true,
            "player": {...},
            "location": "...",
            "in_combat": false,
            "game_time": 12345
        }
    """
    # 获取游戏服务
    container = get_service_container()
    game_service = container.resolve(IGameService)
    
    # 获取游戏状态
    game_state = game_service.get_game_state()
    
    if not game_state.initialized:
        return {
            'initialized': False,
            'message': '游戏尚未初始化'
        }
    
    # 获取玩家服务
    from xwe.services import IPlayerService
    player_service = container.resolve(IPlayerService)
    player = player_service.get_current_player()
    
    status_data = {
        'initialized': True,
        'in_combat': game_state.in_combat,
        'location': game_state.current_location,
        'game_time': game_service.get_game_time()
    }
    
    if player:
        status_data['player'] = {
            'id': player.id,
            'name': player.name,
            'level': player.level,
            'realm': player.realm,
            'health': {
                'current': player.health,
                'max': player.max_health
            },
            'mana': {
                'current': player.mana,
                'max': player.max_mana
            },
            'experience': {
                'current': player.experience,
                'required': player.experience_to_next
            },
            'attributes': {
                'attack': player.attack,
                'defense': player.defense,
                'speed': player.speed
            }
        }
    
    return status_data


@game_bp.route('/command', methods=['POST'])
@api_response
@validate_request({
    'type': 'object',
    'properties': {
        'command': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 200
        }
    },
    'required': ['command']
})
def execute_command():
    """
    执行游戏命令
    
    Request:
        {
            "command": "攻击 敌人"
        }
        
    Returns:
        {
            "command": "攻击 敌人",
            "result": "你对敌人发起了攻击...",
            "state_changed": true,
            "events": [...],
            "suggestions": [...]
        }
    """
    # 获取命令
    command = request.json['command'].strip()
    
    # 获取服务
    container = get_service_container()
    game_service = container.resolve(IGameService)
    
    # 检查游戏状态
    game_state = game_service.get_game_state()
    if not game_state.initialized:
        raise GameNotInitializedError()
    
    # 检查玩家状态
    from xwe.services import IPlayerService
    player_service = container.resolve(IPlayerService)
    player = player_service.get_current_player()
    
    if player and player.health <= 0:
        raise PlayerDeadError()
    
    # 执行命令
    try:
        # 使用命令引擎处理命令
        from xwe.services import ICommandEngine
        command_engine = container.resolve(ICommandEngine)
        
        result = command_engine.process_command(
            command,
            player_id=player.id if player else None,
            location=game_state.current_location,
            in_combat=game_state.in_combat
        )
        
        # 构建响应
        response_data = {
            'command': command,
            'result': result.output,
            'state_changed': result.state_changed,
            'events': result.events
        }
        
        # 如果有建议的命令
        if result.suggestions:
            response_data['suggestions'] = result.suggestions
            
        # 如果需要确认
        if result.require_confirmation:
            response_data['require_confirmation'] = True
            response_data['confirmation_data'] = result.confirmation_data
            
        return response_data
        
    except Exception as e:
        # 记录错误
        log_service = container.resolve(ILogService)
        log_service.log_error(f"Command execution error: {e}", 
                             category='command_error',
                             metadata={'command': command})
        
        # 获取命令建议
        from xwe.services import ICommandEngine
        command_engine = container.resolve(ICommandEngine)
        suggestions = command_engine.get_suggestions(command.split()[0] if command else '')
        
        raise InvalidCommandError(
            command=command,
            suggestions=suggestions or ['帮助', '状态', '地图']
        )


@game_bp.route('/log', methods=['GET'])
@api_response
def get_game_log():
    """
    获取游戏日志
    
    Query Parameters:
        - limit: 返回的日志条数（默认50，最大200）
        - offset: 偏移量（默认0）
        - level: 日志级别过滤（可选）
        - category: 日志类别过滤（可选）
        
    Returns:
        {
            "logs": [
                {
                    "id": 1,
                    "timestamp": 12345,
                    "level": "info",
                    "category": "combat",
                    "message": "你对敌人造成了10点伤害"
                }
            ],
            "total": 100,
            "statistics": {...}
        }
    """
    # 获取参数
    limit = min(request.args.get('limit', 50, type=int), 200)
    offset = request.args.get('offset', 0, type=int)
    level = request.args.get('level')
    category = request.args.get('category')
    
    # 获取日志服务
    container = get_service_container()
    log_service = container.resolve(ILogService)
    
    # 创建过滤器
    filter = LogFilter()
    if level:
        filter.levels = [level]
    if category:
        filter.categories = [category]
    
    # 获取日志
    logs = log_service.get_logs(filter=filter, limit=limit, offset=offset)
    
    # 格式化日志
    formatted_logs = []
    for log in logs:
        formatted_logs.append({
            'id': log.id,
            'timestamp': log.timestamp,
            'level': log.level.value,
            'category': log.category,
            'message': log.message,
            'metadata': log.metadata
        })
    
    # 获取统计信息
    stats = log_service.get_log_statistics()
    
    return {
        'logs': formatted_logs,
        'total': stats['total_logs'],
        'statistics': stats
    }


@game_bp.route('/events', methods=['GET'])
@api_response
def get_recent_events():
    """
    获取最近的游戏事件
    
    Query Parameters:
        - limit: 返回的事件数量（默认20，最大100）
        - type: 事件类型过滤（可选）
        
    Returns:
        {
            "events": [
                {
                    "id": "evt_123",
                    "type": "combat_start",
                    "timestamp": 12345,
                    "data": {...}
                }
            ],
            "statistics": {...}
        }
    """
    # 获取参数
    limit = min(request.args.get('limit', 20, type=int), 100)
    event_type = request.args.get('type')
    
    # 获取事件分发器
    container = get_service_container()
    from xwe.services import IEventDispatcher
    event_dispatcher = container.resolve(IEventDispatcher)
    
    # 获取事件历史
    events = event_dispatcher.get_event_history(
        event_type=event_type,
        limit=limit
    )
    
    # 格式化事件
    formatted_events = []
    for event in events:
        formatted_events.append({
            'type': event.type,
            'timestamp': event.timestamp,
            'data': event.data,
            'source': event.source,
            'correlation_id': event.correlation_id
        })
    
    # 获取统计信息
    stats = event_dispatcher.get_statistics()
    
    return {
        'events': formatted_events,
        'statistics': {
            'total_events': stats.total_events,
            'events_by_type': stats.events_by_type,
            'events_per_minute': stats.events_per_minute,
            'average_processing_time': stats.average_processing_time
        }
    }


@game_bp.route('/initialize', methods=['POST'])
@api_response
@validate_request({
    'type': 'object',
    'properties': {
        'player_name': {
            'type': 'string',
            'minLength': 2,
            'maxLength': 20
        }
    }
})
def initialize_game():
    """
    初始化新游戏
    
    Request:
        {
            "player_name": "玩家名称"  // 可选
        }
    
    Returns:
        {
            "success": true,
            "message": "游戏初始化成功",
            "player_created": true,
            "player_id": "xxx"
        }
    """
    # 获取参数
    player_name = request.json.get('player_name')
    
    # 获取游戏服务
    container = get_service_container()
    game_service = container.resolve(IGameService)
    
    # 初始化游戏
    success = game_service.initialize_game(player_name=player_name)
    
    if not success:
        return {
            'success': False,
            'message': '游戏初始化失败'
        }
    
    response = {
        'success': True,
        'message': '游戏初始化成功',
        'player_created': bool(player_name)
    }
    
    # 如果创建了玩家，返回玩家ID
    if player_name:
        from xwe.services import IPlayerService
        player_service = container.resolve(IPlayerService)
        player = player_service.get_current_player()
        if player:
            response['player_id'] = player.id
    
    return response


@game_bp.route('/help', methods=['GET'])
@api_response
def get_help():
    """
    获取游戏帮助
    
    Query Parameters:
        - command: 获取特定命令的帮助（可选）
        
    Returns:
        {
            "help": "帮助内容...",
            "commands": ["命令1", "命令2", ...],
            "categories": {...}
        }
    """
    command = request.args.get('command')
    
    # 获取命令引擎
    container = get_service_container()
    from xwe.services import ICommandEngine
    command_engine = container.resolve(ICommandEngine)
    
    if command:
        # 获取特定命令的帮助
        # 这里可以调用命令引擎的帮助方法
        help_result = command_engine.process_command(f"帮助 {command}")
        return {
            'help': help_result.output,
            'command': command
        }
    else:
        # 获取所有命令
        all_commands = command_engine.get_all_commands()
        
        # 分类整理
        categories = {
            '基础命令': ['帮助', '状态', '地图', '探索'],
            '战斗命令': ['攻击', '防御', '逃跑', '使用'],
            '修炼命令': ['修炼', '突破'],
            '交互命令': ['对话', '交易'],
            '系统命令': ['保存', '退出']
        }
        
        # 过滤出实际存在的命令
        for category, commands in categories.items():
            categories[category] = [cmd for cmd in commands if cmd in all_commands]
        
        return {
            'help': '使用"帮助 [命令]"查看特定命令的详细说明',
            'commands': all_commands,
            'categories': categories
        }
