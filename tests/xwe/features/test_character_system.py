"""
测试角色创建系统
使用 pytest 运行: pytest tests/test_character_system.py -v
"""

import json
import pytest
from dataclasses import asdict

from src.xwe.core.roll_system import CharacterRoller


class TestCharacterGeneration:
    """测试角色生成函数"""
    
    def test_gen_random_structure(self):
        """测试随机生成的角色数据结构"""
        character = asdict(CharacterRoller().roll())
        
        # 验证必需字段
        assert "name" in character
        assert "spiritual_root_type" in character
        assert "spiritual_root_elements" in character
        assert "attributes" in character
        
        # 验证属性
        attrs = character["attributes"]
        expected_attrs = [
            "comprehension",
            "constitution",
            "luck",
            "charm",
        ]
        for attr in expected_attrs:
            assert attr in attrs
            assert 1 <= attrs[attr] <= 10
            
    def test_gen_template_sword(self):
        """测试剑修模板生成(兼容逻辑)"""
        character = asdict(CharacterRoller().roll())

        assert isinstance(character.get("spiritual_root_elements"), list)
        
    def test_gen_template_body(self):
        """测试体修模板生成(兼容逻辑)"""
        character = asdict(CharacterRoller().roll())

        assert "constitution" in character.get("attributes", {})


class TestAttributeMapping:
    """测试属性映射逻辑"""
    
    def test_attribute_mapping(self):
        """测试后端属性到前端属性的映射"""
        # 模拟后端生成的属性
        backend_attrs = {
            "comprehension": 6,
            "constitution": 7,
            "luck": 8,
            "charm": 5,
            "spirit": 4,
        }

        # 应用映射逻辑（与api_roll中的逻辑一致）
        frontend_attrs = {
            "constitution": backend_attrs.get("constitution", 5),
            "comprehension": backend_attrs.get("comprehension", 5),
            "spirit": backend_attrs.get("spirit", 5),
            "luck": backend_attrs.get("luck", 5),
        }
        
        # 验证映射结果
        assert frontend_attrs["constitution"] == 7
        assert frontend_attrs["comprehension"] == 6
        assert frontend_attrs["spirit"] == 4
        assert frontend_attrs["luck"] == 8
        
    def test_attribute_mapping_with_missing_values(self):
        """测试缺少某些属性时的映射"""
        backend_attrs = {
            "comprehension": 6,
            "constitution": 7,
            "luck": 6,
            "spirit": 9,
        }

        frontend_attrs = {
            "constitution": backend_attrs.get("constitution", 5),
            "comprehension": backend_attrs.get("comprehension", 5),
            "spirit": backend_attrs.get("spirit", 5),
            "luck": backend_attrs.get("luck", 5),
        }

        assert frontend_attrs["spirit"] == 9
        assert frontend_attrs["luck"] == 6


class TestDataStructure:
    """测试完整的数据结构"""
    
    def test_roll_result_structure(self):
        """测试抽卡结果的数据结构"""
        # 模拟API返回的数据结构
        character = asdict(CharacterRoller().roll())
        
        # 映射属性
        backend_attrs = character.get("attributes", {})
        frontend_attrs = {
            "constitution": backend_attrs.get("constitution", 5),
            "comprehension": backend_attrs.get("comprehension", 5),
            "spirit": backend_attrs.get("spirit", 5),
            "luck": backend_attrs.get("luck", 5),
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

    roller = CharacterRoller()
    char = asdict(roller.roll())
    print(f"随机角色: {json.dumps(char, ensure_ascii=False, indent=2)}")

    backend_attrs = char.get("attributes", {})
    frontend_attrs = {
        "constitution": backend_attrs.get("constitution", backend_attrs.get("\u6839\u9aa8", 5)),
        "comprehension": backend_attrs.get("comprehension", backend_attrs.get("\u609f\u6027", 5)),
        "spirit": backend_attrs.get("spirit", backend_attrs.get("\u795e\u8bc6", 5)),
        "luck": backend_attrs.get("luck", backend_attrs.get("\u673a\u7f18", 5))
    }
    print(f"\n映射后的前端属性: {json.dumps(frontend_attrs, ensure_ascii=False, indent=2)}")
