#!/usr/bin/env python3
"""
快速测试水墨风格UI
"""

import subprocess
import time
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent.parent

def test_ui():
    print("=== 测试水墨风格UI ===")
    print("启动服务器...")
    
    # 启动Flask服务器
    flask_process = subprocess.Popen(
        [sys.executable, str(project_root / "entrypoints" / "run_web_ui_optimized.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("等待服务器启动...")
    time.sleep(3)
    
    print("\n测试页面:")
    print("1. 开始页面: http://localhost:5001/")
    print("2. 选择页面: http://localhost:5001/choose")
    print("3. 抽卡页面: http://localhost:5001/roll?mode=random")
    print("4. 游戏页面: http://localhost:5001/game")
    
    print("\n按 Ctrl+C 退出测试...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止服务器...")
        flask_process.terminate()
        flask_process.wait()
        print("测试结束")

if __name__ == "__main__":
    test_ui()
