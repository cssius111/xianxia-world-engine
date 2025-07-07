#!/usr/bin/env python3
"""诊断 Flask 启动问题"""
import sys
import threading
import signal
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=== Flask 启动诊断 ===\n")

# 设置信号处理
def signal_handler(sig, frame):
    print("\n收到中断信号，正在退出...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 检查当前线程
print("1. 当前线程信息:")
print(f"   主线程: {threading.current_thread().name}")
print(f"   活动线程数: {threading.active_count()}")
print(f"   线程列表: {[t.name for t in threading.enumerate()]}\n")

# 尝试启动 Flask
print("2. 尝试启动 Flask...")
try:
    from src.app import create_app
    app = create_app()
    
    # 在新线程中启动，避免阻塞
    def run_flask():
        print("   Flask 线程启动中...")
        app.run(host='127.0.0.1', port=5006, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # 等待一下让 Flask 启动
    time.sleep(2)
    
    print("\n3. 启动后的线程信息:")
    print(f"   活动线程数: {threading.active_count()}")
    print(f"   线程列表: {[t.name for t in threading.enumerate()]}")
    
    print("\n4. 测试连接...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5006))
    sock.close()
    
    if result == 0:
        print("   ✅ 成功连接到 Flask 服务器!")
        print("   访问: http://127.0.0.1:5006")
    else:
        print("   ❌ 无法连接到 Flask 服务器")
    
    print("\n按 Ctrl+C 退出...")
    while True:
        time.sleep(1)
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
