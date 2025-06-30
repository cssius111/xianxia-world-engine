"""
角色系统API路由
处理角色创建、属性修改等操作
"""

from flask import Blueprint, current_app, jsonify, request, session
from run import is_dev_request
import logging

from src.xwe.core.attributes import CharacterAttributes
from src.xwe.core.character import Character, CharacterType
from src.xwe.features.random_player_panel import RandomPlayerPanel

bp = Blueprint("character", __name__)

logger = logging.getLogger(__name__)

# 背景加成配置
BACKGROUND_BONUSES = {
    "poor": {
        "name": "寒门子弟",
        "bonuses": {"max_health": 10, "defense": 2},
        "gold_multiplier": 0.5,
        "description": "出身贫寒，但意志坚定",
    },
    "merchant": {
        "name": "商贾之家",
        "bonuses": {"luck": 1},
        "gold_multiplier": 3.0,
        "description": "家境富裕，见多识广",
    },
    "scholar": {
        "name": "书香门第",
        "bonuses": {"comprehension": 1, "max_mana": 10},
        "gold_multiplier": 1.0,
        "description": "饱读诗书，天资聪颖",
    },
    "martial": {
        "name": "武林世家",
        "bonuses": {"attack_power": 5, "max_health": 20},
        "gold_multiplier": 1.0,
        "initial_skills": ["basic_sword"],
        "description": "习武世家，身手不凡",
    },
}


