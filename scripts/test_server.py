
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def test_home():
    return '<h1>测试服务器运行正常！</h1><p>如果你能看到这个，说明 Flask 基本功能正常。</p>'

@app.route('/test-json')
def test_json():
    return jsonify({"status": "ok", "message": "JSON API 正常"})

if __name__ == '__main__':
    print("启动测试服务器...")
    app.run(port=5002, debug=True)
