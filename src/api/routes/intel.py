"""
情报和信息路由
提供游戏内的各种情报、提示和帮助信息
"""

from flask import Blueprint, jsonify, request

bp = Blueprint('intel', __name__, url_prefix='/api/intel')


@bp.route('/tips')
def get_tips():
    """获取游戏提示"""
    tips = [
        {
            "id": "tip_001",
            "category": "combat",
            "content": "战斗时注意敌人的攻击模式，适时防御可以减少伤害"
        },
        {
            "id": "tip_002", 
            "category": "cultivation",
            "content": "修炼时选择灵气充足的地点可以提高效率"
        },
        {
            "id": "tip_003",
            "category": "social",
            "content": "与NPC保持良好关系可以获得特殊任务和物品"
        },
        {
            "id": "tip_004",
            "category": "exploration",
            "content": "探索时注意周围环境，隐藏的宝物往往在不起眼的地方"
        }
    ]
    
    category = request.args.get('category')
    if category:
        tips = [tip for tip in tips if tip['category'] == category]
    
    return jsonify({"tips": tips})


@bp.route('/commands')
def get_commands():
    """获取可用命令列表"""
    commands = {
        "基础命令": [
            {"command": "状态", "description": "查看角色状态", "aliases": ["status", "info"]},
            {"command": "背包", "description": "查看物品栏", "aliases": ["inventory", "bag"]},
            {"command": "地图", "description": "查看当前地图", "aliases": ["map"]},
            {"command": "帮助", "description": "显示帮助信息", "aliases": ["help", "?"]}
        ],
        "移动命令": [
            {"command": "移动 [地点]", "description": "移动到指定地点", "aliases": ["go", "move"]},
            {"command": "探索", "description": "探索当前区域", "aliases": ["explore", "search"]},
            {"command": "返回", "description": "返回上一个地点", "aliases": ["back", "return"]}
        ],
        "战斗命令": [
            {"command": "攻击 [目标]", "description": "攻击指定目标", "aliases": ["attack", "hit"]},
            {"command": "防御", "description": "进入防御姿态", "aliases": ["defend", "block"]},
            {"command": "技能 [技能名]", "description": "使用技能", "aliases": ["skill", "cast"]},
            {"command": "逃跑", "description": "尝试逃离战斗", "aliases": ["flee", "run"]}
        ],
        "社交命令": [
            {"command": "对话 [NPC]", "description": "与NPC对话", "aliases": ["talk", "speak"]},
            {"command": "交易", "description": "打开交易界面", "aliases": ["trade", "shop"]},
            {"command": "赠送 [物品] [NPC]", "description": "赠送物品给NPC", "aliases": ["give"]}
        ],
        "修炼命令": [
            {"command": "修炼", "description": "进行修炼", "aliases": ["cultivate", "meditate"]},
            {"command": "突破", "description": "尝试突破境界", "aliases": ["breakthrough"]},
            {"command": "炼化 [物品]", "description": "炼化物品", "aliases": ["refine"]}
        ]
    }
    
    return jsonify(commands)


@bp.route('/npcs')
def get_npc_info():
    """获取NPC信息"""
    location = request.args.get('location', 'qingyun_city')
    
    npcs = {
        "qingyun_city": [
            {
                "name": "王老板",
                "title": "杂货店老板",
                "description": "经营着城里最大的杂货店",
                "services": ["trade", "info"]
            },
            {
                "name": "李太虚",
                "title": "青云剑宗长老",
                "description": "负责在城中招收弟子",
                "services": ["quest", "teach"]
            },
            {
                "name": "云梦儿",
                "title": "百花谷弟子",
                "description": "在城中采购药材",
                "services": ["trade", "heal"]
            }
        ]
    }
    
    return jsonify({
        "location": location,
        "npcs": npcs.get(location, [])
    })


@bp.route('/items')
def get_item_info():
    """获取物品信息"""
    item_id = request.args.get('id')
    
    items = {
        "healing_pill": {
            "name": "回血丹",
            "type": "consumable",
            "rarity": "common",
            "description": "基础的疗伤丹药，可恢复少量生命值",
            "effect": "恢复50点生命值"
        },
        "spirit_stone": {
            "name": "灵石",
            "type": "currency",
            "rarity": "common", 
            "description": "修仙界的通用货币，蕴含灵气",
            "effect": "可用于交易或修炼"
        },
        "iron_sword": {
            "name": "精铁剑",
            "type": "weapon",
            "rarity": "common",
            "description": "用精铁打造的长剑，适合初学者使用",
            "effect": "攻击力+10"
        }
    }
    
    if item_id:
        item = items.get(item_id)
        if item:
            return jsonify(item)
        else:
            return jsonify({"error": "物品不存在"}), 404
    
    return jsonify({"items": list(items.keys())})


@bp.route('/quests')
def get_quest_info():
    """获取任务信息"""
    status = request.args.get('status', 'available')
    
    quests = {
        "available": [
            {
                "id": "quest_001",
                "name": "初入江湖",
                "description": "完成新手指引，熟悉基本操作",
                "rewards": ["经验值x100", "灵石x10"]
            },
            {
                "id": "quest_002",
                "name": "妖兽作乱",
                "description": "城外有妖兽出没，需要清理",
                "rewards": ["经验值x200", "精铁剑x1"]
            }
        ],
        "active": [],
        "completed": []
    }
    
    return jsonify({
        "status": status,
        "quests": quests.get(status, [])
    })
