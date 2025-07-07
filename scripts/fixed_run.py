#!/usr/bin/env python3
"""修复版启动脚本 - 禁用可能阻塞的组件"""
import sys
import os
from pathlib import Path

# 设置环境变量以禁用可能阻塞的功能
os.environ['DISABLE_NLP'] = 'true'
os.environ['USE_SIMPLE_COMMAND_ROUTER'] = 'true'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=== 修复版启动脚本 ===")
print("已禁用：")
print("- NLP 处理器")
print("- 复杂的命令路由")
print("\n")

# 修改命令路由器的初始化
print("1. 修补命令路由器...")
try:
    # 创建一个简单的命令路由器替代品
    import src.xwe.core.command_router as cmd_router_module
    
    class SimpleCommandRouter:
        def __init__(self, use_nlp=False):
            self.use_nlp = False
            print("   使用简单命令路由器（无 NLP）")
    
    # 替换原来的 CommandRouter
    cmd_router_module.CommandRouter = SimpleCommandRouter
    print("   ✅ 命令路由器已修补")
except Exception as e:
    print(f"   ⚠️  无法修补命令路由器: {e}")

# 启动应用
print("\n2. 启动应用...")
try:
    from src.app import create_app
    app = create_app()
    
    print("   ✅ 应用创建成功")
    print("\n3. 启动服务器...")
    print("   访问: http://127.0.0.1:5008")
    print("   按 Ctrl+C 停止\n")
    
    app.run(host='127.0.0.1', port=5008, debug=True, use_reloader=False)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n如果仍然失败，请运行：")
    print("1. python check_ports.py  # 检查端口")
    print("2. python diagnose_nlp.py  # 检查 NLP")
    print("3. python quick_start.py  # 最简启动")
