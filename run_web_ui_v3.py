import threading
import webbrowser
from flask import Flask, render_template, request, jsonify
from main_v3_data_driven import DataDrivenGameCore

app = Flask(__name__, static_folder='static', template_folder='templates')

# 创建数据驱动版本的游戏核心
game = DataDrivenGameCore()
# 启动新游戏
game.start_new_game()

# 日志列表
logs = []
# 前端刷新标记
state_changed = True


def flush_output():
    """刷新并收集游戏输出"""
    global state_changed
    changed = False
    for line in game.get_output():
        logs.append(line)
        changed = True
    if changed:
        state_changed = True


@app.route('/')
def index():
    """主页面"""
    flush_output()
    state = game.game_state.to_dict()
    player = game.game_state.player
    buffs = []
    if player and hasattr(player, 'status_effects'):
        buffs = player.status_effects.get_status_summary()
    return render_template(
        'game.html',
        player=state.get('player'),
        logs=logs[-200:],
        buffs=buffs,
        special_status=[],
    )


@app.route('/status')
def status():
    """返回当前状态"""
    flush_output()
    return jsonify(game.game_state.to_dict())


@app.route('/log')
def log():
    """返回最新日志"""
    flush_output()
    return jsonify({'logs': logs[-200:]})


@app.route('/command', methods=['POST'])
def command():
    """处理指令"""
    global state_changed
    data = request.get_json()
    cmd = data.get('command', '')
    if cmd:
        game.process_command(cmd)
        state_changed = True
    flush_output()
    return jsonify({'logs': logs[-200:]})


@app.route('/need_refresh')
def need_refresh():
    """检查前端是否需要刷新"""
    global state_changed
    flush_output()
    if state_changed:
        state_changed = False
        return jsonify({'refresh': True})
    return jsonify({'refresh': False})


def open_browser():
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run()
