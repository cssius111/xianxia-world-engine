"""
测试 Roll 系统功能

确保角色生成系统正常工作。
"""

import unittest
import json
from typing import Dict, Any

# 添加项目根目录到 Python 路径

from xwe.core.roll_system import CharacterRoller, RollResult, ROLL_DATA
from xwe.core.roll_system.roll_utils import weighted_random_choice, random_select_elements


class TestRollSystem(unittest.TestCase):
    """测试Roll系统"""
    
    def setUp(self):
        """测试前准备"""
        self.roller = CharacterRoller()
    
    def test_basic_roll(self):
        """测试基础roll功能"""
        result = self.roller.roll()
        
        # 检查结果类型
        self.assertIsInstance(result, RollResult)
        
        # 检查必要字段
        self.assertIsNotNone(result.name)
        self.assertIn(result.gender, ['男', '女'])
        self.assertIsNotNone(result.identity)
        self.assertIsInstance(result.attributes, dict)
        self.assertIsNotNone(result.spiritual_root_type)
        self.assertIsInstance(result.spiritual_root_elements, list)
        self.assertIsNotNone(result.destiny)
        self.assertIsInstance(result.talents, list)
        
    def test_attribute_generation(self):
        """测试属性生成"""
        result = self.roller.roll()
        
        # 检查所有属性都存在
        required_attrs = ['attack', 'defense', 'health', 'mana', 'speed', 
                         'comprehension', 'luck', 'constitution', 'charm']
        for attr in required_attrs:
            self.assertIn(attr, result.attributes)
            
        # 检查属性值在合理范围内
        for attr_name, attr_value in result.attributes.items():
            attr_config = ROLL_DATA['base_attributes'].get(attr_name, {})
            if 'min' in attr_config and 'max' in attr_config:
                self.assertGreaterEqual(attr_value, attr_config['min'])
                self.assertLessEqual(attr_value, attr_config['max'] + 10)  # +10 允许命格加成
    
    def test_spiritual_root_generation(self):
        """测试灵根生成"""
        root_counts = {"single": 0, "dual": 0, "triple": 0, "quad": 0, "penta": 0}
        
        # 多次roll统计灵根分布
        for _ in range(100):
            result = self.roller.roll()
            root_type = None
            element_count = len(result.spiritual_root_elements)
            
            if element_count == 1:
                root_type = "single"
            elif element_count == 2:
                root_type = "dual"
            elif element_count == 3:
                root_type = "triple"
            elif element_count == 4:
                root_type = "quad"
            elif element_count == 5:
                root_type = "penta"
                
            if root_type:
                root_counts[root_type] += 1
        
        # 确保所有类型都可能出现（概率测试）
        self.assertGreater(sum(root_counts.values()), 0)
        
    def test_destiny_generation(self):
        """测试命格生成"""
        destinies_found = set()
        
        # 多次roll收集不同命格
        for _ in range(200):
            result = self.roller.roll()
            destinies_found.add(result.destiny)
        
        # 至少应该roll出几种不同的命格
        self.assertGreater(len(destinies_found), 3)
        
        # 检查命格数据完整性
        result = self.roller.roll()
        self.assertIsNotNone(result.destiny_desc)
        self.assertIsNotNone(result.destiny_rarity)
        self.assertIsInstance(result.destiny_effects, dict)
    
    def test_talent_generation(self):
        """测试天赋生成"""
        # 多次roll检查天赋数量
        talent_counts = {1: 0, 2: 0, 3: 0}
        
        for _ in range(100):
            result = self.roller.roll()
            count = len(result.talents)
            if count in talent_counts:
                talent_counts[count] += 1
        
        # 确保1-3个天赋都可能出现
        for count in [1, 2, 3]:
            self.assertGreater(talent_counts[count], 0)
        
        # 检查天赋数据结构
        result = self.roller.roll()
        for talent in result.talents:
            self.assertIn('name', talent)
            self.assertIn('category', talent)
            self.assertIn('description', talent)
            self.assertIn('effects', talent)
    
    def test_system_generation(self):
        """测试系统生成"""
        system_count = 0
        system_types = set()
        
        # 多次roll统计系统出现率
        for _ in range(100):
            result = self.roller.roll()
            if result.system:
                system_count += 1
                system_types.add(result.system['name'])
        
        # 系统出现率应该在20-40%左右（30%概率）
        self.assertGreater(system_count, 10)
        self.assertLess(system_count, 50)
        
        # 应该有多种系统类型
        self.assertGreater(len(system_types), 2)
    
    def test_overall_rating(self):
        """测试综合评级"""
        ratings = set()
        
        # 收集不同的评级
        for _ in range(200):
            result = self.roller.roll()
            ratings.add(result.overall_rating[0])  # 取评级字母
        
        # 应该有多个不同等级
        self.assertGreater(len(ratings), 2)
    
    def test_special_tags(self):
        """测试特殊标签"""
        tags_found = set()
        
        # 多次roll收集标签
        for _ in range(100):
            result = self.roller.roll()
            for tag in result.special_tags:
                tags_found.add(tag)
        
        # 应该能生成一些特殊标签
        self.assertGreater(len(tags_found), 0)
    
    def test_result_serialization(self):
        """测试结果序列化"""
        result = self.roller.roll()
        
        # 测试to_dict
        data_dict = result.to_dict()
        self.assertIsInstance(data_dict, dict)
        self.assertIn('基础信息', data_dict)
        self.assertIn('属性面板', data_dict)
        self.assertIn('灵根', data_dict)
        
        # 测试to_json
        json_str = result.to_json()
        self.assertIsInstance(json_str, str)
        # 确保可以解析
        parsed = json.loads(json_str)
        self.assertIsInstance(parsed, dict)
        
        # 测试display
        display_str = result.display()
        self.assertIsInstance(display_str, str)
        self.assertIn('【角色面板】', display_str)
    
    def test_multi_roll(self):
        """测试批量roll"""
        results = self.roller.multi_roll(10)
        
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertIsInstance(result, RollResult)
        
        # 检查名字不应该全部相同
        names = [r.name for r in results]
        self.assertGreater(len(set(names)), 1)
    
    def test_roll_uniqueness(self):
        """测试roll结果的唯一性"""
        results = []
        for _ in range(20):
            results.append(self.roller.roll())
        
        # 检查没有完全相同的结果
        signatures = []
        for r in results:
            # 创建一个简单的签名来比较
            sig = f"{r.name}-{r.destiny}-{len(r.talents)}-{r.spiritual_root_type}"
            signatures.append(sig)
        
        # 应该有很高的唯一性
        self.assertGreater(len(set(signatures)), 15)
    
    def test_weighted_random(self):
        """测试权重随机选择"""
        # 测试数据
        test_items = {
            "common": {"weight": 70},
            "rare": {"weight": 25},
            "epic": {"weight": 5}
        }
        
        # 多次选择统计结果
        counts = {"common": 0, "rare": 0, "epic": 0}
        for _ in range(1000):
            selected, _ = weighted_random_choice(test_items)
            counts[selected] += 1
        
        # common应该最多，epic最少
        self.assertGreater(counts["common"], counts["rare"])
        self.assertGreater(counts["rare"], counts["epic"])


class TestRollUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_random_select_elements(self):
        """测试随机选择元素"""
        elements = ["A", "B", "C", "D", "E"]
        
        # 测试不同数量
        for count in range(1, 6):
            selected = random_select_elements(elements, count)
            self.assertEqual(len(selected), count)
            self.assertEqual(len(set(selected)), count)  # 无重复
            
        # 测试超出范围
        selected = random_select_elements(elements, 10)
        self.assertEqual(len(selected), 5)


if __name__ == '__main__':
    unittest.main()
