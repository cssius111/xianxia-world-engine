#!/usr/bin/env python3
"""快速修复脚本 - 跳过可能有问题的初始化"""
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# 临时禁用 NLP 和其他可能阻塞的功能
os.environ['DISABLE_NLP'] = 'true'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

print("=== 快速启动（跳过可能阻塞的组件）===\n")

try:
    # 直接使用 Flask，绕过复杂的初始化
    from flask import Flask
    from pathlib import Path
    
    project_root = Path(__file__).resolve().parent
    static_folder = project_root / "src" / "web" / "static"
    template_folder = project_root / "src" / "web" / "templates"
    
    app = Flask(__name__, 
                static_folder=str(static_folder), 
                template_folder=str(template_folder))
    app.secret_key = 'test_secret'
    
    @app.route('/')
    def index():
        return '''
        <h1>修仙世界引擎 - 快速启动模式</h1>
        <p>服务器正在运行！</p>
        <p>这是一个简化版本，跳过了可能导致阻塞的组件。</p>
        <ul>
            <li><a href="/test">测试页面</a></li>
            <li><a href="/intro">游戏介绍页面</a></li>
        </ul>
        '''
    
    @app.route('/test')
    def test():
        return '<h2>测试页面</h2><p>一切正常！</p>'
    
    # 尝试加载模板
    try:
        from flask import render_template
        
        @app.route('/intro')
        def intro():
            return render_template('intro_optimized.html')
    except:
        @app.route('/intro')
        def intro():
            return '<h2>模板加载失败</h2><p>但服务器正在运行。</p>'
    
    print("启动简化版服务器...")
    print("访问: http://127.0.0.1:5007")
    print("\n如果这个能运行，说明问题出在复杂的初始化过程中。")
    print("按 Ctrl+C 停止\n")
    
    app.run(host='127.0.0.1', port=5007, debug=True, use_reloader=False)
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
