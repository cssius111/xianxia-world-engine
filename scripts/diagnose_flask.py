#!/usr/bin/env python3
"""
修仙世界引擎 - Flask 应用诊断工具
"""

import sys
from pathlib import Path
import os
import socket
import requests
import json

# 设置项目路径
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def check_port(port=5001):
    """检查端口是否被占用"""
    print(f"\n1. 检查端口 {port} 状态...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f"✅ 端口 {port} 已开启（有服务在监听）")
        return True
    else:
        print(f"❌ 端口 {port} 未开启或无法连接")
        return False

def test_flask_routes():
    """测试 Flask 路由"""
    print("\n2. 测试 Flask 路由...")
    
    base_url = "http://localhost:5001"
    test_routes = [
        ("/", "主页"),
        ("/welcome", "欢迎页"),
        ("/intro", "介绍页"),
        ("/game", "游戏主界面"),
        ("/need_refresh", "刷新检查API"),
    ]
    
    working_routes = []
    failed_routes = []
    
    for route, name in test_routes:
        try:
            response = requests.get(base_url + route, timeout=5, allow_redirects=False)
            if response.status_code in [200, 302, 303, 307]:
                print(f"✅ {name} ({route}): {response.status_code}")
                working_routes.append((route, response.status_code))
                
                # 如果是重定向，显示目标
                if response.status_code in [302, 303, 307]:
                    print(f"   → 重定向到: {response.headers.get('Location', '未知')}")
            else:
                print(f"❌ {name} ({route}): {response.status_code}")
                failed_routes.append((route, response.status_code))
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} ({route}): 无法连接")
            failed_routes.append((route, "无法连接"))
        except Exception as e:
            print(f"❌ {name} ({route}): {str(e)}")
            failed_routes.append((route, str(e)))
    
    return working_routes, failed_routes

def check_flask_config():
    """检查 Flask 配置"""
    print("\n3. 检查 Flask 应用配置...")
    
    try:
        from src.app import create_app
        app = create_app()
        
        print(f"✅ Flask 应用创建成功")
        print(f"   - 模板目录: {app.template_folder}")
        print(f"   - 静态文件目录: {app.static_folder}")
        print(f"   - 秘钥设置: {'是' if app.secret_key else '否'}")
        
        # 检查目录是否存在
        if Path(app.template_folder).exists():
            print(f"   ✅ 模板目录存在")
            templates = list(Path(app.template_folder).glob("*.html"))
            print(f"   - 找到 {len(templates)} 个模板文件")
        else:
            print(f"   ❌ 模板目录不存在！")
            
        if Path(app.static_folder).exists():
            print(f"   ✅ 静态文件目录存在")
        else:
            print(f"   ❌ 静态文件目录不存在！")
            
        # 列出所有注册的路由
        print("\n   注册的路由:")
        for rule in app.url_map.iter_rules():
            if not rule.rule.startswith('/static'):
                print(f"   - {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
                
        return True
        
    except Exception as e:
        print(f"❌ Flask 应用配置检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_curl():
    """使用 curl 测试（备选方案）"""
    print("\n4. 使用 curl 命令测试...")
    print("请在终端运行以下命令测试连接：")
    print("curl -v http://localhost:5001/")
    print("curl -v http://localhost:5001/need_refresh")

def check_browser_console():
    """浏览器控制台检查指南"""
    print("\n5. 浏览器调试步骤：")
    print("1) 打开浏览器访问 http://localhost:5001")
    print("2) 按 F12 打开开发者工具")
    print("3) 查看 Console（控制台）标签是否有错误")
    print("4) 查看 Network（网络）标签：")
    print("   - 是否有失败的请求（红色）")
    print("   - 主页请求的状态码")
    print("   - 静态资源（CSS/JS）是否加载成功")

def create_test_server():
    """创建一个最小化的测试服务器"""
    print("\n6. 创建最小化测试服务器...")
    
    test_code = '''
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
'''
    

def check_logs():
    """检查日志文件"""
    print("\n7. 检查日志文件...")
    
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            print(f"找到 {len(log_files)} 个日志文件:")
            for log_file in sorted(log_files)[-3:]:  # 只显示最新的3个
                print(f"   - {log_file.name}")
                # 读取最后几行
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"     最后一条日志: {lines[-1].strip()}")
                except Exception as e:
                    print(f"     读取失败: {e}")
        else:
            print("❌ 没有找到日志文件")
    else:
        print("❌ 日志目录不存在")

def suggest_fixes():
    """建议的修复方案"""
    print("\n\n=== 🔧 建议的修复步骤 ===")
    print("""
1. **停止当前服务并重启**:
   - Ctrl+C 停止当前服务
   - 运行: python run.py --debug
   
2. **检查防火墙设置**:
   - 确保防火墙允许 5001 端口
   - Mac: 系统偏好设置 > 安全性与隐私 > 防火墙
   
3. **尝试不同的启动方式**:
   - 使用 python start_web.py
   - 使用 flask run --port 5001
   
4. **清理并重新安装**:
   - rm -rf __pycache__ src/__pycache__ src/*/__pycache__
   - pip install -r requirements.txt --force-reinstall
   
5. **检查环境变量**:
   - 确保 .env 文件存在
    - 设置 FLASK_ENV=development
    - 设置 FLASK_DEBUG=1
   
6. **查看完整错误信息**:
   - export FLASK_ENV=development
   - export FLASK_DEBUG=1
   - python run.py
""")

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 修仙世界引擎 - Flask 应用诊断")
    print("=" * 60)
    
    # 检查端口
    port_open = check_port()
    
    if port_open:
        # 测试路由
        working, failed = test_flask_routes()
        
        if not working and failed:
            print("\n⚠️  服务可能在运行但无法正常响应请求")
    
    # 检查配置
    check_flask_config()
    
    # 检查日志
    check_logs()
    
    # 其他建议
    test_with_curl()
    check_browser_console()
    create_test_server()
    
    # 修复建议
    suggest_fixes()
    
    print("\n" + "=" * 60)
    print("诊断完成！请根据上述信息定位问题。")
    print("=" * 60)

if __name__ == "__main__":
    main()
