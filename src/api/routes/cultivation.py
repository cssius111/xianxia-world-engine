"""Cultivation-related API routes."""

from flask import Blueprint, jsonify, request, session, current_app
import logging

logger = logging.getLogger(__name__)
cultivation_bp = Blueprint('cultivation', __name__, url_prefix='/api/cultivation')


@cultivation_bp.get('/status')
def get_cultivation_status():
    """
    Returns the player's realm, progress %, and pending tribulation info.
    ---
    responses:
      200:
        description: Success
        content:
          application/json:
            schema:
              type: object
              properties:
                realm:
                  type: string
                  description: Current cultivation realm
                progress:
                  type: number
                  description: Progress percentage in current realm
                next_tribulation:
                  type: object
                  nullable: true
                  description: Information about pending tribulation
    """
    try:
        # Try to get from game state if available
        if hasattr(current_app, 'game_instances') and 'session_id' in session:
            session_id = session.get('session_id')
            if session_id in current_app.game_instances:
                game = current_app.game_instances[session_id]['game']
                player = game.game_state.player
                
                data = {
                    "realm": getattr(player.attributes, 'realm_name', '炼气期'),
                    "progress": getattr(player.attributes, 'realm_progress', 0),
                    "next_tribulation": getattr(player, 'next_tribulation', None)
                }
                return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error getting cultivation status from game state: {e}")
    
    # Fallback to session data or defaults
    data = {
        "realm": session.get('realm', '炼气期'),
        "progress": session.get('realm_progress', 0),
        "next_tribulation": None,
        # Additional data for backward compatibility
        "current_technique": "青云诀",
        "technique_level": "入门",
        "techniques": [
            {"name": "青云诀", "level": "黄阶下品", "color": "#4CAF50"},
            {"name": "烈火诀", "level": "黄阶中品", "color": "#666"},
            {"name": "寒冰诀", "level": "黄阶中品", "color": "#666"},
        ],
        "max_hours": 8,
        "warning": "注意：当前体力只能支撑8小时修炼",
    }
    return jsonify(data), 200


@cultivation_bp.post('/start')
def start_cultivation():
    """Start cultivation session."""
    data = request.get_json(silent=True) or {}
    hours = int(data.get('hours', 1))
    
    # Validate hours
    if hours < 1:
        return jsonify({"success": False, "error": "修炼时间至少为1小时"}), 400
    if hours > 8:
        return jsonify({"success": False, "error": "当前体力最多支撑8小时修炼"}), 400
    
    result = f"你专心修炼了 {hours} 小时，感到灵力有所提升。"
    return jsonify({"success": True, "result": result})


@cultivation_bp.post('/stop')
def stop_cultivation():
    """Stop current cultivation session."""
    # TODO: Implement actual cultivation stop logic
    return jsonify({
        "success": True,
        "result": "你停止了修炼，感到神清气爽。"
    })
