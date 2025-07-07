#!/usr/bin/env python3
"""简化的启动脚本，用于调试"""
import sys
import os
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

print("=== 简化启动脚本 ===")
print(f"Python 版本: {sys.version}")
print(f"项目路径: {PROJECT_ROOT}")

try:
    print("\n1. 导入模块...")
    from src.app import create_app
    print("   ✅ 导入成功")
    
    print("\n2. 创建 Flask 应用...")
    app = create_app()
    print(f"   ✅ Flask 应用创建成功: {app}")
    
    print("\n3. 启动服务器...")
    print("   监听地址: http://127.0.0.1:5003")
    print("   按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 使用最简单的方式启动
    app.run(host='127.0.0.1', port=5003, debug=True, use_reloader=False)
    
except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
