"""
系统相关API
提供系统信息、命令列表、版本信息等
"""

from flask import Blueprint, session
from typing import Dict, Any, List
import time
import psutil
import os

from ..utils import api_response
from xwe.metrics import metrics_registry


# 创建蓝图
system_bp = Blueprint('system', __name__)


@system_bp.route('/info', methods=['GET'])
@api_response
def get_system_info():
    """
    获取系统信息
    
    Returns:
        {
            "version": "1.0.0",
            "name": "修仙世界引擎",
            "uptime": 3600,
            "server_time": 12345,
            "environment": "production"
        }
    """
    # 计算运行时间
    uptime = int(time.time() - getattr(system_bp, '_start_time', time.time()))
    
    return {
        'version': '1.0.0',
        'name': '修仙世界引擎',
        'uptime': uptime,
        'server_time': int(time.time()),
        'environment': os.environ.get('FLASK_ENV', 'production')
    }


@system_bp.route('/commands', methods=['GET'])
@api_response
def get_available_commands():
    """
    获取可用命令列表
    
    Returns:
        {
            "commands": [
                {
                    "name": "攻击",
                    "aliases": ["a", "attack"],
                    "description": "对目标发起攻击",
                    "usage": "攻击 [目标]",
                    "category": "combat"
                }
            ],
            "categories": ["基础", "战斗", "探索", "交互"]
        }
    """
    commands = [
        {
            'name': '帮助',
            'aliases': ['help', 'h', '?'],
            'description': '显示帮助信息',
            'usage': '帮助',
            'category': '基础'
        },
        {
            'name': '状态',
            'aliases': ['status', 's'],
            'description': '查看角色状态',
            'usage': '状态',
            'category': '基础'
        },
        {
            'name': '攻击',
            'aliases': ['attack', 'a'],
            'description': '对目标发起攻击',
            'usage': '攻击 [目标]',
            'category': '战斗'
        },
        {
            'name': '防御',
            'aliases': ['defend', 'd'],
            'description': '进入防御姿态',
            'usage': '防御',
            'category': '战斗'
        },
        {
            'name': '逃跑',
            'aliases': ['flee', 'run'],
            'description': '尝试逃离战斗',
            'usage': '逃跑',
            'category': '战斗'
        },
        {
            'name': '使用',
            'aliases': ['use', 'u'],
            'description': '使用技能或物品',
            'usage': '使用 [技能/物品] [目标]',
            'category': '战斗'
        },
        {
            'name': '探索',
            'aliases': ['explore', 'e'],
            'description': '探索当前区域',
            'usage': '探索',
            'category': '探索'
        },
        {
            'name': '移动',
            'aliases': ['move', 'go'],
            'description': '移动到其他区域',
            'usage': '移动 [方向/地点]',
            'category': '探索'
        },
        {
            'name': '地图',
            'aliases': ['map', 'm'],
            'description': '查看地图',
            'usage': '地图',
            'category': '探索'
        },
        {
            'name': '修炼',
            'aliases': ['cultivate', 'train'],
            'description': '进行修炼',
            'usage': '修炼',
            'category': '修炼'
        },
        {
            'name': '突破',
            'aliases': ['breakthrough'],
            'description': '尝试突破境界',
            'usage': '突破',
            'category': '修炼'
        },
        {
            'name': '对话',
            'aliases': ['talk', 'chat'],
            'description': '与NPC对话',
            'usage': '对话 [NPC名称]',
            'category': '交互'
        },
        {
            'name': '交易',
            'aliases': ['trade', 'shop'],
            'description': '进行交易',
            'usage': '交易 [NPC名称]',
            'category': '交互'
        },
        {
            'name': '保存',
            'aliases': ['save'],
            'description': '保存游戏进度',
            'usage': '保存',
            'category': '系统'
        },
        {
            'name': '加载',
            'aliases': ['load'],
            'description': '加载游戏进度',
            'usage': '加载',
            'category': '系统'
        },
        {
            'name': '退出',
            'aliases': ['quit', 'exit'],
            'description': '退出游戏',
            'usage': '退出',
            'category': '系统'
        }
    ]
    
    # 获取所有类别
    categories = list(set(cmd['category'] for cmd in commands))
    
    return {
        'commands': commands,
        'categories': categories
    }


@system_bp.route('/stats', methods=['GET'])
@api_response
def get_system_stats():
    """
    获取系统统计信息
    
    Returns:
        {
            "memory": {
                "used": 1024,
                "total": 8192,
                "percent": 12.5
            },
            "cpu": {
                "percent": 25.0,
                "count": 4
            },
            "sessions": {
                "active": 10,
                "total": 100
            }
        }
    """
    # 获取内存信息
    memory = psutil.virtual_memory()
    
    # 获取CPU信息
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count()
    
    return {
        'memory': {
            'used': memory.used // (1024 * 1024),  # MB
            'total': memory.total // (1024 * 1024),  # MB
            'percent': memory.percent
        },
        'cpu': {
            'percent': cpu_percent,
            'count': cpu_count
        },
        'sessions': {
            'active': 1,  # 当前简化实现
            'total': 1
        }
    }


