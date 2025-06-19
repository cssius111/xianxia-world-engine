"""
玩家相关API
处理玩家信息查询、技能、背包等功能
"""

from flask import Blueprint, session
from typing import Dict, Any, List

from ..utils import api_response, validate_request
from ..errors import NotFoundError, InvalidRequestError


# 创建蓝图
player_bp = Blueprint('player', __name__)


@player_bp.route('/info', methods=['GET'])
@api_response
def get_player_info():
    """
    获取玩家详细信息
    
    Returns:
        {
            "id": "player_123",
            "name": "张三",
            "level": 10,
            "realm": "筑基期",
            "attributes": {...},
            "stats": {...}
        }
    """
    game = session.get('game')
    
    if not game or not game.player:
        raise NotFoundError('玩家', 'current')
    
    player = game.player
    
    return {
        'id': player.id,
        'name': player.name,
        'level': player.level,
        'realm': player.realm,
        'attributes': {
            'health': player.health,
            'max_health': player.max_health,
            'mana': player.mana,
            'max_mana': player.max_mana,
            'attack': player.attack,
            'defense': player.defense,
            'speed': player.speed
        },
        'stats': {
            'experience': player.experience,
            'experience_to_next': player.experience_to_next,
            'spiritual_root': player.spiritual_root,
            'talent': player.talent,
            'fate': player.fate
        }
    }


@player_bp.route('/skills', methods=['GET'])
@api_response
def get_player_skills():
    """
    获取玩家技能列表
    
    Returns:
        {
            "skills": [
                {
                    "id": "skill_001",
                    "name": "基础剑法",
                    "level": 1,
                    "type": "attack",
                    "description": "...",
                    "cooldown": 0
                }
            ],
            "skill_points": 5
        }
    """
    game = session.get('game')
    
    if not game or not game.player:
        raise NotFoundError('玩家', 'current')
    
    player = game.player
    
    # 格式化技能数据
    skills_data = []
    for skill_id, skill in player.skills.items():
        skills_data.append({
            'id': skill_id,
            'name': skill.name,
            'level': skill.level,
            'type': skill.type,
            'description': skill.description,
            'cooldown': skill.current_cooldown,
            'max_cooldown': skill.cooldown,
            'mana_cost': skill.mana_cost
        })
    
    return {
        'skills': skills_data,
        'skill_points': getattr(player, 'skill_points', 0)
    }


@player_bp.route('/inventory', methods=['GET'])
@api_response
def get_player_inventory():
    """
    获取玩家背包物品
    
    Returns:
        {
            "items": [
                {
                    "id": "item_001",
                    "name": "回复丹",
                    "type": "consumable",
                    "quantity": 5,
                    "description": "..."
                }
            ],
            "capacity": {
                "used": 10,
                "total": 50
            }
        }
    """
    game = session.get('game')
    
    if not game or not game.player:
        raise NotFoundError('玩家', 'current')
    
    # 如果还没有实现背包系统，返回空数据
    if not hasattr(game.player, 'inventory'):
        return {
            'items': [],
            'capacity': {
                'used': 0,
                'total': 50
            }
        }
    
    # 格式化背包数据
    items_data = []
    for item_id, item_info in game.player.inventory.items():
        items_data.append({
            'id': item_id,
            'name': item_info.get('name', '未知物品'),
            'type': item_info.get('type', 'misc'),
            'quantity': item_info.get('quantity', 1),
            'description': item_info.get('description', '')
        })
    
    return {
        'items': items_data,
        'capacity': {
            'used': len(items_data),
            'total': getattr(game.player, 'inventory_capacity', 50)
        }
    }


@player_bp.route('/achievements', methods=['GET'])
@api_response
def get_player_achievements():
    """
    获取玩家成就列表
    
    Returns:
        {
            "achievements": [
                {
                    "id": "ach_001",
                    "name": "初出茅庐",
                    "description": "完成第一场战斗",
                    "unlocked": true,
                    "unlock_time": 12345,
                    "progress": {
                        "current": 1,
                        "total": 1
                    }
                }
            ],
            "total_points": 100
        }
    """
    game = session.get('game')
    
    if not game or not game.player:
        raise NotFoundError('玩家', 'current')
    
    # 如果还没有实现成就系统，返回空数据
    if not hasattr(game.player, 'achievements'):
        return {
            'achievements': [],
            'total_points': 0
        }
    
    # 格式化成就数据
    achievements_data = []
    total_points = 0
    
    for ach_id, ach_info in game.player.achievements.items():
        achievements_data.append({
            'id': ach_id,
            'name': ach_info.get('name', '未知成就'),
            'description': ach_info.get('description', ''),
            'unlocked': ach_info.get('unlocked', False),
            'unlock_time': ach_info.get('unlock_time', None),
            'progress': ach_info.get('progress', {'current': 0, 'total': 1}),
            'points': ach_info.get('points', 0)
        })
        
        if ach_info.get('unlocked', False):
            total_points += ach_info.get('points', 0)
    
    return {
        'achievements': achievements_data,
        'total_points': total_points
    }


@player_bp.route('/stats/combat', methods=['GET'])
@api_response
def get_combat_stats():
    """
    获取玩家战斗统计
    
    Returns:
        {
            "total_battles": 100,
            "victories": 80,
            "defeats": 20,
            "total_damage_dealt": 10000,
            "total_damage_taken": 5000,
            "kills": {
                "total": 80,
                "by_type": {...}
            }
        }
    """
    game = session.get('game')
    
    if not game or not game.player:
        raise NotFoundError('玩家', 'current')
    
    # 如果还没有统计系统，返回默认数据
    stats = getattr(game.player, 'combat_stats', {})
    
    return {
        'total_battles': stats.get('total_battles', 0),
        'victories': stats.get('victories', 0),
        'defeats': stats.get('defeats', 0),
        'total_damage_dealt': stats.get('total_damage_dealt', 0),
        'total_damage_taken': stats.get('total_damage_taken', 0),
        'kills': stats.get('kills', {'total': 0, 'by_type': {}})
    }
