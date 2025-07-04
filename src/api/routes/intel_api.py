"""Intel (intelligence) API routes for sidebar panels."""

from flask import Blueprint, jsonify, request

intel_api_bp = Blueprint('intel_api', __name__, url_prefix='/api')

# Additional intel blueprint for /intel prefix routes
intel_tips_bp = Blueprint('intel_tips', __name__, url_prefix='/intel')


@intel_api_bp.get('/intel')
def get_intel_data():
    """Get intelligence/news data for the game world."""
    intel_data = {
        "global": [
            {
                "id": "intel_001",
                "title": "秘境开启",
                "content": "传闻附近将开启古老秘境。",
                "source": "坊市传闻",
                "time": "辰时",
                "importance": "high",
                "interactable_task_id": None
            },
            {
                "id": "intel_002",
                "title": "妖兽潮",
                "content": "最近妖兽活动频繁，外出需谨慎。",
                "source": "城主府公告",
                "time": "昨日",
                "importance": "medium",
                "interactable_task_id": "quest_002"
            }
        ],
        "personal": [
            {
                "id": "intel_p001",
                "title": "师门任务",
                "content": "师傅让你采集灵草。",
                "source": "师门",
                "time": "早上",
                "importance": "medium",
                "interactable_task_id": "quest_001"
            },
            {
                "id": "intel_p002",
                "title": "商会邀请",
                "content": "灵宝商会邀请你参加拍卖会。",
                "source": "灵宝商会",
                "time": "三日后",
                "importance": "low",
                "interactable_task_id": None
            }
        ],
        "rumors": [
            {
                "id": "rumor_001",
                "content": "听说东方有一处遗迹，藏有上古功法。",
                "credibility": 0.3
            }
        ]
    }
    return jsonify({"success": True, "data": intel_data})


@intel_tips_bp.get('/tips')
def get_intel_tips():
    """Get game tips (alternative endpoint for compatibility)."""
    tips = [
        {
            "id": "tip_001",
            "category": "combat",
            "content": "战斗时注意敌人的攻击模式，适时防御可以减少伤害",
            "level": "beginner"
        },
        {
            "id": "tip_002",
            "category": "cultivation",
            "content": "修炼时选择灵气充足的地点可以提高效率",
            "level": "beginner"
        },
        {
            "id": "tip_003",
            "category": "social",
            "content": "与NPC保持良好关系可以获得特殊任务和物品",
            "level": "intermediate"
        },
        {
            "id": "tip_004",
            "category": "exploration",
            "content": "探索时注意周围环境，隐藏的宝物往往在不起眼的地方",
            "level": "beginner"
        },
        {
            "id": "tip_005",
            "category": "economy",
            "content": "合理管理资源，不要在前期浪费珍贵材料",
            "level": "intermediate"
        }
    ]
    
    category = request.args.get('category')
    level = request.args.get('level')
    
    filtered_tips = tips
    if category:
        filtered_tips = [t for t in filtered_tips if t['category'] == category]
    if level:
        filtered_tips = [t for t in filtered_tips if t.get('level') == level]
    
    return jsonify({"tips": filtered_tips})
