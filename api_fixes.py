from flask import Blueprint, jsonify, request

sidebar_api_bp = Blueprint('sidebar_api', __name__, url_prefix='/api')


@sidebar_api_bp.get('/cultivation/status')
def cultivation_status():
    """返回示例修炼状态数据"""
    data = {
        "current_technique": "青云诀",
        "technique_level": "入门",
        "progress": 25,
        "techniques": [
            {"name": "青云诀", "level": "黄阶下品", "color": "#4CAF50"},
            {"name": "烈火诀", "level": "黄阶中品", "color": "#666"},
            {"name": "寒冰诀", "level": "黄阶中品", "color": "#666"},
        ],
        "max_hours": 8,
        "warning": "注意：当前体力只能支撑8小时修炼",
    }
    return jsonify({"success": True, "data": data})


@sidebar_api_bp.post('/cultivation/start')
def cultivation_start():
    """开始修炼，返回示例结果"""
    hours = request.get_json(silent=True) or {}
    hours = int(hours.get('hours', 1))
    result = f"你专心修炼了 {hours} 小时，感到灵力有所提升。"
    return jsonify({"success": True, "result": result})


@sidebar_api_bp.get('/achievements')
def achievements():
    """返回示例成就数据"""
    achievements_data = [
        {
            "name": "初入仙门",
            "description": "踏上修仙之路",
            "unlocked": True,
            "unlock_time": "2025-06-30 10:00",
            "reward": "铜钱x100",
        },
        {
            "name": "筑基成功",
            "description": "突破至筑基期",
            "unlocked": False,
            "unlock_time": None,
            "reward": "丹药x1",
        },
    ]
    return jsonify({"success": True, "unlocked": 1, "total": len(achievements_data), "achievements": achievements_data})


@sidebar_api_bp.get('/map')
def map_data():
    """返回示例地图数据"""
    data = {
        "regions": [
            {
                "name": "青云山脉",
                "description": "云雾缭绕的仙山",
                "locations": [
                    {"name": "青云城", "description": "繁华的修真城市", "discovered": True, "accessible": True},
                    {"name": "青云峰", "description": "青云宗山门", "discovered": True, "accessible": True},
                    {"name": "灵兽森林", "description": "危机四伏的森林", "discovered": False, "accessible": False},
                ],
            }
        ]
    }
    return jsonify({"success": True, "data": data})


@sidebar_api_bp.get('/quests')
def quests():
    """返回示例任务数据"""
    quests_data = [
        {
            "name": "初入青云",
            "description": "前往青云城了解情况",
            "status": "active",
            "progress": 1,
            "max_progress": 3,
            "objectives": [
                {"text": "与城主对话", "completed": True},
                {"text": "寻找灵草", "completed": False},
            ],
        },
        {
            "name": "寻找机缘",
            "description": "探索周围区域，寻找修炼资源",
            "status": "available",
            "progress": 0,
            "max_progress": 1,
            "objectives": [],
        },
    ]
    return jsonify({
        "success": True,
        "quests": quests_data,
        "active_count": 1,
        "available_count": 1,
    })


@sidebar_api_bp.get('/intel')
def intel():
    """返回示例情报数据"""
    intel_data = {
        "global": [
            {
                "title": "秘境开启",
                "content": "传闻附近将开启古老秘境。",
                "source": "坊市传闻",
                "time": "辰时",
                "importance": "high",
                "interactable_task_id": None,
            }
        ],
        "personal": [
            {
                "title": "师门任务",
                "content": "师傅让你采集灵草。",
                "source": "师门",
                "time": "早上",
                "importance": "medium",
                "interactable_task_id": "quest_001",
            }
        ],
    }
    return jsonify({"success": True, "data": intel_data})


@sidebar_api_bp.get('/player/stats/detailed')
def player_stats_detailed():
    """返回示例详细玩家状态"""
    data = {
        "basic_info": {"name": "无名侠客", "realm": "炼气期", "realm_level": 1},
        "cultivation": {"cultivation_level": 0, "max_cultivation": 100},
        "attributes": {"constitution": 5, "comprehension": 5, "spirit": 5, "luck": 5},
        "resources": {"gold": 100},
        "combat_stats": {"current_health": 100, "max_health": 100},
        "social": {"faction": "散修", "reputation": 0},
    }
    return jsonify({"success": True, "data": data})


def register_sidebar_apis(app):
    """注册侧边栏相关API"""
    app.register_blueprint(sidebar_api_bp)
    return sidebar_api_bp
