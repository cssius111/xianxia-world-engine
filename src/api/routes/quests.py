"""Quest system API routes."""

from flask import Blueprint, jsonify, request

quests_bp = Blueprint('quests', __name__, url_prefix='/api')


@quests_bp.get('/quests')
def get_quests():
    """Get all quests."""
    quests_data = [
        {
            "id": "quest_001",
            "name": "初入青云",
            "description": "前往青云城了解情况",
            "status": "active",
            "progress": 1,
            "max_progress": 3,
            "type": "main",
            "objectives": [
                {"id": "obj_001", "text": "与城主对话", "completed": True},
                {"id": "obj_002", "text": "寻找灵草", "completed": False},
                {"id": "obj_003", "text": "回报城主", "completed": False}
            ],
            "rewards": {
                "exp": 100,
                "gold": 50,
                "items": ["灵石x3"]
            }
        },
        {
            "id": "quest_002",
            "name": "寻找机缘",
            "description": "探索周围区域，寻找修炼资源",
            "status": "available",
            "progress": 0,
            "max_progress": 1,
            "type": "side",
            "objectives": [],
            "rewards": {
                "exp": 50,
                "gold": 20
            }
        },
        {
            "id": "quest_003",
            "name": "师门任务",
            "description": "完成师傅交代的任务",
            "status": "completed",
            "progress": 5,
            "max_progress": 5,
            "type": "daily",
            "objectives": [
                {"id": "obj_004", "text": "修炼5小时", "completed": True}
            ],
            "rewards": {
                "exp": 30,
                "contribution": 10
            }
        }
    ]
    
    active_count = sum(1 for q in quests_data if q["status"] == "active")
    available_count = sum(1 for q in quests_data if q["status"] == "available")
    completed_count = sum(1 for q in quests_data if q["status"] == "completed")
    
    return jsonify({
        "success": True,
        "quests": quests_data,
        "active_count": active_count,
        "available_count": available_count,
        "completed_count": completed_count
    })


@quests_bp.post('/quests/<quest_id>/accept')
def accept_quest(quest_id: str):
    """Accept an available quest."""
    # TODO: Implement quest acceptance logic
    return jsonify({
        "success": True,
        "message": f"已接受任务: {quest_id}",
        "quest_id": quest_id
    })


@quests_bp.post('/quests/<quest_id>/complete')
def complete_quest(quest_id: str):
    """Complete a quest and claim rewards."""
    # TODO: Implement quest completion logic
    return jsonify({
        "success": True,
        "message": f"任务完成: {quest_id}",
        "rewards": {
            "exp": 100,
            "gold": 50,
            "items": ["灵石x3"]
        }
    })
