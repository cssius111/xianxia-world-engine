import threading
import webbrowser
from flask import Flask, render_template, request, jsonify
from xwe.core.game_core import GameCore

app = Flask(__name__, static_folder='static', template_folder='templates')

game = GameCore()
# 默认角色名
game.start_new_game()

# 存储日志
logs = []


def flush_output():
    for line in game.get_output():
        logs.append(line)


@app.route('/')
def index():
    flush_output()
    return render_template('game.html')


@app.route('/status')
def status():
    flush_output()
    return jsonify(game.game_state.to_dict())


@app.route('/log')
def log():
    flush_output()
    return jsonify({'logs': logs[-200:]})


@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    cmd = data.get('command', '')
    if cmd:
        game.process_command(cmd)
    flush_output()
    return jsonify({'logs': logs[-200:]})


def open_browser():
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run()
