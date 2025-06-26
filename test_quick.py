#!/usr/bin/env python3
"""
快速测试角色创建系统
"""

import subprocess
import sys
import time
import requests
import json

def check_server():
    """检查服务器是否运行"""
    try:
        response = requests.get("http://localhost:5001/need_refresh", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_roll_api():
    """测试角色抽卡API"""
    print("\n测试 /api/roll 接口...")
    
    try:
        response = requests.post(
            "http://localhost:5001/api/roll",
            json={"mode": "random"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ API返回错误状态码: {response.status_code}")
            return False
            
        data = response.json()
        
        if not data.get("success"):
            print(f"❌ API返回失败")
            return False
            
        character = data.get("character", {})
        
        # 显示生成的角色
        print("\n✅ 成功生成角色:")
        print(f"  姓名: {character.get('name', '未知')}")
        print(f"  性别: {character.get('gender', '未知')}")
        print(f"  背景: {character.get('background', '未知')}")
        
        attrs = character.get('attributes', {})
        print("  属性:")
        for attr in ['constitution', 'comprehension', 'spirit', 'luck']:
            value = attrs.get(attr, '缺失')
            status = "✅" if attr in attrs else "❌"
            print(f"    {status} {attr}: {value}")
            
        destiny = data.get('destiny', {})
        if destiny:
            print(f"  命格: {destiny.get('name', '未知')} - {destiny.get('description', '')}")
        
        # 检查是否所有必需字段都存在
        missing_fields = []
        for field in ['name', 'gender', 'background', 'attributes']:
            if field not in character:
                missing_fields.append(field)
                
        for attr in ['constitution', 'comprehension', 'spirit', 'luck']:
            if attr not in attrs:
                missing_fields.append(f"attributes.{attr}")
                
        if missing_fields:
            print(f"\n❌ 缺少字段: {', '.join(missing_fields)}")
            return False
        else:
            print("\n✅ 所有必需字段都存在!")
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("====================")
    print("角色创建系统测试")
    print("====================")
    
    # 检查服务器
    print("\n检查服务器状态...")
    if not check_server():
        print("❌ 服务器未运行!")
        print("\n请先启动服务器:")
        print("  python run.py")
        sys.exit(1)
    
    print("✅ 服务器正在运行")
    
    # 测试API
    success = test_roll_api()
    
    if success:
        print("\n" + "="*40)
        print("✅ API测试通过!")
        print("\n现在请手动测试:")
        print("1. 访问 http://localhost:5001")
        print("2. 点击 '开始游戏'")
        print("3. 在角色创建页面点击 '随机生成'")
        print("4. 验证所有属性正确显示")
        print("5. 验证命格显示（如果有）")
        print("6. 点击 '确认创建'")
        print("7. 验证成功进入游戏")
        print("="*40)
    else:
        print("\n❌ API测试失败，请检查代码!")
        
if __name__ == "__main__":
    main()
