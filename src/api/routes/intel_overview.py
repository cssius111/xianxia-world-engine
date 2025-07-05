"""Intel overview API route."""

from flask import Blueprint, jsonify

intel_bp = Blueprint('intel_overview', __name__, url_prefix='/api')


@intel_bp.get('/intel')
def get_intel_overview():
    """Get intel overview data."""
    data = {
        "recent_events": [
            "青云城最近妖兽活动频繁",
            "血月商会正在收购灵草",
            "有修士在灵兽森林发现了古迹"
        ],
        "rumors": [
            "据说青云峰后山有秘境即将开启",
            "城主府正在招募护卫"
        ],
        "tips": [
            "修炼时选择灵气充足的地点可以提高效率",
            "与NPC保持良好关系可以获得特殊任务"
        ],
        "discoveries": {
            "locations": 3,
            "npcs": 5,
            "items": 12
        }
    }
    
    return jsonify({"success": True, "data": data})
