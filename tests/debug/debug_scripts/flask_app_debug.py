#!/usr/bin/env python3
"""
测试脚本3：Flask应用测试
"""

import sys
import os
from pathlib import Path
import json

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("🌐 修仙世界引擎 - Flask应用测试")
print("=" * 60)

test_results = {
    "flask_app": False,
    "routes": {},
    "blueprints": {},
    "errors": []
}

try:
    # 尝试导入和创建Flask应用
    print("\n1. 测试Flask应用初始化...")
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['FLASK_SECRET_KEY'] = 'test_secret_key'
    
    from run_web_ui_v2 import XianxiaWebServer
    
    server = XianxiaWebServer()
    app = server.app
    
    if app is not None:
        print("✅ Flask应用创建成功")
        test_results["flask_app"] = True
        
        # 2. 测试路由注册
        print("\n2. 检查路由注册:")
        
        expected_routes = [
            '/',
            '/welcome',
            '/intro',
            '/game',
            '/command',
            '/status',
            '/log',
            '/need_refresh',
            '/save_game',
            '/load_game',
            '/create_character',
            '/modal/<modal_name>',
            '/get_audio_list',
            '/sw.js'
        ]
        
        # 获取所有注册的路由
        registered_routes = []
        for rule in app.url_map.iter_rules():
            registered_routes.append(str(rule))
        
        for route in expected_routes:
            # 简化匹配（因为Flask的rule格式可能不同）
            route_base = route.split('<')[0] if '<' in route else route
            found = any(route_base in r for r in registered_routes)
            test_results["routes"][route] = found
            status = "✅" if found else "❌"
            print(f"{status} {route}")
            
        # 3. 测试蓝图注册
        print("\n3. 检查蓝图注册:")
        expected_blueprints = ['lore', 'character', 'intel']
        
        for bp_name in expected_blueprints:
            registered = bp_name in app.blueprints
            test_results["blueprints"][bp_name] = registered
            status = "✅" if registered else "❌"
            print(f"{status} {bp_name}")
            
        # 4. 测试客户端
        print("\n4. 测试基本请求:")
        with app.test_client() as client:
            # 测试首页重定向
            print("  测试 / -> /welcome 重定向...")
            response = client.get('/')
            if response.status_code == 302:  # 重定向
                print("  ✅ 首页重定向正常")
            else:
                print(f"  ❌ 首页状态码: {response.status_code}")
                test_results["errors"].append(f"首页状态码异常: {response.status_code}")
            
            # 测试静态文件路径
            print("  测试静态文件路径...")
            response = client.get('/static/css/ink_style.css')
            if response.status_code in [200, 404]:  # 200成功，404文件不存在
                print(f"  ✅ 静态文件路径可访问 (状态: {response.status_code})")
            else:
                print(f"  ❌ 静态文件路径异常: {response.status_code}")
                
    else:
        print("❌ Flask应用创建失败")
        test_results["errors"].append("Flask应用创建失败")
        
except Exception as e:
    print(f"\n❌ 测试过程中出错: {e}")
    test_results["errors"].append(f"初始化错误: {str(e)}")
    
    # 尝试获取更详细的错误信息
    import traceback
    error_detail = traceback.format_exc()
    print("\n详细错误信息:")
    print(error_detail)
    test_results["errors"].append(f"详细错误: {error_detail}")

# 总结
print("\n" + "=" * 60)
print("📊 测试总结:")

if test_results["flask_app"]:
    route_count = len(test_results["routes"])
    route_ok = sum(1 for v in test_results["routes"].values() if v)
    bp_count = len(test_results["blueprints"])
    bp_ok = sum(1 for v in test_results["blueprints"].values() if v)
    
    print(f"Flask应用: ✅")
    print(f"路由注册: {route_ok}/{route_count}")
    print(f"蓝图注册: {bp_ok}/{bp_count}")
else:
    print(f"Flask应用: ❌")

if test_results["errors"]:
    print(f"\n错误数: {len(test_results['errors'])}")
    for error in test_results["errors"]:
        print(f"  - {error}")

# 保存结果
results_file = PROJECT_ROOT / "tests" / "debug" / "flask_test_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(test_results, f, indent=2, ensure_ascii=False)

print(f"\n详细结果已保存到: {results_file}")
print("=" * 60)
