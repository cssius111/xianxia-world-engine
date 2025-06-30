"""
存档相关API
处理游戏的保存和加载功能
"""

import json
import os
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, session

from src.xwe.core.game_core import GameState

save_bp = Blueprint("save", __name__)

# 存档目录
SAVE_DIR = "saves"


@save_bp.route("/list", methods=["GET"])
def list_saves():
    """列出所有存档"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    saves = []
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SAVE_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    save_data = json.load(f)
                    saves.append(
                        {
                            "filename": filename,
                            "timestamp": save_data.get("timestamp", "unknown"),
                            "player_name": save_data.get("player_name", "未知"),
                            "level": save_data.get("level", 1),
                        }
                    )
            except:
                pass

    return jsonify({"saves": saves})


@save_bp.route("/save", methods=["POST"])
def save_game():
    """保存游戏"""
    data = request.get_json()
    save_name = data.get("name", "autosave")

    # 确保存档目录存在
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # 生成存档文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{save_name}_{timestamp}.json"
    filepath = os.path.join(SAVE_DIR, filename)

    if "session_id" not in session:
        return jsonify({"success": False, "error": "会话已过期"}), 401

    from run import get_game_instance

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    player = game.game_state.player
    save_data = {
        "version": current_app.config.get("VERSION", "1.0.0"),
        "timestamp": timestamp,
        "player_name": player.name if player else "未知",
        "level": getattr(player.attributes, "level", 1) if player else 1,
        "game_state": game.game_state.to_dict(),
    }

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True, "filename": filename, "message": "游戏已保存"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@save_bp.route("/load/<filename>", methods=["POST"])
def load_game(filename):
    """加载游戏"""
    filepath = os.path.join(SAVE_DIR, filename)

    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": "存档文件不存在"}), 404

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            save_data = json.load(f)
        if "session_id" not in session:
            return jsonify({"success": False, "error": "会话已过期"}), 401

        from run import get_game_instance

        instance = get_game_instance(session["session_id"])
        game = instance["game"]

        game.game_state = GameState.from_dict(save_data.get("game_state", {}))
        instance["need_refresh"] = True

        return jsonify({"success": True, "message": "游戏已加载", "data": save_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@save_bp.route("/delete/<filename>", methods=["DELETE"])
def delete_save(filename):
    """删除存档"""
    filepath = os.path.join(SAVE_DIR, filename)

    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": "存档文件不存在"}), 404

    try:
        os.remove(filepath)
        return jsonify({"success": True, "message": "存档已删除"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
