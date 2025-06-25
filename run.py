#!/usr/bin/env python3
"""
修仙世界引擎 - 统一启动器
集成 DeepSeek NLP 命令处理
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from xwe.core.command_router import CommandRouter
from xwe.core.cultivation_system import CultivationSystem
from xwe.core.data_loader import DataLoader
from xwe.core.game_core import create_enhanced_game
from xwe.features import ExplorationSystem, InventorySystem
from xwe.features.ai_personalization import AIPersonalization
from xwe.features.community_system import CommunitySystem
from xwe.features.narrative_system import NarrativeSystem
from xwe.features.technical_ops import TechnicalOps


def is_dev_request(req) -> bool:
    """检查请求是否开启开发模式"""
    return (
        req.args.get("dev") == "true"
        or str(req.headers.get("dev", "")).lower() == "true"
    )


# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Flask应用配置
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "xianxia_world_secret_key_2025"
app.config["JSON_AS_ASCII"] = False

# 日志配置
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("XianxiaEngine")

# 确保必要目录存在
for directory in ["saves", "logs"]:
    Path(directory).mkdir(parents=True, exist_ok=True)

# 初始化数据加载器
data_loader = DataLoader()

# 初始化游戏系统
exploration_system = ExplorationSystem()
inventory_system = InventorySystem()

# ---------------- 游戏实例管理 -----------------
# Web UI 优化版中提供的多会话支持
game_instances = {}


def get_game_instance(session_id):
    """获取或创建游戏实例"""
    if session_id not in game_instances:
        game_mode = os.getenv("GAME_MODE", "player")
        game = create_enhanced_game(game_mode=game_mode)

        # 初始化系统
        game.cultivation_system = CultivationSystem()
        game.narrative_system = NarrativeSystem()
        game.ai_personalization = AIPersonalization()
        game.community_system = CommunitySystem()
        game.technical_ops = TechnicalOps()

        # 创建默认玩家
        if not game.game_state.player:
            from xwe.core.attributes import CharacterAttributes
            from xwe.core.character import Character, CharacterType

            attrs = CharacterAttributes()
            attrs.realm_name = "炼气期"
            attrs.realm_level = 1
            attrs.level = 1
            attrs.cultivation_level = 0
            attrs.max_cultivation = 100
            attrs.realm_progress = 0
            attrs.faction = "正道"

            attrs.current_health = 100
            attrs.max_health = 100
            attrs.current_mana = 50
            attrs.max_mana = 50
            attrs.current_stamina = 100
            attrs.max_stamina = 100
            attrs.attack_power = 10
            attrs.defense = 5

            player = Character(
                id="player",
                name="无名侠客",
                character_type=CharacterType.PLAYER,
                attributes=attrs,
            )
            game.game_state.player = player
            game.game_state.current_location = "青云城"
            game.game_state.logs = []

        game_instances[session_id] = {
            "game": game,
            "last_update": time.time(),
            "need_refresh": True,
        }

    return game_instances[session_id]


def cleanup_old_instances():
    """清理超时的游戏实例"""
    current_time = time.time()
    timeout = 3600

    to_remove = []
    for sid, inst in game_instances.items():
        if current_time - inst["last_update"] > timeout:
            to_remove.append(sid)

    for sid in to_remove:
        try:
            instance = game_instances[sid]
            if hasattr(instance["game"], "technical_ops"):
                instance["game"].technical_ops.save_game(instance["game"].game_state)
        except Exception:
            pass

        del game_instances[sid]


# 初始化命令路由器（带NLP支持）
try:
    command_router = CommandRouter(use_nlp=True)
    logger.info("命令路由器初始化成功（NLP模式）")
except Exception as e:
    logger.warning(f"NLP模式初始化失败: {e}, 使用传统模式")
    command_router = CommandRouter(use_nlp=False)

# ========== 页面路由 ==========


@app.route("/")
def index():
    """首页"""
    if session.get("player_created"):
        return redirect(url_for("game_screen"))
    return redirect(url_for("intro_screen"))


@app.route("/welcome")
def welcome():
    """欢迎页面 - 新游戏或继续游戏"""
    cleanup_old_instances()
    save_exists = Path("saves/autosave.json").exists()
    return render_template("welcome.html", save_exists=save_exists)


@app.route("/intro")
def intro_screen():
    """角色创建页面"""
    dev_mode = request.args.get("mode") == "dev"
    return render_template("intro_optimized.html", dev_mode=dev_mode)


# 新的开始页面路由，渲染角色创建并显示欢迎模态框
@app.route("/start")
def start_screen():
    """开始页面"""
    dev_mode = request.args.get("mode") == "dev"
    return render_template("intro_optimized.html", dev_mode=dev_mode)


@app.route("/game")
def game_screen():
    """游戏主界面"""
    # 提供默认数据
    player_data = {
        "name": session.get("player_name", "无名侠客"),
        "attributes": {
            "realm_name": "炼气期",
            "realm_level": 1,
            "current_health": 100,
            "max_health": 100,
            "current_mana": 50,
            "max_mana": 50,
            "current_stamina": 100,
            "max_stamina": 100,
            "attack_power": 10,
            "defense": 5,
        },
        "extra_data": {},
    }

    return render_template(
        "game_enhanced_optimized_v2.html",
        player=player_data,
        location="青云城",
        buffs=[],
        special_status=[],
        is_new_session=True,
        dev_mode=request.args.get("mode") == "dev",
    )


@app.route("/roll")
def roll_screen():
    """属性随机页面"""
    return render_template("screens/roll_screen.html")


@app.route("/choose")
def choose_start():
    """开局选择页面"""
    return render_template("screens/choose_start.html")


# ========== 模态框路由 ==========


@app.route("/modal/<modal_name>")
def modal(modal_name):
    """通用模态框加载"""
    allowed_modals = [
        "status",
        "inventory",
        "cultivation",
        "achievement",
        "exploration",
        "map",
        "quest",
        "save",
        "load",
        "help",
        "settings",
        "exit",
    ]

    if modal_name not in allowed_modals:
        return "无效的模态框", 404

    try:
        return render_template(f"modals/{modal_name}.html")
    except Exception:
        return f"<h3>{modal_name.title()}</h3><p>功能开发中...</p>"


# ========== API路由 ==========


@app.route("/need_refresh")
def need_refresh():
    """前端轮询热更新/断线检测"""
    return jsonify({"refresh": False, "version": "2025-06-25"})


@app.route("/create_character", methods=["POST"])
def create_character():
    """创建角色"""
    dev_mode = is_dev_request(request)
    data = request.get_json()

    if data and "name" in data:
        player_name = data.get("name", "无名侠客")
        session["player_name"] = player_name
        session["player_id"] = f"player_{player_name}"  # 简单的玩家ID生成
        session["location"] = "青云城"  # 初始位置

        # 创建初始背包
        inventory_system.create_initial_inventory(session["player_id"])

        logger.info(f"创建角色: {player_name}")

        if not session.get("player_created"):
            session["player_created"] = True

        if "destiny" in data:
            session["destiny"] = data["destiny"]

    if dev_mode:
        session["dev"] = True

    return jsonify(
        {
            "success": True,
            "narrative": f"{data.get('name', '无名侠客')} 的修仙之旅由此开始。",
        }
    )


@app.route("/get_audio_list")
def get_audio_list():
    """获取可用音频文件列表"""
    audio_dir = Path("static/audio")
    audio_files = []

    if audio_dir.exists():
        audio_extensions = [".mp3", ".ogg", ".wav"]
        for ext in audio_extensions:
            audio_files.extend([f.name for f in audio_dir.glob(f"*{ext}")])

    return jsonify({"files": audio_files})


@app.route("/save_game", methods=["POST"])
def save_game_route():
    """保存游戏"""
    if "session_id" not in session:
        return jsonify({"success": False, "error": "会话已过期"})

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    try:
        if hasattr(game, "technical_ops"):
            game.technical_ops.save_game(game.game_state)
        return jsonify({"success": True, "message": "游戏已保存"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/load_game", methods=["POST"])
def load_game_route():
    """加载游戏"""
    if "session_id" not in session:
        return jsonify({"success": False, "error": "会话已过期"})

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    try:
        if hasattr(game, "technical_ops"):
            loaded_state = game.technical_ops.load_game()
            if loaded_state:
                game.game_state = loaded_state
                instance["need_refresh"] = True
                return jsonify({"success": True, "message": "游戏已加载"})
        return jsonify({"success": False, "error": "没有找到存档"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/roll", methods=["POST"])
def api_roll():
    """抽卡API"""
    import sys as _sys

    _sys.path.append(str(Path(__file__).parent))
    import random

    from scripts.gen_character import (
        gen_from_prompt,
        gen_random,
        gen_template,
        save_character,
    )

    data = request.get_json()
    mode = data.get("mode", "random")

    if mode == "random":
        character = gen_random()
    elif mode == "template":
        template_type = data.get("type", "sword")
        character = gen_template(template_type)
    elif mode == "custom":
        prompt = data.get("prompt", "")
        character = gen_from_prompt(prompt)
    else:
        character = gen_random()

    # 随机命格
    destiny_data = data_loader.get_destinies()
    options = destiny_data.get("destiny_grades", [])
    destiny = random.choice(options) if options else None

    save_character(character)

    return jsonify({"success": True, "character": character, "destiny": destiny})


@app.route("/command", methods=["POST"])
def process_command():
    """处理游戏命令（集成NLP）"""
    dev_mode = is_dev_request(request)
    data = request.get_json()
    user_input = data.get("text", data.get("command", ""))  # 兼容两种字段名
    player_id = session.get("player_id", "default")

    if dev_mode:
        session["dev"] = True

    # 使用命令路由器处理
    command_handler, params = command_router.route_command(user_input)

    # 记录解析结果
    if "explanation" in params:
        logger.info(
            f"命令解析: {user_input} -> {command_handler} ({params.get('explanation')})"
        )
    else:
        logger.info(f"命令解析: {user_input} -> {command_handler}")

    # 根据不同的命令类型处理
    if command_handler == "explore":
        # 执行探索
        location = session.get("location", "青云城")
        explore_result = exploration_system.explore(location)

        # 将获得的物品加入背包
        result_text = explore_result["narration"]
        if explore_result["items"]:
            added_items = inventory_system.add_items(player_id, explore_result["items"])
            if added_items:
                items_text = "、".join(
                    [f"{name}x{qty}" for name, qty in added_items.items()]
                )
                result_text += f"\n\n获得物品：{items_text}"

        return jsonify(
            {
                "success": True,
                "result": result_text,
                "bag_updated": bool(explore_result["items"]),
                "explore_result": explore_result,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    elif command_handler == "inventory":
        # 查看背包
        inventory_data = inventory_system.get_inventory_data(player_id)

        if inventory_data["items"]:
            items_text = "\n".join(
                [
                    f"- {item['name']} x{item['quantity']}"
                    for item in inventory_data["items"]
                ]
            )
            result_text = (
                f"你的背包中有：\n{items_text}\n\n"
                f"金币：{inventory_data['gold']}\n"
                f"容量：{inventory_data['used']}/{inventory_data['capacity']}"
            )
        else:
            result_text = "你的背包空空如也。"

        return jsonify(
            {
                "success": True,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    elif command_handler == "status":
        # 查看状态
        result_text = f"【{session.get('player_name', '无名侠客')}】\n境界：炼气期一层\n生命：100/100\n法力：50/50\n体力：100/100"
        return jsonify(
            {
                "success": True,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    elif command_handler == "cultivate":
        # 修炼
        duration = params.get("duration", "")
        if duration:
            result_text = f"你开始{params.get('mode', '打坐')}修炼{duration}，感受天地灵气缓缓流入体内..."
        else:
            result_text = "你开始打坐修炼，感受天地灵气缓缓流入体内..."

        return jsonify(
            {
                "success": True,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    elif command_handler == "move":
        # 移动
        location = params.get("location", params.get("target", ""))
        if location:
            # 更新位置
            session["location"] = location
            result_text = f"你来到了{location}。"
        else:
            result_text = "你想去哪里？（可用地点：城主府、丹药铺、任务大厅、城外）"

        return jsonify(
            {
                "success": True,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    elif command_handler == "use_item":
        # 使用物品
        item_name = params.get("item", params.get("target", ""))
        if item_name:
            # 检查并使用物品
            if inventory_system.has_item(player_id, item_name):
                inventory_system.remove_item(player_id, item_name, 1)
                result_text = f"你使用了{item_name}。"
            else:
                result_text = f"你没有{item_name}。"
        else:
            result_text = "请指定要使用的物品。"

        return jsonify(
            {
                "success": True,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    elif command_handler == "talk":
        # 对话
        target = params.get("target", "")
        if target:
            result_text = f"你与{target}交谈。\n{target}：少侠好，有什么可以帮助你的吗？"
        else:
            result_text = "附近没有可以交谈的人。"

        return jsonify(
            {
                "success": True,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    elif command_handler == "help":
        # 帮助
        result_text = command_router.get_help_text()
        return jsonify(
            {
                "success": True,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    elif command_handler == "unknown":
        # 未知命令
        confidence = params.get("confidence", 0.5)
        if confidence < 0.5:
            result_text = f"抱歉，我不太理解'{user_input}'的意思。请尝试其他表达方式。"
        else:
            result_text = f"命令'{user_input}'暂未实现。"

        return jsonify(
            {
                "success": True,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    elif command_handler == "context_error":
        # 上下文错误
        result_text = f"在当前场景下，{params.get('message', '该命令不可用')}。"
        return jsonify(
            {
                "success": False,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )

    else:
        # 其他命令
        result_text = f"命令'{command_handler}'功能开发中..."
        return jsonify(
            {
                "success": True,
                "result": result_text,
                "parsed_command": {"handler": command_handler, "params": params},
            }
        )


@app.route("/status")
def get_status():
    """获取游戏状态"""
    player_id = session.get("player_id", "default")
    inventory_data = inventory_system.get_inventory_data(player_id)

    player_name = session.get("player_name", "无名侠客")
    realm_name = "炼气期"
    realm_level = 1
    current_health = 100
    max_health = 100
    current_mana = 50
    max_mana = 50
    location = session.get("location", "青云城")

    if "session_id" in session:
        try:
            instance = get_game_instance(session["session_id"])
            game = instance["game"]
            player = getattr(game.game_state, "player", None)
            if player:
                player_name = player.name
                realm_name = player.attributes.realm_name
                realm_level = player.attributes.realm_level
                current_health = player.attributes.current_health
                max_health = player.attributes.max_health
                current_mana = player.attributes.current_mana
                max_mana = player.attributes.max_mana
                location = game.game_state.current_location
        except Exception as e:
            logger.error(f"读取游戏状态失败: {e}")

    return jsonify(
        {
            "player": {
                "name": player_name,
                "attributes": {
                    "realm_name": realm_name,
                    "realm_level": realm_level,
                    "current_health": current_health,
                    "max_health": max_health,
                    "current_mana": current_mana,
                    "max_mana": max_mana,
                },
            },
            "location": location,
            "gold": inventory_data["gold"],
            "inventory": inventory_data,
        }
    )


@app.route("/log")
def get_log():
    """获取游戏日志"""
    return jsonify(
        {
            "logs": [
                "欢迎来到修仙世界！",
                "你出生在青云城，开始了修仙之旅。",
                "输入'帮助'查看可用命令。",
            ]
        }
    )


@app.route("/nlp_cache_info")
def get_nlp_cache_info():
    """获取NLP缓存信息"""
    cache_info = command_router.get_nlp_cache_info()
    if cache_info:
        return jsonify({"success": True, "cache_info": cache_info})
    else:
        return jsonify({"success": False, "message": "NLP未启用或不支持缓存"})


@app.route("/clear_nlp_cache", methods=["POST"])
def clear_nlp_cache():
    """清除NLP缓存"""
    command_router.clear_nlp_cache()
    return jsonify({"success": True, "message": "NLP缓存已清除"})


# 数据接口
@app.route("/data/destiny")
def get_destiny_data():
    """返回命格数据"""
    return jsonify(data_loader.get_destinies())


@app.route("/data/fortune")
def get_fortune_data():
    """返回气运数据"""
    return jsonify(data_loader.get_fortunes())


@app.route("/data/templates")
def get_templates_data():
    """返回角色模板数据"""
    return jsonify(data_loader.get_character_templates())


@app.route("/api/parse_custom", methods=["POST"])
def parse_custom_text():
    """使用LLM解析自定义背景"""
    try:
        data = request.get_json()
        text = data.get("text", "")

        try:
            import json as pyjson

            from xwe.core.nlp import LLMClient

            llm = LLMClient()
            result = llm.chat(text)

            try:
                parsed = pyjson.loads(result)
            except Exception:
                parsed = {"result": result}

            return jsonify({"success": True, "data": parsed})

        except ImportError:
            # NLP模块不可用
            return jsonify({"success": False, "error": "NLP功能未启用或不可用"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ========== NLP监控路由 ==========


@app.route("/nlp_monitor")
def nlp_monitor():
    """NLP监控面板"""
    return render_template("nlp_monitor.html")


@app.route("/api/nlp/stats")
def get_nlp_stats():
    """获取NLP统计数据"""
    try:
        from xwe.core.nlp.monitor import get_nlp_monitor

        monitor = get_nlp_monitor()
        stats = monitor.get_stats()
        return jsonify({"success": True, "stats": stats})
    except ImportError:
        # NLP模块不可用
        return jsonify({"success": False, "error": "NLP功能未安装或不可用"})
    except Exception as e:
        logger.error(f"获取NLP统计失败: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/nlp/export")
def export_nlp_metrics():
    """导出NLP性能数据"""
    try:
        import os
        import tempfile

        from xwe.core.nlp.monitor import get_nlp_monitor

        monitor = get_nlp_monitor()

        # 创建临时文件
        fd, path = tempfile.mkstemp(suffix=".json")
        try:
            # 导出数据
            monitor.export_metrics(path)

            # 读取文件内容
            with open(path, "rb") as f:
                data = f.read()

            # 返回文件
            response = make_response(data)
            response.headers["Content-Type"] = "application/json"
            response.headers[
                "Content-Disposition"
            ] = f'attachment; filename=nlp_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            return response

        finally:
            # 清理临时文件
            os.close(fd)
            os.unlink(path)

    except ImportError:
        return jsonify({"success": False, "error": "NLP功能未安装或不可用"}), 500
    except Exception as e:
        logger.error(f"导出NLP数据失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/nlp/config")
def get_nlp_config():
    """获取NLP配置"""
    try:
        from xwe.core.nlp.config import get_nlp_config

        config = get_nlp_config()

        # 不暴露敏感信息
        safe_config = {
            "enabled": config.is_enabled(),
            "provider": config.get("provider"),
            "model": config.get("model"),
            "cache_size": config.get("cache_size"),
            "fallback_enabled": config.get("fallback_enabled"),
            "performance_monitoring": config.get("performance_monitoring"),
        }

        return jsonify({"success": True, "config": safe_config})
    except ImportError:
        # NLP模块不可用，返回默认配置
        return jsonify(
            {
                "success": True,
                "config": {
                    "enabled": False,
                    "provider": "none",
                    "model": "none",
                    "cache_size": 0,
                    "fallback_enabled": True,
                    "performance_monitoring": False,
                },
            }
        )
    except Exception as e:
        logger.error(f"获取NLP配置失败: {e}")
        return jsonify({"success": False, "error": str(e)})


# ========== 工具路由 ==========


@app.route("/favicon.ico")
def favicon():
    """返回站点图标"""
    return send_from_directory(
        os.path.join(app.root_path, "static", "favicon_io"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/sw.js")
def service_worker():
    """Service Worker"""
    try:
        return (
            app.send_static_file("sw.js"),
            200,
            {"Content-Type": "application/javascript", "Cache-Control": "no-cache"},
        )
    except Exception:
        return "", 404


# ========== 错误处理 ==========


@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404错误: {request.path}")
    return "页面未找到", 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"500错误: {str(e)}")
    return "服务器错误", 500


# ========== 启动服务器 ==========


def main():
    """主函数"""
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("DEBUG", "true").lower() == "true"

    print("=" * 60)
    print("🎮 修仙世界引擎")
    print("=" * 60)
    print(f"🌐 访问地址: http://localhost:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print(f"📝 日志目录: {Path('logs').absolute()}")
    print(f"💾 存档目录: {Path('saves').absolute()}")

    # 显示NLP状态
    if hasattr(command_router, "use_nlp") and command_router.use_nlp:
        print("🤖 DeepSeek NLP: 已启用")
    else:
        print("🤖 DeepSeek NLP: 未启用（使用传统解析）")

    print("=" * 60)
    print("使用 Ctrl+C 停止服务器")
    print("=" * 60)

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
