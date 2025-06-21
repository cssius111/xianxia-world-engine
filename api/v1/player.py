"""
玩家相关API
处理玩家角色的创建、查询和更新
"""

from flask import Blueprint, jsonify, request, session
import time
from xwe.core.character import Character, CharacterType
from xwe.core.attributes import CharacterAttributes

player_bp = Blueprint('player', __name__)


@player_bp.route('/info', methods=['GET'])
def get_player_info():
    """获取玩家信息"""
    if 'session_id' not in session:
        return jsonify({"error": "会话已过期"}), 401

    from entrypoints import run_web_ui_optimized

    instance = run_web_ui_optimized.get_game_instance(session['session_id'])
    game = instance["game"]
    player = game.game_state.player

    if not player:
        return jsonify({"error": "未找到玩家"}), 404

    return jsonify(player.to_dict())


@player_bp.route('/create', methods=['POST'])
def create_player():
    """创建新玩家"""
    data = request.get_json()
    name = data.get('name', '无名侠客')
    character_type = data.get('type', 'balanced')

    if 'session_id' not in session:
        session['session_id'] = str(time.time())

    from entrypoints import run_web_ui_optimized

    instance = run_web_ui_optimized.get_game_instance(session['session_id'])
    game = instance["game"]

    attrs = CharacterAttributes()
    player = Character(id="player", name=name, character_type=CharacterType.PLAYER, attributes=attrs)

    if character_type == 'sword':
        player.attributes.attack_power += 5
    elif character_type == 'body':
        player.attributes.defense += 5
    elif character_type == 'magic':
        player.attributes.max_mana += 20

    game.game_state.player = player
    instance["need_refresh"] = True

    return jsonify({"success": True, "player": player.to_dict()})


@player_bp.route('/inventory', methods=['GET'])
def get_inventory():
    """获取玩家背包"""
    if 'session_id' not in session:
        return jsonify({"items": [], "capacity": 0, "used": 0})

    from entrypoints import run_web_ui_optimized

    instance = run_web_ui_optimized.get_game_instance(session['session_id'])
    game = instance["game"]
    player = game.game_state.player

    if not player:
        return jsonify({"items": [], "capacity": 0, "used": 0})

    inventory = player.inventory.to_dict()
    inventory["used"] = len(player.inventory.items)
    return jsonify(inventory)


@player_bp.route('/skills', methods=['GET'])
def get_skills():
    """获取玩家技能"""
    if 'session_id' not in session:
        return jsonify({"skills": []})

    from entrypoints import run_web_ui_optimized

    instance = run_web_ui_optimized.get_game_instance(session['session_id'])
    game = instance["game"]
    player = game.game_state.player

    skills = []
    if player:
        for skill_id in getattr(player, 'skills', []):
            skills.append({"id": skill_id})

    return jsonify({"skills": skills})


@player_bp.route('/cultivate', methods=['POST'])
def cultivate():
    """修炼"""
    data = request.get_json()
    duration = data.get('duration', 1)
    if 'session_id' not in session:
        return jsonify({"success": False, "error": "会话已过期"}), 401

    from entrypoints import run_web_ui_optimized

    instance = run_web_ui_optimized.get_game_instance(session['session_id'])
    game = instance["game"]
    player = game.game_state.player

    if not player:
        return jsonify({"success": False, "error": "未找到玩家"}), 404

    exp_gained = 0
    if hasattr(game, 'cultivation_system'):
        exp_gained = game.cultivation_system.calculate_cultivation_exp(player, duration)
        player.attributes.cultivation_exp += exp_gained

    instance["need_refresh"] = True

    return jsonify({
        "success": True,
        "exp_gained": exp_gained,
        "message": f"修炼了{duration}个时辰"
    })
