#!/usr/bin/env python3
"""
快速UI测试脚本
使用 FastAPI + Selenium 进行30秒端到端测试
"""

import time
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_basic_routes():
    """测试基础路由"""
    import requests
    
    base_url = "http://localhost:5001"
    
    print("测试基础路由...")
    
    # 测试首页
    try:
        resp = requests.get(f"{base_url}/", timeout=5)
        assert resp.status_code == 200
        print("✓ 首页加载成功")
    except Exception as e:
        print(f"✗ 首页加载失败: {e}")
        return False
    
    # 测试选择页面
    try:
        resp = requests.get(f"{base_url}/choose", timeout=5)
        assert resp.status_code == 200
        print("✓ 选择页面加载成功")
    except Exception as e:
        print(f"✗ 选择页面加载失败: {e}")
        return False
    
    # 测试抽卡页面
    try:
        resp = requests.get(f"{base_url}/roll?mode=random", timeout=5)
        assert resp.status_code == 200
        print("✓ 抽卡页面加载成功")
    except Exception as e:
        print(f"✗ 抽卡页面加载失败: {e}")
        return False
    
    # 测试抽卡API
    try:
        resp = requests.post(f"{base_url}/api/roll", 
                           json={"mode": "random"},
                           timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        assert "character" in data
        print("✓ 抽卡API正常")
    except Exception as e:
        print(f"✗ 抽卡API失败: {e}")
        return False
    
    return True


def run_smoke_test():
    """运行烟雾测试"""
    print("=== 修仙世界UI烟雾测试 ===")
    
    # 启动Flask服务器
    print("启动Flask服务器...")
    flask_cmd = [
        sys.executable,
        str(project_root / "entrypoints" / "run_web_ui_optimized.py")
    ]
    
    # 使用subprocess启动Flask
    flask_process = subprocess.Popen(
        flask_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(3)
    
    try:
        # 运行测试
        success = test_basic_routes()
        
        if success:
            print("\n✅ 所有测试通过!")
        else:
            print("\n❌ 测试失败!")
            
    finally:
        # 停止Flask服务器
        print("\n停止Flask服务器...")
        flask_process.terminate()
        flask_process.wait()
    
    return success


if __name__ == "__main__":
    # 运行测试
    success = run_smoke_test()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)
