"""
系统相关API
处理系统设置、版本信息等
"""

import json
import os

import psutil
from flask import Blueprint, current_app, jsonify, request, session

system_bp = Blueprint("system_v1", __name__)


@system_bp.route("/info", methods=["GET"])
def get_system_info():
    """获取系统信息"""
    return jsonify(
        {
            "version": "1.0.0",
            "name": "仙侠世界引擎",
            "environment": os.getenv("FLASK_ENV", "production"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "features": {
                "npc_system": True,
                "combat_system": True,
                "cultivation_system": True,
                "roll_system": True,
            },
        }
    )


@system_bp.route("/settings", methods=["GET"])
def get_settings():
    """获取系统设置"""
    return jsonify(
        {
            "graphics": {"text_speed": "normal", "show_animations": True},
            "audio": {"master_volume": 0.8, "music_volume": 0.7, "sfx_volume": 0.9},
            "gameplay": {
                "auto_save": True,
                "auto_save_interval": 300,
                "difficulty": "normal",
            },
        }
    )


@system_bp.route("/settings", methods=["PUT"])
def update_settings():
    """更新系统设置"""
    data = request.get_json()
    settings_file = "game_settings.json"

    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        current_app.config.update(data)
        return jsonify({"success": True, "message": "设置已更新"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/logs", methods=["GET"])
def get_logs():
    """获取系统日志"""
    limit = request.args.get("limit", 100, type=int)
    log_file = os.path.join(current_app.config.get("LOG_PATH", "logs"), "app.log")

    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
            logs = [line.strip() for line in lines]

    return jsonify({"logs": logs, "total": len(logs)})


@system_bp.route("/performance", methods=["GET"])
def get_performance():
    """获取性能统计"""
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory_usage = psutil.virtual_memory().percent

    from run import game_instances

    return jsonify(
        {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "response_time": 0,
            "active_sessions": len(game_instances),
        }
    )
