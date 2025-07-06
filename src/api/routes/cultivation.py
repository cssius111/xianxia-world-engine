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
    """Start cultivation session with basic checks."""
    data = request.get_json(silent=True) or {}
    hours = int(data.get("hours", 1))

    # Validate hours
    if hours < 1:
        return jsonify({"success": False, "error": "修炼时间至少为1小时"}), 400
    if hours > 8:
        return jsonify({"success": False, "error": "当前体力最多支撑8小时修炼"}), 400

    session_id = session.get("session_id")
    player = None
    game = None
    if hasattr(current_app, "game_instances") and session_id in current_app.game_instances:
        game = current_app.game_instances[session_id]["game"]
        player = getattr(game.game_state, "player", None)

    if player and game:
        required_mana = hours * 5
        if player.attributes.current_mana < required_mana:
            return (
                jsonify({"success": False, "confirm": "灵气不足，是否继续修炼？"}),
                400,
            )

        if player.attributes.comprehension < 5:
            return (
                jsonify({"success": False, "confirm": "悟性不足，继续修炼收益甚微，确认继续？"}),
                400,
            )

        if player.attributes.realm_progress >= 100:
            return (
                jsonify({"success": False, "confirm": "已到瓶颈，请突破后再修炼"}),
                400,
            )

        player.attributes.current_mana -= required_mana
        if hasattr(game, "time_system"):
            try:
                game.time_system.advance_time(
                    "cultivate_basic", game.game_state, {"hours": hours}
                )
            except Exception as e:  # pragma: no cover - safety
                logger.error(f"advance_time error: {e}")

        # 环境加成
        location_bonus = 1.0
        area = None
        try:
            area = game.world_map.get_area(game.game_state.current_location)
            if area:
                location_bonus += getattr(area, "danger_level", 0) * 0.05
        except Exception as e:  # pragma: no cover - optional world map
            logger.error(f"location bonus error: {e}")

        exp_gained = 0
        if hasattr(game, "cultivation_system"):
            exp_gained = game.cultivation_system.calculate_cultivation_exp(
                player, hours, location_bonus
            )
            player.attributes.cultivation_exp += exp_gained
            req = game.cultivation_system.realm_breakthroughs.get(
                player.attributes.realm_name, {}
            )
            need = req.get("exp_required", 100)
            player.attributes.realm_progress = min(
                100.0, player.attributes.cultivation_exp / need * 100
            )

        event = None
        try:
            ns = getattr(game, "narrative_system", None)
            if ns:
                event = ns.generate_story_event(
                    {
                        "action": "cultivation",
                        "location": getattr(area, "name", ""),
                        "hours": hours,
                    }
                )
        except Exception as e:  # pragma: no cover - fallback
            logger.error(f"generate_story_event error: {e}")

        result = f"你专心修炼了 {hours} 小时，获得 {exp_gained} 修为。"
        return jsonify(
            {
                "success": True,
                "result": result,
                "exp_gained": exp_gained,
                "event": event,
            }
        )

    # Fallback simple text when no game instance
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
