"""
世界观和背景知识路由
提供游戏世界的背景故事、历史等信息
"""

from flask import Blueprint, render_template, jsonify

bp = Blueprint('lore', __name__, url_prefix='/lore')


@bp.route('/')
def index():
    """世界观主页"""
    return render_template('lore/index.html')


@bp.route('/world')
def world_info():
    """世界设定"""
    world_data = {
        "name": "玄苍界",
        "description": "一个充满灵气的修仙世界，分为九大州，每州都有独特的修仙文化。",
        "regions": [
            {
                "name": "东玄州",
                "description": "剑修圣地，以剑道闻名天下"
            },
            {
                "name": "南离州", 
                "description": "炼丹师的天堂，盛产各种灵药"
            },
            {
                "name": "西极州",
                "description": "体修之地，崇尚炼体之道"
            },
            {
                "name": "北冥州",
                "description": "冰雪之地，冰系功法的发源地"
            }
        ]
    }
    return jsonify(world_data)


@bp.route('/history')
def history():
    """历史大事记"""
    events = [
        {
            "year": -10000,
            "event": "上古时期",
            "description": "天地初开，灵气充沛，神兽横行"
        },
        {
            "year": -5000,
            "event": "仙魔大战",
            "description": "正道与魔道的第一次大规模冲突"
        },
        {
            "year": -1000,
            "event": "封神之战",
            "description": "诸多大能飞升，留下无数传承"
        },
        {
            "year": 0,
            "event": "新纪元",
            "description": "修仙界进入相对和平的发展期"
        }
    ]
    return jsonify({"timeline": events})


@bp.route('/cultivation')
def cultivation_system():
    """修炼体系说明"""
    realms = [
        {"name": "炼气期", "levels": 9, "description": "引气入体，筑基之前"},
        {"name": "筑基期", "levels": 9, "description": "筑就道基，正式踏入修仙之路"},
        {"name": "金丹期", "levels": 9, "description": "凝结金丹，寿元大增"},
        {"name": "元婴期", "levels": 9, "description": "元婴出窍，可短暂飞行"},
        {"name": "化神期", "levels": 9, "description": "神识化形，掌控天地之力"},
        {"name": "合体期", "levels": 9, "description": "与天地合一，寿元万载"},
        {"name": "大乘期", "levels": 9, "description": "一念动山河，准备飞升"},
        {"name": "渡劫期", "levels": 9, "description": "历经天劫，超凡入圣"}
    ]
    return jsonify({"realms": realms})


@bp.route('/factions')
def factions():
    """门派介绍"""
    factions = [
        {
            "name": "青云剑宗",
            "type": "正道",
            "specialty": "剑道",
            "description": "天下第一剑宗，以一剑破万法闻名"
        },
        {
            "name": "万佛寺",
            "type": "正道",
            "specialty": "佛法",
            "description": "佛门圣地，擅长度化之术"
        },
        {
            "name": "天魔教",
            "type": "魔道",
            "specialty": "魔功",
            "description": "魔道巨擘，功法诡异强大"
        },
        {
            "name": "百花谷",
            "type": "中立",
            "specialty": "医道",
            "description": "医道圣地，救死扶伤"
        }
    ]
    return jsonify({"factions": factions})
