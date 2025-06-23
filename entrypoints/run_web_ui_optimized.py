import os
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session, redirect, url_for

from api import register_api
from routes import character, intel, lore
from xwe.core.cultivation_system import CultivationSystem

# 导入游戏核心
from xwe.core.game_core import create_enhanced_game
from xwe.features.ai_personalization import AIPersonalization
from xwe.features.community_system import CommunitySystem
from xwe.features.narrative_system import NarrativeSystem
from xwe.features.technical_ops import TechnicalOps

# 使用项目根目录下的 templates 目录
templates_path = Path(__file__).resolve().parent.parent / "templates"
app = Flask(__name__, static_folder="static", template_folder=str(templates_path))
app.secret_key = "xianxia_world_secret_key_2025"
register_api(app)

# 注册路由蓝图
app.register_blueprint(lore.bp)
app.register_blueprint(character.bp)
app.register_blueprint(intel.bp)

# 全局游戏实例管理
game_instances = {}


def get_game_instance(session_id):
    """获取或创建游戏实例"""
    if session_id not in game_instances:
        # 创建新游戏实例
        game_mode = os.getenv("GAME_MODE", "player")
        game = create_enhanced_game(game_mode=game_mode)

        # 初始化各系统
        # CultivationSystem 构造函数不接受游戏实例参数
        game.cultivation_system = CultivationSystem()
        game.narrative_system = NarrativeSystem()
        game.ai_personalization = AIPersonalization()
        game.community_system = CommunitySystem()
        game.technical_ops = TechnicalOps()

        # 创建玩家
        if not game.game_state.player:
            # xwe.core.attributes 模块中并未定义 Attributes 类，实际类名为
            # CharacterAttributes。这里直接导入并使用该类。
            from xwe.core.attributes import CharacterAttributes
            from xwe.core.character import Character

            # 使用平衡后的配置
            # 创建角色属性实例
            attrs = CharacterAttributes()
            attrs.realm_name = "炼气期"
            attrs.realm_level = 1
            attrs.level = 1
            attrs.cultivation_level = 0
            attrs.max_cultivation = 100
            attrs.realm_progress = 0
            attrs.faction = "正道"

            # 使用平衡后的属性值
            attrs.current_health = 100
            attrs.max_health = 100
            attrs.current_mana = 50
            attrs.max_mana = 50
            attrs.current_stamina = 100
            attrs.max_stamina = 100
            attrs.attack_power = 10
            attrs.defense = 5

            from xwe.core.character import CharacterType

            player = Character(
                id="player", name="无名侠客", character_type=CharacterType.PLAYER, attributes=attrs
            )
            game.game_state.player = player
            game.game_state.current_location = "青云城"

            # 清空日志，准备新游戏
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
    timeout = 3600  # 1小时超时

    to_remove = []
    for session_id, instance in game_instances.items():
        if current_time - instance["last_update"] > timeout:
            to_remove.append(session_id)

    for session_id in to_remove:
        # 尝试保存游戏
        try:
            instance = game_instances[session_id]
            if hasattr(instance["game"], "technical_ops"):
                instance["game"].technical_ops.save_game(instance["game"].game_state)
        except Exception:
            pass

        del game_instances[session_id]


@app.route("/")
def index():
    """主页面 - 重定向到欢迎页面"""
    return redirect(url_for('welcome'))


@app.route("/welcome")
def welcome():
    """欢迎页面 - 新游戏/继续游戏/开发者模式"""
    # 清理旧实例
    cleanup_old_instances()
    
    # 检查是否有存档
    save_exists = Path("saves/autosave.json").exists()
    
    return render_template("welcome.html", save_exists=save_exists)


@app.route("/intro")
def intro():
    """角色创建介绍页面"""
    # 确保会话ID
    if "session_id" not in session:
        session["session_id"] = str(time.time())
    
    # 检查是否是开发模式
    dev_mode = request.args.get('mode') == 'dev'
    
    return render_template("intro_optimized.html", dev_mode=dev_mode)


@app.route("/game")
def game():
    """游戏主界面"""
    # 确保会话ID
    if "session_id" not in session:
        session["session_id"] = str(time.time())
        session["is_new_session"] = True
    else:
        session["is_new_session"] = False

    # 获取游戏实例
    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    # 准备渲染数据
    player = game.game_state.player
    
    # 检查是否是开发模式
    dev_mode = request.args.get('mode') == 'dev' or session.get('dev_mode', False)
    if dev_mode:
        session['dev_mode'] = True
        app.logger.info("[DEV MODE] Game page accessed in development mode")

    # 传递是否是新会话的标志
    return render_template(
        "game_enhanced_optimized.html",
        player=player,
        location=game.game_state.current_location,
        buffs=[],
        special_status=[],
        is_new_session=session.get("is_new_session", False),
        dev_mode=dev_mode,
    )


