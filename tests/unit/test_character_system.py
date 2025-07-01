"""
测试角色创建系统
使用 pytest 运行: pytest tests/test_character_system.py -v
"""

import json
import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径，便于导入 scripts 模块
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.dev.gen_character import gen_random, gen_template


class TestCharacterGeneration:
    """测试角色生成函数"""
    
    def test_gen_random_structure(self):
        """测试随机生成的角色数据结构"""
        character = gen_random()
        
        # 验证必需字段
        assert "name" in character
        assert "age" in character
        assert "spiritual_root" in character
        assert "attributes" in character
        
        # 验证属性
        attrs = character["attributes"]
        expected_attrs = [
            "comprehension", "constitution", "fortune", "charisma",
            "willpower", "perception", "destiny", "opportunity"
        ]
        for attr in expected_attrs:
            assert attr in attrs
            assert 1 <= attrs[attr] <= 10
            
    def test_gen_template_sword(self):
        """测试剑修模板生成"""
        character = gen_template("sword")
        
        assert character["spiritual_root"] in ["金", "火", "雷"]
        # 剑修应该有更高的悟性
        assert character["attributes"]["comprehension"] >= 3
        assert character["attributes"]["perception"] >= 2
        
    def test_gen_template_body(self):
        """测试体修模板生成"""
        character = gen_template("body")
        
        assert character["spiritual_root"] in ["土", "金", "木"]
        # 体修应该有更高的根骨
        assert character["attributes"]["constitution"] >= 3
        assert character["attributes"]["willpower"] >= 2


class TestAttributeMapping:
    """测试属性映射逻辑"""
    
    def test_attribute_mapping(self):
        """测试后端属性到前端属性的映射"""
        # 模拟后端生成的属性
        backend_attrs = {
            "comprehension": 6,
            "constitution": 7,
            "fortune": 8,
            "charisma": 5,
            "willpower": 9,
            "perception": 4,
            "destiny": 3,
            "opportunity": 6
        }
        
        # 应用映射逻辑（与run.py中的逻辑相同）
        frontend_attrs = {
            "constitution": backend_attrs.get("constitution", 5),
            "comprehension": backend_attrs.get("comprehension", 5),
            "spirit": backend_attrs.get("perception", backend_attrs.get("willpower", 5)),
            "luck": backend_attrs.get("fortune", backend_attrs.get("opportunity", 5))
        }
        
        # 验证映射结果
        assert frontend_attrs["constitution"] == 7
        assert frontend_attrs["comprehension"] == 6
        assert frontend_attrs["spirit"] == 4  # 使用perception
        assert frontend_attrs["luck"] == 8  # 使用fortune
        
    def test_attribute_mapping_with_missing_values(self):
        """测试缺少某些属性时的映射"""
        # 缺少perception的情况
        backend_attrs = {
            "comprehension": 6,
            "constitution": 7,
            "willpower": 9,
            "opportunity": 6
        }
        
        frontend_attrs = {
            "constitution": backend_attrs.get("constitution", 5),
            "comprehension": backend_attrs.get("comprehension", 5),
            "spirit": backend_attrs.get("perception", backend_attrs.get("willpower", 5)),
            "luck": backend_attrs.get("fortune", backend_attrs.get("opportunity", 5))
        }
        
        assert frontend_attrs["spirit"] == 9  # 使用willpower作为备选
        assert frontend_attrs["luck"] == 6  # 使用opportunity作为备选


class TestDataStructure:
    """测试完整的数据结构"""
    
    def test_roll_result_structure(self):
        """测试抽卡结果的数据结构"""
        # 模拟API返回的数据结构
        character = gen_random()
        
        # 映射属性
        backend_attrs = character.get("attributes", {})
        frontend_attrs = {
            "constitution": backend_attrs.get("constitution", 5),
            "comprehension": backend_attrs.get("comprehension", 5),
            "spirit": backend_attrs.get("perception", backend_attrs.get("willpower", 5)),
            "luck": backend_attrs.get("fortune", backend_attrs.get("opportunity", 5))
        }
        
        # 构建完整结果
        roll_result = {
            "name": character.get("name", "无名侠客"),
            "gender": "male",  # 模拟随机性别
            "background": "poor",  # 模拟随机背景
            "attributes": frontend_attrs,
            "destiny": {
                "id": "MORTAL_FATE",
                "name": "凡命",
                "description": "平凡命格，修炼之路充满艰辛"
            }
        }
        
        # 验证结构完整性
        assert "name" in roll_result
        assert "gender" in roll_result
        assert "background" in roll_result
        assert "attributes" in roll_result
        assert "destiny" in roll_result
        
        # 验证属性完整性
        attrs = roll_result["attributes"]
        for attr in ["constitution", "comprehension", "spirit", "luck"]:
            assert attr in attrs
            assert isinstance(attrs[attr], (int, float))
            assert 1 <= attrs[attr] <= 10


if __name__ == "__main__":
    # 如果直接运行，执行简单测试
    print("运行角色生成测试...")
    
    # 测试随机生成
    char = gen_random()
    print(f"随机角色: {json.dumps(char, ensure_ascii=False, indent=2)}")
    
    # 测试属性映射
    backend_attrs = char.get("attributes", {})
    frontend_attrs = {
        "constitution": backend_attrs.get("constitution", 5),
        "comprehension": backend_attrs.get("comprehension", 5),
        "spirit": backend_attrs.get("perception", backend_attrs.get("willpower", 5)),
        "luck": backend_attrs.get("fortune", backend_attrs.get("opportunity", 5))
    }
    print(f"\n映射后的前端属性: {json.dumps(frontend_attrs, ensure_ascii=False, indent=2)}")
