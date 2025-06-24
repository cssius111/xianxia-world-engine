#!/usr/bin/env python3
"""
修仙世界引擎 - 统一启动器
简化版本，保留核心功能
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from xwe.core.data_loader import DataLoader
import logging
from pathlib import Path
from datetime import datetime
import os
import sys

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Flask应用配置
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = 'xianxia_world_secret_key_2025'
app.config['JSON_AS_ASCII'] = False

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("XianxiaEngine")

# 确保必要目录存在
for directory in ["saves", "logs"]:
    Path(directory).mkdir(parents=True, exist_ok=True)

# 初始化数据加载器
data_loader = DataLoader()

# ========== 页面路由 ==========

@app.route("/")
def index():
    """首页"""
    return redirect(url_for("start_screen"))

@app.route("/start")
def start_screen():
    """开始页面"""
    save_exists = Path("saves/autosave.json").exists()
    return render_template(
        "screens/start_screen.html",
        save_exists=save_exists,
        build_time=datetime.now().strftime("%Y.%m.%d")
    )

@app.route("/intro")
def intro_screen():
    """角色创建页面"""
    dev_mode = request.args.get('mode') == 'dev'
    return render_template("intro_optimized.html", dev_mode=dev_mode)

@app.route("/game")
def game_screen():
    """游戏主界面"""
    # 提供默认数据
    player_data = {
        'name': session.get('player_name', '无名侠客'),
        'attributes': {
            'realm_name': '炼气期',
            'realm_level': 1,
            'current_health': 100,
            'max_health': 100,
            'current_mana': 50,
            'max_mana': 50,
            'current_stamina': 100,
            'max_stamina': 100,
            'attack_power': 10,
            'defense': 5,
        },
        'extra_data': {}
    }
    
    return render_template(
        "game_enhanced_optimized_v2.html",
        player=player_data,
        location='青云城',
        buffs=[],
        special_status=[],
        is_new_session=True,
        dev_mode=request.args.get('mode') == 'dev'
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
        'status', 'inventory', 'cultivation', 'achievement',
        'exploration', 'map', 'quest', 'save', 'load',
        'help', 'settings', 'exit'
    ]
    
    if modal_name not in allowed_modals:
        return "无效的模态框", 404
        
    try:
        return render_template(f"modals/{modal_name}.html")
    except:
        return f"<h3>{modal_name.title()}</h3><p>功能开发中...</p>"

# ========== API路由 ==========

@app.route("/create_character", methods=["POST"])
def create_character():
    """创建角色"""
    data = request.get_json()
    
    # 保存角色名到会话
    if data and 'name' in data:
        session['player_name'] = data.get('name', '无名侠客')
        logger.info(f"创建角色: {session['player_name']}")
    
    return jsonify({
        "success": True,
        "narrative": f"{data.get('name', '无名侠客')} 的修仙之旅由此开始。"
    })

@app.route("/command", methods=["POST"])
def process_command():
    """处理游戏命令"""
    data = request.get_json()
    command = data.get("command", "")
    
    # 模拟响应
    responses = {
        "帮助": "可用命令：查看状态、修炼、探索、背包、地图",
        "查看状态": f"【{session.get('player_name', '无名侠客')}】\n境界：炼气期一层\n生命：100/100\n法力：50/50",
        "修炼": "你开始打坐修炼，感受天地灵气缓缓流入体内...",
        "探索": "你在青云城中漫步，发现了一家丹药铺...",
        "背包": "你的背包中有：\n- 灵石 x10\n- 回气丹 x3",
        "地图": "当前位置：青云城\n可去往：城主府、丹药铺、任务大厅、城外"
    }
    
    result = responses.get(command, f"你输入了：{command}")
    logger.info(f"处理命令: {command}")
    
    return jsonify({"success": True, "result": result})

@app.route("/status")
def get_status():
    """获取游戏状态"""
    return jsonify({
        "player": {
            "name": session.get('player_name', '无名侠客'),
            "attributes": {
                "realm_name": "炼气期",
                "realm_level": 1,
                "current_health": 100,
                "max_health": 100,
                "current_mana": 50,
                "max_mana": 50
            }
        },
        "location": "青云城",
        "gold": 100
    })

@app.route("/log")
def get_log():
    """获取游戏日志"""
    return jsonify({
        "logs": [
            "欢迎来到修仙世界！",
            "你出生在青云城，开始了修仙之旅。",
            "输入'帮助'查看可用命令。"
        ]
    })

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
        from xwe.core.nlp import LLMClient
        import json as pyjson

        llm = LLMClient()
        result = llm.chat(text)

        try:
            parsed = pyjson.loads(result)
        except Exception:
            parsed = {"result": result}

        return jsonify({"success": True, "data": parsed})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ========== 工具路由 ==========

@app.route('/favicon.ico')
def favicon():
    """避免favicon 404错误"""
    return '', 204

@app.route("/sw.js")
def service_worker():
    """Service Worker"""
    try:
        return app.send_static_file('sw.js'), 200, {
            'Content-Type': 'application/javascript',
            'Cache-Control': 'no-cache'
        }
    except:
        return '', 404

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
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    
    print("=" * 60)
    print("🎮 修仙世界引擎")
    print("=" * 60)
    print(f"🌐 访问地址: http://localhost:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print(f"📝 日志目录: {Path('logs').absolute()}")
    print(f"💾 存档目录: {Path('saves').absolute()}")
    print("=" * 60)
    print("使用 Ctrl+C 停止服务器")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == '__main__':
    main()
