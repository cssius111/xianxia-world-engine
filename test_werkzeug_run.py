#!/usr/bin/env python3
"""使用 werkzeug 直接启动的测试脚本"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=== Werkzeug 直接启动测试 ===")

try:
    from werkzeug.serving import run_simple
    from src.app import create_app
    
    app = create_app()
    
    print("使用 werkzeug 启动服务器...")
    print("访问: http://127.0.0.1:5004")
    
    run_simple('127.0.0.1', 5004, app, use_reloader=False, use_debugger=True)
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
