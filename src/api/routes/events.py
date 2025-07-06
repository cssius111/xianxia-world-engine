from __future__ import annotations

import json
import time
from flask import Blueprint, Response, stream_with_context, session

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


__all__ = ["events_bp"]