@app.route("/command", methods=["POST"])
def process_command():
    """处理游戏命令"""
    data = request.get_json()
    command = data.get("command", "")

    if "session_id" not in session:
        return jsonify({"error": "会话已过期，请刷新页面"})

    instance = get_game_instance(session["session_id"])
    game = instance["game"]
    
    # 开发模式日志
    if session.get('dev_mode', False):
        app.logger.info(f"[DEV MODE] Processing command: {command}")
        app.logger.info(f"[DEV MODE] Current location: {game.game_state.current_location}")

    # 处理命令
    game.process_command(command)

    # 标记需要刷新
    instance["need_refresh"] = True
    instance["last_update"] = time.time()

    return jsonify({"success": True})


@app.route("/status")
def get_status():
    """获取游戏状态"""
    if "session_id" not in session:
        return jsonify({"error": "会话已过期"})

    instance = get_game_instance(session["session_id"])
    game = instance["game"]
    player = game.game_state.player

    # 准备状态数据
    status_data = {
        "player": None,
        "location": game.game_state.current_location,
        "location_name": game.game_state.current_location,
        "gold": 0,
    }

    if player:
        status_data["player"] = {
            "name": player.name,
            "attributes": {
                "realm_name": player.attributes.realm_name,
                "realm_level": player.attributes.realm_level,
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
        }

        # 获取金币数量
        if hasattr(player, "inventory") and hasattr(player.inventory, "gold"):
            status_data["gold"] = player.inventory.gold

    return jsonify(status_data)


@app.route("/log")
def get_log():
    """获取游戏日志"""
    if "session_id" not in session:
        return jsonify({"logs": []})

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    # 限制日志数量，避免传输过多数据
    logs = game.game_state.logs[-100:]  # 最多显示最近100条

    return jsonify({"logs": logs})


@app.route("/need_refresh")
def need_refresh():
    """检查是否需要刷新"""
    if "session_id" not in session:
        return jsonify({"refresh": False})

    instance = get_game_instance(session["session_id"])
    need_refresh = instance.get("need_refresh", False)

    # 重置标记
    if need_refresh:
        instance["need_refresh"] = False

    return jsonify({"refresh": need_refresh})


@app.route("/save_game", methods=["POST"])
def save_game():
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
def load_game():
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


@app.route("/create_character", methods=["POST"])
def create_character():
    """创建角色"""
    if "session_id" not in session:
        session["session_id"] = str(time.time())
    
    data = request.get_json()
    instance = get_game_instance(session["session_id"])
    game = instance["game"]
    
    # 创建新角色
    if game.game_state.player:
        player = game.game_state.player
        player.name = data.get('name', '无名侠客')
        
        # 根据选择的模式设置属性
        character_type = data.get('type', 'random')
        if character_type == 'sword':  # 剑修
            player.attributes.attack_power += 5
            player.attributes.defense -= 2
            player.extra_data = {'faction': '剑宗', 'spiritual_root': '金'}
        elif character_type == 'body':  # 体修
            player.attributes.defense += 5
            player.attributes.speed -= 2
            player.extra_data = {'faction': '炼体宗', 'spiritual_root': '土'}
        elif character_type == 'magic':  # 法修
            player.attributes.max_mana += 20
            player.attributes.max_health -= 10
            player.extra_data = {'faction': '玄天宗', 'spiritual_root': '水'}
        
        # 重新计算衍生属性
        player.attributes.calculate_derived_attributes()
        
    instance["need_refresh"] = True
    return jsonify({"success": True})


@app.route("/get_audio_list")
def get_audio_list():
    """获取音频文件列表"""
    audio_dir = Path("static/audio")
    audio_files = []
    
    if audio_dir.exists():
        # 支持的音频格式
        audio_extensions = ['.mp3', '.ogg', '.wav']
        for ext in audio_extensions:
            audio_files.extend([f.name for f in audio_dir.glob(f"*{ext}")])
    
    return jsonify({"files": audio_files})


@app.route("/modal/<modal_name>")
def load_modal(modal_name):
    """加载模态框内容"""
    # 白名单验证
    allowed_modals = [
        'status', 'inventory', 'cultivation', 'achievement', 
        'exploration', 'map', 'quest', 'save', 'load', 
        'help', 'settings', 'exit'
    ]
    
    if modal_name not in allowed_modals:
        return "Invalid modal", 404
    
    # 获取当前游戏状态
    if "session_id" in session:
        instance = get_game_instance(session["session_id"])
        game = instance["game"]
        player = game.game_state.player
    else:
        player = None
        game = None
    
    # 尝试加载对应的模态框模板
    try:
        return render_template(f"modals/{modal_name}.html", player=player, game=game)
    except Exception:
        # 如果模板不存在，返回占位内容
        return f"<h3>{modal_name.title()}</h3><p>功能开发中...</p>"


if __name__ == "__main__":
    print("=== 修仙世界引擎 Web UI (优化版) ===")
    print("访问 http://localhost:5001 开始游戏")
    print("使用 Ctrl+C 停止服务器")
    print("=====================================")

    # 确保存档目录存在
    os.makedirs("saves", exist_ok=True)

    # 启动服务器
    app.run(debug=True, host="0.0.0.0", port=5001)
