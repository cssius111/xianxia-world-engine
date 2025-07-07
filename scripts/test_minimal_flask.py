#!/usr/bin/env python3
"""最简单的 Flask 测试"""
from flask import Flask

print("=== 最简 Flask 测试 ===")

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Flask 正在运行！</h1><p>如果你看到这个页面，说明 Flask 本身没有问题。</p>'

if __name__ == '__main__':
    print("启动最简 Flask 应用...")
    print("访问: http://127.0.0.1:5005")
    app.run(host='127.0.0.1', port=5005, debug=True)
