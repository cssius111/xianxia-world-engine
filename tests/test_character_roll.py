#!/usr/bin/env python3
"""
测试角色抽卡API
验证返回的数据结构是否正确
"""

import json
import requests
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_roll_api():
    """测试/api/roll接口"""
    print("测试角色抽卡API...")
    
    # 发送请求
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
        
        # 验证响应结构
        if not data.get("success"):
            print(f"❌ API返回失败: {data}")
            return False
            
        character = data.get("character", {})
        
        # 验证必需字段
        required_fields = ["name", "gender", "background", "attributes"]
        for field in required_fields:
            if field not in character:
                print(f"❌ 缺少必需字段: {field}")
                return False
                
        # 验证属性
        attributes = character.get("attributes", {})
        expected_attrs = ["constitution", "comprehension", "spirit", "luck"]
        for attr in expected_attrs:
            if attr not in attributes:
                print(f"❌ 缺少属性: {attr}")
                return False
            value = attributes[attr]
            if not isinstance(value, (int, float)) or value < 1 or value > 10:
                print(f"❌ 属性值无效: {attr}={value}")
                return False
                
        # 验证性别
        if character["gender"] not in ["male", "female"]:
            print(f"❌ 无效的性别: {character['gender']}")
            return False
            
        # 验证背景
        if character["background"] not in ["poor", "merchant", "scholar", "martial"]:
            print(f"❌ 无效的背景: {character['background']}")
            return False
            
        # 验证命格
        destiny = data.get("destiny")
        if destiny:
            if not destiny.get("name"):
                print(f"❌ 命格缺少名称")
                return False
                
        print("✅ 角色抽卡API测试通过!")
        print(f"生成的角色:")
        print(f"  姓名: {character['name']}")
        print(f"  性别: {character['gender']}")
        print(f"  背景: {character['background']}")
        print(f"  属性: {json.dumps(attributes, ensure_ascii=False)}")
        if destiny:
            print(f"  命格: {destiny.get('name', '未知')}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行 (http://localhost:5001)")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_multiple_rolls(n=5):
    """测试多次抽卡，确保属性完整"""
    print(f"\n测试{n}次连续抽卡...")
    
    success_count = 0
    for i in range(n):
        print(f"\n第{i+1}次抽卡:")
        if test_roll_api():
            success_count += 1
            
    print(f"\n总结: {success_count}/{n} 次成功")
    return success_count == n

if __name__ == "__main__":
    print("=" * 50)
    print("角色抽卡API测试")
    print("=" * 50)
    
    # 单次测试
    if test_roll_api():
        # 多次测试
        test_multiple_rolls()
    else:
        print("\n请先启动服务器: python run.py")
