#!/usr/bin/env python3
"""
最终解决方案 - 智能启动脚本
自动检测并修复常见的 Flask 启动问题
"""
import sys
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

print("""
╔════════════════════════════════════════╗
║        修仙世界引擎 - 智能启动器       ║
╚════════════════════════════════════════╝
""")

# 1. 设置环境变量
print("1. 配置环境...")
env_vars = {
    'DISABLE_NLP': 'true',
    'USE_NLP': 'false',
    'FLASK_ENV': 'development',
    'FLASK_DEBUG': '1',
    'WERKZEUG_RUN_MAIN': 'true'  # 防止 reloader 导致的双重初始化
}

for key, value in env_vars.items():
    os.environ[key] = value
    print(f"   ✓ {key}={value}")

# 2. 检查端口
print("\n2. 检查端口可用性...")
import socket
port = 5001
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', port))
sock.close()

if result == 0:
    print(f"   ⚠️  端口 {port} 已被占用")
    print("   正在查找可用端口...")
    for p in range(5002, 5010):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', p))
        sock.close()
        if result != 0:
            port = p
            print(f"   ✓ 使用端口 {port}")
            break
else:
    print(f"   ✓ 端口 {port} 可用")

# 3. 修改 CommandRouter 的初始化
print("\n3. 应用运行时修补...")
try:
    # 创建一个模拟的 CommandRouter
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "command_router_patch", 
        PROJECT_ROOT / "src" / "xwe" / "core" / "command_router.py"
    )
    cmd_module = importlib.util.module_from_spec(spec)
    
    # 修补初始化方法
    original_init = None
    if hasattr(cmd_module, 'CommandRouter'):
        original_init = cmd_module.CommandRouter.__init__
    
    def patched_init(self, use_nlp=False):  # 强制禁用 NLP
        self.routes = []
        self.current_context = "exploration"
        self.use_nlp = False
        self.nlp_processor = None
        self._nlp_handler = None
        self._init_default_routes()
        self.command_handler_map = {
            "探索": "explore",
            "修炼": "cultivate",
            "查看状态": "status",
            "打开背包": "inventory",
            "前往": "move",
            "使用物品": "use_item",
            "使用": "use_item",
            "交谈": "talk",
            "对话": "talk",
            "交易": "trade",
            "攻击": "attack",
            "防御": "defend",
            "逃跑": "flee",
            "突破": "breakthrough",
            "保存": "save",
            "退出": "quit",
            "帮助": "help",
            "未知": "unknown",
        }
        print("   ✓ 命令路由器已修补（禁用 NLP）")
    
    # 应用修补
    sys.modules['src.xwe.core.command_router'] = cmd_module
    if hasattr(cmd_module, 'CommandRouter'):
        cmd_module.CommandRouter.__init__ = patched_init
    
except Exception as e:
    print(f"   ⚠️  修补失败: {e}")
    print("   将通过环境变量禁用 NLP")

# 4. 启动应用
print("\n4. 启动 Flask 应用...")
print(f"\n{'='*50}")
print(f"服务器地址: http://127.0.0.1:{port}")
print("按 Ctrl+C 停止服务器")
print(f"{'='*50}\n")

try:
    from src.app import create_app
    app = create_app()
    
    # 直接运行，不使用 reloader
    app.run(
        host='127.0.0.1', 
        port=port, 
        debug=True, 
        use_reloader=False,
        threaded=False
    )
    
except KeyboardInterrupt:
    print("\n\n服务器已停止")
except Exception as e:
    print(f"\n❌ 启动失败: {e}")
    print("\n可能的解决方案：")
    print("1. 运行 'python quick_start.py' 测试最简版本")
    print("2. 运行 'python test_minimal_flask.py' 测试 Flask 本身")
    print("3. 检查日志文件 logs/app.log")
    import traceback
    traceback.print_exc()
