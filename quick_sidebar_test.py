#!/usr/bin/env python3
"""
快速侧边栏健康检查脚本
检查API端点和关键功能是否正常工作
"""

import requests
import json
import time
from datetime import datetime

def check_server():
    """检查服务器是否运行"""
    try:
        response = requests.get('http://localhost:5001', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_api_endpoints():
    """检查API端点健康状态"""
    endpoints = [
        ('/status', 'GET'),
        ('/api/cultivation/status', 'GET'),
        ('/api/achievements', 'GET'),
        ('/api/map', 'GET'),
        ('/api/quests', 'GET'),
        ('/api/intel', 'GET'),
        ('/api/player/stats/detailed', 'GET'),
    ]
    
    results = []
    for endpoint, method in endpoints:
        try:
            url = f'http://localhost:5001{endpoint}'
            response = requests.request(method, url, timeout=5)
            results.append({
                'endpoint': endpoint,
                'status': response.status_code,
                'ok': response.status_code in [200, 201, 204],
                'data': response.json() if response.status_code == 200 else None
            })
        except Exception as e:
            results.append({
                'endpoint': endpoint,
                'status': 'ERROR',
                'ok': False,
                'error': str(e)
            })
    
    return results

def main():
    print("🏥 修仙游戏侧边栏健康检查")
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查服务器
    print("1. 检查服务器状态...")
    if not check_server():
        print("❌ 服务器未运行！请先运行: python3 start_web.py")
        return
    print("✅ 服务器运行正常")
    print()
    
    # 检查API端点
    print("2. 检查API端点...")
    api_results = check_api_endpoints()
    
    working_count = 0
    for result in api_results:
        status_icon = "✅" if result['ok'] else "❌"
        print(f"   {status_icon} {result['endpoint']} - {result['status']}")
        if result['ok']:
            working_count += 1
    
    print()
    print(f"API健康度: {working_count}/{len(api_results)} ({working_count/len(api_results)*100:.1f}%)")
    
    # 生成报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'server_status': 'running',
        'api_health': f"{working_count}/{len(api_results)}",
        'api_details': api_results,
        'sidebar_functional': working_count >= 5  # 至少5个API正常才算功能正常
    }
    
    # 保存报告
    with open('sidebar_health_check.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print()
    print("📊 详细报告已保存到: sidebar_health_check.json")
    
    # 总结
    print()
    print("🎯 总结:")
    if working_count == len(api_results):
        print("   ✅ 侧边栏所有功能API正常工作")
    elif working_count >= 5:
        print("   ⚠️  侧边栏基本功能正常，但有部分API异常")
    else:
        print("   ❌ 侧边栏功能存在严重问题，需要修复")

if __name__ == '__main__':
    main()