@bp.post("/api/character/create")
def create_character():
    """创建新角色"""
    try:
        dev_mode = is_dev_request(request)
        data = request.get_json()

        # 验证必需字段
        required_fields = ["name", "gender", "background", "attributes"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify({"success": False, "error": f"缺少必需字段: {field}"}),
                    400,
                )

        # 验证角色名
        name = data["name"].strip()
        if not name or len(name) > 20:
            return (
                jsonify({"success": False, "error": "角色名必须在1-20个字符之间"}),
                400,
            )

        # 获取游戏实例
        if "session_id" not in session:
            return jsonify({"success": False, "error": "会话已过期"}), 401

        # 这里需要从主应用获取游戏实例
        # 使用current_app来避免循环引用
        from run import get_game_instance

        instance = get_game_instance(session["session_id"])
        game = instance["game"]

        # 根据当前模式加载角色面板配置
        game_mode = session.get("game_mode", "player")
        panel = RandomPlayerPanel(game_mode=game_mode)

        # 创建角色属性
        attrs = CharacterAttributes()

        # 基础属性设置
        attrs.realm_name = "聚气期"
        attrs.realm_level = 1
        attrs.level = 1
        attrs.cultivation_level = 0
        attrs.max_cultivation = 100

        # 根据Roll的属性点分配计算实际属性
        if dev_mode:
            roll_attrs = {k: int(v) for k, v in data["attributes"].items()}
        else:
            roll_attrs = panel.sanitize_attributes(data["attributes"])

        # 根骨影响生命值和防御
        constitution = roll_attrs.get("constitution", 5)
        attrs.constitution = constitution
        attrs.max_health = 80 + constitution * 10
        attrs.current_health = attrs.max_health
        attrs.defense = 3 + constitution

        # 悟性影响修炼速度（存储为额外数据）
        comprehension = roll_attrs.get("comprehension", 5)
        attrs.comprehension = comprehension

        # 神识影响法力值和法术威力
        spirit = roll_attrs.get("spirit", 5)
        attrs.willpower = spirit
        attrs.max_mana = 30 + spirit * 10
        attrs.current_mana = attrs.max_mana

        # 机缘影响掉落率（存储为额外数据）
        luck = roll_attrs.get("luck", 5)
        attrs.luck = luck

        # 基础攻击力
        attrs.attack_power = 10

        # 体力值
        attrs.max_stamina = 100
        attrs.current_stamina = attrs.max_stamina

        # 应用背景加成
        background = data.get("background", "poor")
        if background in BACKGROUND_BONUSES:
            bg_data = BACKGROUND_BONUSES[background]
            bonuses = bg_data["bonuses"]

            # 应用属性加成
            for attr, value in bonuses.items():
                if hasattr(attrs, attr):
                    current = getattr(attrs, attr)
                    setattr(attrs, attr, current + value)

        # 创建角色
        player = Character(
            id="player",
            name=name,
            character_type=CharacterType.PLAYER,
            attributes=attrs,
        )
        if player.attributes is attrs:
            logger.debug("[CHARACTER] 写入属性成功")
        else:
            logger.debug("[CHARACTER] 写入属性失败")

        # 设置额外数据
        player.extra_data = {
            "gender": data["gender"],
            "background": background,
            "background_name": BACKGROUND_BONUSES[background]["name"],
            "comprehension": comprehension,
            "luck": luck,
            "created_at": str(
                current_app.config.get("SERVER_START_TIME", "2025-01-01")
            ),
        }
        destiny = data.get("destiny")
        if destiny is not None:
            player.extra_data["destiny"] = destiny

        logger.info(
            "[CHARACTER] 创建角色 %s，属性: 根骨=%d 悟性=%d 神识=%d 机缘=%d，灵根=%s，命运=%s",
            name,
            constitution,
            comprehension,
            spirit,
            luck,
            player.spiritual_root,
            destiny,
        )

        logger.debug(
            "[CHARACTER] 保存额外数据键: %s",
            list(player.extra_data.keys()),
        )

        # 初始化背包和金币
        if hasattr(player, "inventory"):
            gold_multiplier = BACKGROUND_BONUSES[background].get("gold_multiplier", 1.0)
            player.inventory.gold = int(100 * gold_multiplier)

            # 武林世家初始剑法
            if (
                background == "martial"
                and "initial_skills" in BACKGROUND_BONUSES[background]
            ):
                # TODO: 添加初始技能
                pass

        # 设置到游戏状态
        game.game_state.player = player
        game.game_state.current_location = "青云城"

        # 添加欢迎日志
        game.game_state.logs.append(
            {
                "type": "system",
                "message": f"欢迎来到修仙世界，{name}！",
                "timestamp": current_app.config.get(
                    "CURRENT_TIME", "2025-01-01 00:00:00"
                ),
            }
        )

        game.game_state.logs.append(
            {
                "type": "story",
                "message": f'作为{BACKGROUND_BONUSES[background]["name"]}，你怀揣着对修仙的向往，踏上了这条充满未知的道路...',
                "timestamp": current_app.config.get(
                    "CURRENT_TIME", "2025-01-01 00:00:01"
                ),
            }
        )

        # 标记需要刷新
        instance["need_refresh"] = True

        return jsonify(
            {
                "success": True,
                "message": "角色创建成功",
                "character": {
                    "name": player.name,
                    "level": player.attributes.level,
                    "realm": player.attributes.realm_name,
                    "location": game.game_state.current_location,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": f"创建角色失败: {str(e)}"}), 500


@bp.get("/api/character/info")
def get_character_info():
    """获取当前角色信息"""
    try:
        if "session_id" not in session:
            return jsonify({"success": False, "error": "会话已过期"}), 401

        from run import get_game_instance

        instance = get_game_instance(session["session_id"])
        game = instance["game"]

        player = game.game_state.player
        if not player:
            return jsonify({"success": False, "error": "角色不存在"}), 404

        # 构建角色信息
        character_info = {
            "name": player.name,
            "attributes": {
                "realm_name": player.attributes.realm_name,
                "realm_level": player.attributes.realm_level,
                "level": player.attributes.level,
                "cultivation_level": player.attributes.cultivation_level,
                "max_cultivation": player.attributes.max_cultivation,
                "current_health": player.attributes.current_health,
                "max_health": player.attributes.max_health,
                "current_mana": player.attributes.current_mana,
                "max_mana": player.attributes.max_mana,
                "current_stamina": player.attributes.current_stamina,
                "max_stamina": player.attributes.max_stamina,
                "attack_power": player.attributes.attack_power,
                "defense": player.attributes.defense,
            },
            "extra_data": getattr(player, "extra_data", {}),
            "location": game.game_state.current_location,
        }

        # 添加背包信息
        if hasattr(player, "inventory"):
            character_info["inventory"] = {
                "gold": getattr(player.inventory, "gold", 0),
                "items": [],  # TODO: 添加物品列表
            }

        return jsonify({"success": True, "character": character_info})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
