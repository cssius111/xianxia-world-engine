"""Player-related API routes."""

from flask import Blueprint, jsonify

player_bp = Blueprint('player', __name__, url_prefix='/api/player')


@player_bp.get('/stats/detailed')
def get_player_stats_detailed():
    """Get detailed player statistics."""
    data = {
        "basic_info": {
            "id": "player_001",
            "name": "无名侠客",
            "realm": "炼气期",
            "realm_level": 1,
            "title": "初入江湖",
            "age": 18
        },
        "cultivation": {
            "cultivation_level": 0,
            "max_cultivation": 100,
            "cultivation_speed": 1.0,
            "breakthrough_chance": 0.1
        },
        "attributes": {
            "constitution": 5,
            "comprehension": 5,
            "spirit": 5,
            "luck": 5,
            "charm": 5
        },
        "resources": {
            "gold": 100,
            "spirit_stones": 10,
            "contribution_points": 0
        },
        "combat_stats": {
            "current_health": 100,
            "max_health": 100,
            "current_qi": 50,
            "max_qi": 50,
            "attack": 10,
            "defense": 8,
            "speed": 12,
            "critical_rate": 0.05
        },
        "social": {
            "faction": "散修",
            "reputation": 0,
            "relationships": []
        },
        "skills": {
            "combat_skills": [],
            "life_skills": [],
            "special_skills": []
        }
    }
    return jsonify({"success": True, "data": data})


@player_bp.get('/inventory')
def get_inventory():
    """Get player inventory."""
    inventory = {
        "capacity": 50,
        "used": 5,
        "items": [
            {
                "id": "item_001",
                "name": "回血丹",
                "type": "consumable",
                "quantity": 3,
                "description": "恢复50点生命值"
            },
            {
                "id": "item_002",
                "name": "精铁剑",
                "type": "weapon",
                "quantity": 1,
                "description": "攻击力+5",
                "equipped": True
            }
        ]
    }
    return jsonify({"success": True, "inventory": inventory})


@player_bp.get('/stats/summary')
def get_player_stats_summary():
    """Get brief player statistics summary."""
    return jsonify({
        "success": True,
        "summary": {
            "name": "无名侠客",
            "realm": "炼气期",
            "level": 1,
            "health_percent": 100,
            "qi_percent": 100,
            "location": "青云城"
        }
    })