@system_bp.route('/health', methods=['GET'])
@api_response
def health_check():
    """
    健康检查接口
    
    Returns:
        {
            "status": "healthy",
            "checks": {
                "database": "ok",
                "cache": "ok",
                "storage": "ok",
                "services": "ok"
            },
            "details": {...}
        }
    """
    from xwe.services import ServiceContainer
    checks = {}
    details = {}
    
    # 检查存档目录
    try:
        saves_dir = 'saves'
        if os.path.exists(saves_dir) and os.access(saves_dir, os.W_OK):
            checks['storage'] = 'ok'
            details['storage'] = {
                'path': saves_dir,
                'writable': True
            }
        else:
            checks['storage'] = 'error'
            details['storage'] = {
                'path': saves_dir,
                'error': 'Directory not writable'
            }
    except Exception as e:
        checks['storage'] = 'error'
        details['storage'] = {'error': str(e)}
    
    # 检查会话
    try:
        if session:
            checks['session'] = 'ok'
        else:
            checks['session'] = 'warning'
    except:
        checks['session'] = 'error'
    
    # 检查服务容器
    try:
        container = ServiceContainer.get_instance()
        if container:
            service_count = len(container._services)
            initialized_count = sum(1 for s in container._services.values() if s.get('instance'))
            
            if initialized_count > 0:
                checks['services'] = 'ok'
                details['services'] = {
                    'registered': service_count,
                    'initialized': initialized_count
                }
            else:
                checks['services'] = 'warning'
                details['services'] = {
                    'registered': service_count,
                    'initialized': 0,
                    'warning': 'No services initialized'
                }
        else:
            checks['services'] = 'error'
            details['services'] = {'error': 'ServiceContainer not available'}
    except Exception as e:
        checks['services'] = 'error'
        details['services'] = {'error': str(e)}
    
    # 检查内存使用
    try:
        memory = psutil.virtual_memory()
        if memory.percent < 90:
            checks['memory'] = 'ok'
        else:
            checks['memory'] = 'warning'
        details['memory'] = {
            'used_mb': memory.used // (1024 * 1024),
            'total_mb': memory.total // (1024 * 1024),
            'percent': memory.percent
        }
    except:
        checks['memory'] = 'unknown'
    
    # 简化的数据库和缓存检查
    checks['database'] = 'ok'  # 当前使用文件系统
    checks['cache'] = 'ok'     # 当前使用内存
    
    # 判断整体状态
    error_count = sum(1 for status in checks.values() if status == 'error')
    warning_count = sum(1 for status in checks.values() if status == 'warning')
    
    if error_count > 0:
        overall_status = 'unhealthy'
    elif warning_count > 0:
        overall_status = 'degraded'
    else:
        overall_status = 'healthy'
    
    return {
        'status': overall_status,
        'checks': checks,
        'details': details,
        'timestamp': int(time.time())
    }


@system_bp.route('/time', methods=['GET'])
@api_response
def get_game_time():
    """
    获取游戏时间信息
    
    Returns:
        {
            "real_time": 12345,
            "game_time": 67890,
            "game_date": {
                "year": 1,
                "month": 3,
                "day": 15,
                "hour": 14,
                "season": "春"
            }
        }
    """
    game = session.get('game')
    
    # 游戏时间（如果有的话）
    game_time = 0
    game_date = {
        'year': 1,
        'month': 1,
        'day': 1,
        'hour': 0,
        'season': '春'
    }
    
    if game and hasattr(game, 'game_time'):
        game_time = game.game_time
        
        # 计算游戏日期（假设1游戏日 = 3600秒）
        days = game_time // 3600
        hours = (game_time % 3600) // 150  # 1小时 = 150秒
        
        # 计算年月日
        year = days // 360 + 1
        day_of_year = days % 360
        month = day_of_year // 30 + 1
        day = day_of_year % 30 + 1
        
        # 计算季节
        season_map = {
            1: '春', 2: '春', 3: '春',
            4: '夏', 5: '夏', 6: '夏',
            7: '秋', 8: '秋', 9: '秋',
            10: '冬', 11: '冬', 12: '冬'
        }
        season = season_map.get(month, '春')
        
        game_date = {
            'year': year,
            'month': month,
            'day': day,
            'hour': hours,
            'season': season
        }
    
    return {
        'real_time': int(time.time()),
        'game_time': game_time,
        'game_date': game_date
    }


@system_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    获取Prometheus格式的系统指标
    
    Returns:
        Prometheus text format metrics
    """
    # 更新一些系统指标
    memory = psutil.virtual_memory()
    metrics_registry.set_gauge('memory_usage_bytes', memory.used)
    metrics_registry.set_gauge('cpu_usage_percent', psutil.cpu_percent(interval=0.1))
    
    # 获取在线玩家数（简化实现）
    active_players = len([s for s in dir(session) if not s.startswith('_')])
    metrics_registry.set_gauge('active_players', active_players)
    
    # 返回Prometheus格式的指标
    from flask import Response
    return Response(
        metrics_registry.export_metrics(),
        mimetype='text/plain; version=0.0.4'
    )


# 记录启动时间
system_bp._start_time = time.time()
