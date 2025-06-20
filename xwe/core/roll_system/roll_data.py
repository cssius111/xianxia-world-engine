"""
Roll 系统数据配置

包含所有可能的命格、天赋、系统、身份等数据定义。
每个项目都有详细的描述和权重配置。
"""

ROLL_DATA = {
    # 基础属性范围
    "base_attributes": {
        "attack": {"min": 5, "max": 15, "description": "初始攻击力"},
        "defense": {"min": 3, "max": 12, "description": "初始防御力"},
        "health": {"min": 80, "max": 150, "description": "初始生命值"},
        "mana": {"min": 30, "max": 80, "description": "初始法力值"},
        "speed": {"min": 8, "max": 15, "description": "初始速度"},
        "comprehension": {"min": 1, "max": 10, "description": "悟性，影响技能学习速度"},
        "luck": {"min": 1, "max": 10, "description": "气运，影响机缘获得"},
        "constitution": {"min": 1, "max": 10, "description": "根骨，影响修炼速度"},
        "charm": {"min": 1, "max": 10, "description": "魅力，影响NPC好感度"},
    },
    # 灵根类型及权重
    "spiritual_roots": {
        "types": {
            "single": {
                "weight": 5,
                "name": "单灵根",
                "description": "极为罕见的天才体质，修炼速度极快",
                "bonus": {"cultivation_speed": 2.0, "breakthrough_chance": 1.3},
            },
            "dual": {
                "weight": 15,
                "name": "双灵根",
                "description": "少见的优秀体质，修炼速度快",
                "bonus": {"cultivation_speed": 1.5, "breakthrough_chance": 1.15},
            },
            "triple": {
                "weight": 30,
                "name": "三灵根",
                "description": "较为常见的体质，修炼速度正常",
                "bonus": {"cultivation_speed": 1.0, "breakthrough_chance": 1.0},
            },
            "quad": {
                "weight": 35,
                "name": "四灵根",
                "description": "普通体质，修炼速度较慢",
                "bonus": {"cultivation_speed": 0.8, "breakthrough_chance": 0.9},
            },
            "penta": {
                "weight": 15,
                "name": "五灵根",
                "description": "杂灵根，修炼困难但均衡发展",
                "bonus": {
                    "cultivation_speed": 0.6,
                    "breakthrough_chance": 0.8,
                    "all_element_affinity": 1.2,
                },
            },
        },
        "elements": ["金", "木", "水", "火", "土"],
    },
    # 命格配置
    "destinies": {
        "天命主角": {
            "weight": 1,
            "rarity": "legendary",
            "description": "天地气运所钟，命中注定的主角。遇难成祥，逢凶化吉，总能在绝境中找到生机。",
            "effects": {
                "luck": 5,
                "critical_save_chance": 0.5,
                "treasure_find_rate": 2.0,
                "npc_initial_favor": 20,
            },
        },
        "天煞孤星": {
            "weight": 5,
            "rarity": "rare",
            "description": "命犯孤煞，亲友缘薄。虽然孤独，但也因此心无旁骛，修炼速度远超常人。",
            "effects": {
                "cultivation_speed": 1.5,
                "npc_initial_favor": -10,
                "solo_combat_bonus": 1.3,
                "team_penalty": 0.7,
            },
        },
        "紫薇星君": {
            "weight": 3,
            "rarity": "epic",
            "description": "帝星加身，天生领袖。容易获得他人追随，建立势力时事半功倍。",
            "effects": {
                "charm": 3,
                "leadership": 5,
                "faction_reputation_gain": 1.5,
                "subordinate_loyalty": 1.3,
            },
        },
        "杀破狼": {
            "weight": 8,
            "rarity": "rare",
            "description": "杀星入命，天生战神。战斗天赋极高，越战越勇，但也容易招惹是非。",
            "effects": {
                "attack": 3,
                "combat_experience_gain": 1.5,
                "berserk_chance": 0.1,
                "enemy_aggro": 1.3,
            },
        },
        "福星高照": {
            "weight": 10,
            "rarity": "uncommon",
            "description": "福星庇佑，小有气运。虽无大富大贵，但总能平安顺遂。",
            "effects": {"luck": 2, "injury_reduction": 0.9, "daily_resource_bonus": 1.2},
        },
        "文曲星君": {
            "weight": 12,
            "rarity": "uncommon",
            "description": "文曲下凡，悟性超群。学习能力极强，参悟功法事半功倍。",
            "effects": {"comprehension": 3, "skill_learn_speed": 1.5, "spell_power": 1.2},
        },
        "武曲星君": {
            "weight": 12,
            "rarity": "uncommon",
            "description": "武曲临身，武道奇才。肉身强横，近战能力卓越。",
            "effects": {"constitution": 2, "attack": 2, "physical_skill_power": 1.3, "defense": 1},
        },
        "天生道体": {
            "weight": 2,
            "rarity": "epic",
            "description": "万中无一的道体，与天地大道亲和。修炼如喝水般简单，突破瓶颈如履平地。",
            "effects": {
                "cultivation_speed": 2.0,
                "breakthrough_chance": 1.5,
                "dao_comprehension": 5,
            },
        },
        "大器晚成": {
            "weight": 20,
            "rarity": "common",
            "description": "前期平平无奇，但潜力巨大。境界越高，优势越明显。",
            "effects": {
                "early_stage_penalty": 0.8,
                "late_stage_bonus": 1.5,
                "experience_retention": 1.2,
            },
        },
        "天生反骨": {
            "weight": 8,
            "rarity": "rare",
            "description": "性格叛逆，不服管教。容易与人结怨，但也因此激发斗志。",
            "effects": {"faction_reputation_gain": 0.7, "combat_fury": 1.2, "revenge_damage": 1.4},
        },
        "凡人之躯": {
            "weight": 25,
            "rarity": "common",
            "description": "普普通通的凡人，没有特殊天赋。但正因为平凡，所以拥有无限可能。",
            "effects": {"all_attributes": 1.0, "adaptability": 1.1},
        },
    },
    # 天赋配置
    "talents": {
        "剑道天才": {
            "weight": 10,
            "category": "combat",
            "description": "天生剑骨，对剑法有着超乎常人的理解。使用剑类武器时如臂使指。",
            "effects": {
                "sword_skill_power": 1.5,
                "sword_skill_learn_speed": 2.0,
                "sword_critical": 0.15,
            },
        },
        "丹药亲和": {
            "weight": 12,
            "category": "auxiliary",
            "description": "体质特殊，服用丹药效果倍增，且不易产生抗药性。",
            "effects": {
                "pill_effect": 1.5,
                "pill_toxin_resistance": 0.7,
                "alchemy_success_rate": 1.3,
            },
        },
        "阵法奇才": {
            "weight": 8,
            "category": "auxiliary",
            "description": "对阵法有着天生的敏锐感知，布阵破阵皆是好手。",
            "effects": {
                "formation_power": 1.4,
                "formation_break_chance": 1.5,
                "formation_comprehension": 3,
            },
        },
        "天生神力": {
            "weight": 15,
            "category": "physical",
            "description": "生而神力，力大无穷。近战伤害大幅提升。",
            "effects": {"physical_attack": 1.3, "strength": 5, "weapon_requirement": 0.8},
        },
        "灵体清净": {
            "weight": 10,
            "category": "spiritual",
            "description": "灵台清明，不染尘埃。修炼时不易走火入魔，心境提升快。",
            "effects": {
                "cultivation_stability": 1.5,
                "mental_defense": 1.3,
                "enlightenment_chance": 1.2,
            },
        },
        "商业奇才": {
            "weight": 20,
            "category": "social",
            "description": "天生的生意头脑，买卖交易总能获得额外收益。",
            "effects": {"buy_discount": 0.8, "sell_bonus": 1.3, "trade_reputation": 1.5},
        },
        "天生媚骨": {
            "weight": 8,
            "category": "social",
            "description": "魅力非凡，容易获得他人好感。社交场合如鱼得水。",
            "effects": {"charm": 5, "npc_favor_gain": 1.5, "persuasion_success": 1.3},
        },
        "战斗直觉": {
            "weight": 12,
            "category": "combat",
            "description": "战斗中的第六感极其敏锐，能预判敌人的攻击。",
            "effects": {"dodge_rate": 0.15, "counter_chance": 0.2, "battle_awareness": 3},
        },
        "炼器宗师": {
            "weight": 10,
            "category": "auxiliary",
            "description": "对炼器之道有着独特理解，炼制的法器品质更高。",
            "effects": {"crafting_quality": 1.4, "crafting_speed": 1.3, "material_save": 0.8},
        },
        "符箓妙手": {
            "weight": 10,
            "category": "auxiliary",
            "description": "制符天赋异禀，绘制的符箓威力更强，成功率更高。",
            "effects": {
                "talisman_power": 1.3,
                "talisman_success_rate": 1.5,
                "talisman_duration": 1.2,
            },
        },
        "异兽亲和": {
            "weight": 8,
            "category": "special",
            "description": "天生受到灵兽喜爱，容易获得灵兽认可，驯兽事半功倍。",
            "effects": {"beast_affinity": 2.0, "tame_success_rate": 1.5, "pet_growth_rate": 1.3},
        },
        "不死之身": {
            "weight": 2,
            "category": "special",
            "description": "体质异常，恢复力惊人。受伤后能快速自愈。",
            "effects": {"regeneration": 5, "revival_chance": 0.1, "poison_immunity": 0.5},
        },
    },
    # 系统配置（外挂系统）
    "systems": {
        "签到系统": {
            "weight": 20,
            "rarity": "common",
            "description": "每日签到可获得奖励，连续签到奖励递增。简单实用的辅助系统。",
            "features": [
                "每日签到获得灵石、丹药等基础资源",
                "连续签到7天获得稀有物品",
                "月签满勤有机会获得功法秘籍",
                "特殊地点签到双倍奖励",
            ],
            "initial_bonus": {"daily_spirit_stones": 10, "sign_in_reminder": True},
        },
        "任务系统": {
            "weight": 15,
            "rarity": "common",
            "description": "发布各类任务，完成后获得奖励。有主线、支线、日常等多种任务类型。",
            "features": [
                "主线任务推动境界提升",
                "支线任务获得额外奖励",
                "日常任务稳定收入来源",
                "隐藏任务触发特殊机缘",
            ],
            "initial_bonus": {"quest_reward_bonus": 1.2, "quest_tracker": True},
        },
        "商城系统": {
            "weight": 10,
            "rarity": "uncommon",
            "description": "神秘商城，可用特殊货币兑换各类珍稀物品。商品每日刷新。",
            "features": [
                "使用系统点数兑换物品",
                "每日限购优惠商品",
                "VIP等级享受折扣",
                "可购买其他世界的特殊物品",
            ],
            "initial_bonus": {"system_points": 1000, "daily_free_refresh": 1},
        },
        "抽奖系统": {
            "weight": 12,
            "rarity": "uncommon",
            "description": "消耗抽奖券进行抽奖，奖品从普通到神级应有尽有。欧皇的最爱。",
            "features": [
                "单抽、十连抽选择",
                "十连必出稀有",
                "奖池定期更新",
                "保底机制防止连续不中",
            ],
            "initial_bonus": {"lottery_tickets": 10, "lucky_bonus": 1.1},
        },
        "吞噬进化系统": {
            "weight": 5,
            "rarity": "rare",
            "description": "可吞噬各类物品、功法甚至生灵，转化为自身力量。极其强大但也极其危险。",
            "features": [
                "吞噬妖兽获得其天赋能力",
                "吞噬功法融合创造新法",
                "吞噬天材地宝强化体质",
                "吞噬失败会遭到反噬",
            ],
            "initial_bonus": {"devour_success_rate": 0.7, "digestion_speed": 1.5},
        },
        "修改器系统": {
            "weight": 3,
            "rarity": "epic",
            "description": "bug级存在，可以修改自身部分属性。每次修改需要消耗修改点。",
            "features": [
                "临时修改属性应对危机",
                "永久微调天赋资质",
                "修改物品属性",
                "修改点通过特殊方式获得",
            ],
            "initial_bonus": {"modification_points": 3, "attribute_modify_limit": 0.2},
        },
        "时间管理系统": {
            "weight": 8,
            "rarity": "rare",
            "description": "掌控时间流速，可加速修炼或减缓战斗节奏。时间系的外挂。",
            "features": [
                "修炼时时间加速最高10倍",
                "战斗中短暂时间减缓",
                "时光回溯撤销错误操作",
                "消耗时间点数激活能力",
            ],
            "initial_bonus": {"time_points": 100, "daily_time_acceleration": 2},
        },
        "合成系统": {
            "weight": 15,
            "rarity": "common",
            "description": "可将低级物品合成为高级物品，废物利用的好帮手。",
            "features": [
                "三合一基础合成",
                "配方解锁高级合成",
                "合成成功率可提升",
                "特殊材料触发变异合成",
            ],
            "initial_bonus": {
                "synthesis_success_rate": 0.8,
                "recipe_book": ["basic_pill_synthesis"],
            },
        },
        "洞察之眼": {
            "weight": 10,
            "rarity": "uncommon",
            "description": "能看穿他人修为、物品品质等信息。信息获取类外挂。",
            "features": [
                "查看NPC详细信息",
                "鉴定物品真实价值",
                "看破阵法弱点",
                "预测敌人下一步行动",
            ],
            "initial_bonus": {"insight_level": 1, "daily_insight_uses": 10},
        },
        "模拟器系统": {
            "weight": 6,
            "rarity": "rare",
            "description": "可模拟未来修炼道路，提前体验不同选择的结果。谋定而后动。",
            "features": ["模拟突破成功率", "预演战斗结果", "测试功法契合度", "每日有限模拟次数"],
            "initial_bonus": {"daily_simulations": 3, "simulation_accuracy": 0.8},
        },
    },
    # 身份配置
    "identities": {
        "凡人": {
            "weight": 30,
            "description": "普通人家出身，无背景无资源，一切靠自己打拼。",
            "starting_bonus": {"spirit_stones": 10, "reputation": 0, "potential_bonus": 1.1},
        },
        "散修": {
            "weight": 25,
            "description": "独自修行的修炼者，自由但孤独，资源全靠自己争取。",
            "starting_bonus": {"spirit_stones": 50, "combat_experience": 100, "survival_skills": 2},
        },
        "世家子弟": {
            "weight": 15,
            "description": "修仙世家的后人，有一定资源和人脉，但也有家族责任。",
            "starting_bonus": {
                "spirit_stones": 200,
                "family_reputation": 100,
                "starting_artifacts": 1,
                "family_pressure": True,
            },
        },
        "宗门弟子": {
            "weight": 20,
            "description": "名门正派的外门弟子，有稳定的修炼资源和传承。",
            "starting_bonus": {
                "spirit_stones": 100,
                "sect_contribution": 50,
                "monthly_resources": True,
                "sect_missions": True,
            },
        },
        "皇室血脉": {
            "weight": 5,
            "description": "凡俗王朝的皇族，虽在凡俗界地位崇高，但在修仙界只是起点。",
            "starting_bonus": {
                "spirit_stones": 500,
                "mortal_influence": 1000,
                "guard_protection": 2,
                "political_intrigue": True,
            },
        },
        "神秘来历": {
            "weight": 3,
            "description": "身世成谜，似乎有着不为人知的过去。随着修为提升，身世之谜会逐渐揭开。",
            "starting_bonus": {
                "random_legendary_item": 1,
                "hidden_bloodline": True,
                "mysterious_events": True,
                "unknown_enemies": True,
            },
        },
        "转世重生": {
            "weight": 2,
            "description": "前世为大能，今生重新修炼。虽修为尽失，但见识和经验还在。",
            "starting_bonus": {
                "comprehension": 5,
                "past_life_memories": True,
                "cultivation_experience": 1000,
                "karmic_enemies": True,
            },
        },
    },
    # 角色生成配置
    "character_creation": {
        "name_generation": {
            "surnames": [
                "李",
                "王",
                "张",
                "刘",
                "陈",
                "杨",
                "赵",
                "黄",
                "周",
                "吴",
                "徐",
                "孙",
                "马",
                "胡",
                "郭",
                "林",
                "何",
                "高",
                "罗",
                "郑",
            ],
            "male_names": [
                "天",
                "龙",
                "云",
                "风",
                "雷",
                "阳",
                "明",
                "浩",
                "宇",
                "辰",
                "轩",
                "峰",
                "杰",
                "涛",
                "然",
                "晨",
                "烨",
                "霆",
                "泽",
                "瀚",
            ],
            "female_names": [
                "雪",
                "月",
                "霜",
                "梦",
                "瑶",
                "琳",
                "婷",
                "燕",
                "莲",
                "凤",
                "芸",
                "菲",
                "诗",
                "韵",
                "灵",
                "妍",
                "玥",
                "曦",
                "萱",
                "蝶",
            ],
        }
    },
}
