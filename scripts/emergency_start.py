#!/usr/bin/env python3
"""
修仙世界引擎 - 紧急启动脚本
如果正常启动失败，使用此脚本
"""

import sys
import os
from pathlib import Path

# 强制设置所有必要的路径
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['PYTHONUNBUFFERED'] = '1'

print("=" * 60)
print("🚨 修仙世界引擎 - 紧急启动模式")
print("=" * 60)

try:
    # 尝试正常导入
    from src.app import create_app
    print("✅ 成功导入应用")
    
    app = create_app()
    print(f"✅ Flask 应用创建成功")
    print(f"   - 模板目录: {app.template_folder}")
    print(f"   - 静态目录: {app.static_folder}")
    
    # 添加一个测试路由
    @app.route('/test')
    def test():
        return '''
        <h1>✅ 服务器运行正常！</h1>
        <p>如果您能看到这个页面，说明 Flask 基本功能正常。</p>
        <p>测试其他页面：</p>
        <ul>
            <li><a href="/">主页</a></li>
            <li><a href="/intro">游戏介绍</a></li>
            <li><a href="/game">游戏界面</a></li>
        </ul>
        <p>如果其他页面无法访问，请检查模板文件。</p>
        '''
    
    print("\n🎮 正在启动服务器...")
    print(f"🌐 访问地址: http://localhost:5001")
    print(f"🧪 测试地址: http://localhost:5001/test")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    # 启动应用
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    
except Exception as e:
    print(f"\n❌ 启动失败: {e}")
    print("\n尝试最小化启动...")
    
    # 如果失败，创建最小化应用
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def emergency():
            return '''
            <h1>⚠️ 紧急模式</h1>
            <p>主应用启动失败，当前运行在最小化模式。</p>
            <p>错误信息：{}</p>
            <p>请检查：</p>
            <ol>
                <li>是否所有依赖都已安装</li>
                <li>Python 路径是否正确</li>
                <li>模板文件是否存在</li>
            </ol>
            '''.format(str(e))
        
        print("✅ 最小化应用创建成功")
        print(f"🌐 访问地址: http://localhost:5001")
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    except Exception as e2:
        print(f"❌ 完全失败: {e2}")
        print("\n请运行以下命令进行修复：")
        print("1. pip install flask")
        print("2. pip install -r requirements.txt")
        print("3. python diagnose_flask.py")
