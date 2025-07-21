"""
角色系统API路由
处理角色创建、属性修改等操作
"""

from flask import Blueprint, current_app, jsonify, request, session
from src.app import inventory_system
from src.common.request_utils import is_dev_request
import logging

from src.xwe.core.attributes import CharacterAttributes
from src.xwe.core.character import Character, CharacterType
from src.xwe.features.random_player_panel import RandomPlayerPanel

bp = Blueprint("character", __name__)

logger = logging.getLogger(__name__)

# 背景加成配置
BACKGROUND_BONUSES = {
    "poor": {
        "name": "寒门子弟",
        "bonuses": {"max_health": 10, "defense": 2},
        "gold_multiplier": 0.5,
        "description": "出身贫寒，但意志坚定",
    },
    "merchant": {
        "name": "商贾之家",
        "bonuses": {"luck": 1},
        "gold_multiplier": 3.0,
        "description": "家境富裕，见多识广",
    },
    "scholar": {
        "name": "书香门第",
        "bonuses": {"comprehension": 1, "max_mana": 10},
        "gold_multiplier": 1.0,
        "description": "饱读诗书，天资聪颖",
    },
    "martial": {
        "name": "武林世家",
        "bonuses": {"attack_power": 5, "max_health": 20},
        "gold_multiplier": 1.0,
        "initial_skills": ["basic_sword"],
        "description": "习武世家，身手不凡",
    },
}


@bp.post("/api/character/create")
def create_character():
    """旧版创建角色接口（已废弃）"""
    return (
        jsonify({"success": False, "error": "该接口已废弃，请使用 /create_character"}),
        410,
    )


@bp.get("/api/character/info")
def get_character_info():
    """获取当前角色信息"""
    try:
        if "session_id" not in session:
            return jsonify({"success": False, "error": "会话已过期"}), 401

        # Access game instance through current_app to avoid circular import
        if hasattr(current_app, 'game_instances'):
            session_id = session["session_id"]
            if session_id in current_app.game_instances:
                instance = current_app.game_instances[session_id]
            else:
                return jsonify({"success": False, "error": "游戏实例不存在"}), 404
        else:
            return jsonify({"success": False, "error": "游戏系统未初始化"}), 500
        game = instance["game"]

        player = game.game_state.player
        if not player:
            return jsonify({"success": False, "error": "角色不存在"}), 404

        # 构建角色信息
        character_info = {
            "name": player.name,
            "attributes": {
                "realm_name": player.attributes.realm_name,
                "realm_level": player.attributes.realm_level,
                "level": player.attributes.level,
                "cultivation_level": player.attributes.cultivation_level,
                "max_cultivation": player.attributes.max_cultivation,
                "current_health": player.attributes.current_health,
                "max_health": player.attributes.max_health,
                "current_mana": player.attributes.current_mana,
                "max_mana": player.attributes.max_mana,
                "current_stamina": player.attributes.current_stamina,
                "max_stamina": player.attributes.max_stamina,
                "attack_power": player.attributes.attack_power,
                "defense": player.attributes.defense,
            },
            "extra_data": getattr(player, "extra_data", {}),
            "location": game.game_state.current_location,
        }

        # 添加背包信息
        if hasattr(player, "inventory"):
            inv_data = inventory_system.get_inventory_data(session.get("player_id", player.id))
            character_info["inventory"] = {
                "gold": inv_data.get("gold", 0),
                "items": inv_data.get("items", []),
            }

        return jsonify({"success": True, "character": character_info})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
