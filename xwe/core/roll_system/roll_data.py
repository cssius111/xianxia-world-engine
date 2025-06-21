# xwe/core/roll_system/roll_data.py
"""Roll 系统示例数据"""

ROLL_DATA = {
    "names": ["张三", "李四", "王五"],
    "genders": ["男", "女"],
    "identities": [
        {"name": "凡人", "desc": "普通的凡人"},
        {"name": "修士", "desc": "踏上修行之路的新人"},
    ],
    "spiritual_roots": [
        {"type": "普通灵根", "elements": ["金", "木"], "desc": "常见的双灵根"},
        {"type": "天灵根", "elements": ["火"], "desc": "罕见的单属性灵根"},
    ],
    "destinies": [
        {
            "name": "天生至尊",
            "rarity": "神话",
            "desc": "注定不凡",
            "effects": ["所有属性大幅提升"],
        },
        {"name": "庸才", "rarity": "普通", "desc": "平庸之辈", "effects": []},
    ],
    "talents": [
        {"name": "力量", "description": "天生力大无穷"},
        {"name": "智慧", "description": "异常聪慧"},
        {"name": "坚韧", "description": "意志坚定"},
    ],
    "systems": [
        {
            "name": "签到系统",
            "rarity": "稀有",
            "description": "每日签到获得奖励",
            "features": ["签到奖励"],
        },
        {
            "name": "任务系统",
            "rarity": "普通",
            "description": "完成任务获得经验",
            "features": ["任务发布"],
        },
    ],
}
