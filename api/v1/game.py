"""
游戏核心API
处理游戏主要功能的接口
"""

import time

from flask import Blueprint, current_app, jsonify, request, session

game_bp = Blueprint("game", __name__)


@game_bp.route("/status", methods=["GET"])
def get_game_status():
    """获取游戏状态"""
    if "session_id" not in session:
        return jsonify(
            {
                "status": "idle",
                "version": current_app.config.get("VERSION", "1.0.0"),
                "players_online": 0,
            }
        )

    from run import game_instances, get_game_instance

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    return jsonify(
        {
            "status": "running",
            "version": current_app.config.get("VERSION", "1.0.0"),
            "players_online": len(game_instances),
            "location": getattr(game.game_state, "current_location", None),
        }
    )


@game_bp.route("/command", methods=["POST"])
def process_command():
    """处理游戏命令"""
    data = request.get_json()
    command = data.get("command", "")

    if "session_id" not in session:
        return jsonify({"success": False, "error": "会话已过期"}), 401

    from run import get_game_instance

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    game.process_command(command)
    instance["need_refresh"] = True
    instance["last_update"] = time.time()

    return jsonify({"success": True, "message": f"命令 '{command}' 已处理"})


@game_bp.route("/locations", methods=["GET"])
def get_locations():
    """获取所有可用位置"""
    if "session_id" not in session:
        return jsonify({"locations": []})

    from run import get_game_instance

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    locations = []
    world_map = getattr(game, "world_map", None)
    if world_map and hasattr(world_map, "areas"):
        for area_id, area in world_map.areas.items():
            locations.append(
                {
                    "id": area_id,
                    "name": getattr(area, "name", area_id),
                    "type": getattr(area, "type", "unknown"),
                }
            )

    return jsonify({"locations": locations})


@game_bp.route("/time", methods=["GET"])
def get_game_time():
    """获取游戏时间"""
    if "session_id" not in session:
        return jsonify({"game_time": 0, "day": 0, "time_of_day": "unknown"})

    from run import get_game_instance

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    game_time = getattr(game.game_state, "game_time", 0.0)
    day = int(game_time // 24) + 1
    hour = int(game_time % 24)

    if hour < 6:
        tod = "night"
    elif hour < 12:
        tod = "morning"
    elif hour < 18:
        tod = "afternoon"
    else:
        tod = "evening"

    return jsonify({"game_time": game_time, "day": day, "time_of_day": tod})
