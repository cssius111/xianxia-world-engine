"""Player related routes."""

from __future__ import annotations

import json
import time
from flask import Blueprint, jsonify, request, session, Response, stream_with_context

from src.common.request_utils import is_dev_request

from .. import (
    build_status_data,
    command_router,
    get_game_instance,
    inventory_system,
    logger,
    status_cache,
)

player_bp = Blueprint("player_ui", __name__)


@player_bp.route("/create_character", methods=["POST"])
def create_character():
    dev_mode = is_dev_request()
    data = request.get_json()

    if data and "name" in data:
        player_name = data.get("name", "无名侠客")
        session["player_name"] = player_name
        session["player_id"] = f"player_{player_name}"
        session["location"] = "青云城"

        inventory_system.create_initial_inventory(session["player_id"])

        logger.info(f"创建角色: {player_name}")

        if not session.get("player_created"):
            session["player_created"] = True

        if "destiny" in data:
            session["destiny"] = data["destiny"]

        if "session_id" not in session:
            session["session_id"] = str(time.time())
        instance = get_game_instance(session["session_id"], initialize_player=False)
        game = instance["game"]

        from src.xwe.core.attributes import CharacterAttributes
        from src.xwe.core.character import Character, CharacterType

        attrs_data = data.get("attributes")
        attrs = None
        if attrs_data:
            attrs = CharacterAttributes.from_dict(attrs_data)
            for key in [
                "strength",
                "constitution",
                "agility",
                "intelligence",
                "willpower",
                "comprehension",
                "luck",
            ]:
                val = getattr(attrs, key, 0)
                setattr(attrs, key, max(1, min(10, int(val))))
            attrs.calculate_derived_attributes()

        if attrs is None:
            attrs = CharacterAttributes()

        player = Character(
            id=session.get("player_id", "player"),
            name=player_name,
            character_type=CharacterType.PLAYER,
            attributes=attrs,
        )
        game.game_state.player = player
        game.game_state.current_location = session.get("location", "青云城")
        game.game_state.logs = []
        logger.info(f"[PLAYER] attributes set: {attrs.to_dict()}")

    if dev_mode:
        session["dev"] = True

    return jsonify({"success": True, "narrative": f"{data.get('name', '无名侠客')} 的修仙之旅由此开始。"})


@player_bp.route("/status")
def get_status():
    status_dict = build_status_data()
    logger.debug("[STATUS] %s", status_dict)
    return jsonify(status_dict)


@player_bp.route("/status/stream")
def stream_status():
    @stream_with_context
    def event_stream():
        session_id = session.get("session_id", "default")
        last_data = status_cache.get(session_id)
        while True:
            data = build_status_data()
            if data != last_data:
                last_data = data
                status_cache[session_id] = data
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            time.sleep(2)

    return Response(event_stream(), mimetype="text/event-stream")


@player_bp.route("/log")
def get_log():
    return jsonify({"logs": ["欢迎来到修仙世界！", "你出生在青云城，开始了修仙之旅。", "输入'帮助'查看可用命令。"]})


@player_bp.route("/nlp_cache_info")
def get_nlp_cache_info():
    cache_info = command_router.get_nlp_cache_info()
    if cache_info:
        return jsonify({"success": True, "cache_info": cache_info})
    else:
        return jsonify({"success": False, "message": "NLP未启用或不支持缓存"})


@player_bp.route("/clear_nlp_cache", methods=["POST"])
def clear_nlp_cache():
    command_router.clear_nlp_cache()
    return jsonify({"success": True, "message": "NLP缓存已清除"})
