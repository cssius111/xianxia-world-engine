from __future__ import annotations

import json
import time
from flask import Blueprint, Response, stream_with_context, session, jsonify, request, current_app

from src.app import build_status_data, status_cache


events_bp = Blueprint("events", __name__)


def _generate_events():
    session_id = session.get("session_id", "default")
    last_data = status_cache.get(session_id)
    while True:
        data = build_status_data()
        subset = {
            "player": data.get("player", {}),
            "inventory": data.get("inventory", {}),
        }
        if subset != last_data:
            last_data = subset
            status_cache[session_id] = subset
            yield f"data: {json.dumps(subset, ensure_ascii=False)}\n\n"
        time.sleep(1)


@events_bp.route("/events")
def events_stream():
    return Response(stream_with_context(_generate_events()), mimetype="text/event-stream")


@events_bp.get("/api/events/random")
def random_event():
    """返回随机事件"""
    style = request.args.get("style", "")

    session_id = session.get("session_id", "default")
    try:
        if hasattr(current_app, "game_instances") and session_id in current_app.game_instances:
            game = current_app.game_instances[session_id]["game"]
            ns = getattr(game, "narrative_system", None)
            if ns:
                event = ns.generate_story_event({"style": style})
                return jsonify(event)
    except Exception as e:  # pragma: no cover - fallback
        current_app.logger.error(f"random_event error: {e}")

    from src.xwe.features.narrative_system import narrative_system
    event = narrative_system.generate_story_event({"style": style})
    return jsonify(event)


__all__ = ["events_bp"]
