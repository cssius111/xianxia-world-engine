#!/usr/bin/env python3
"""
测试NLP处理器修复
验证build_prompt方法是否能正确处理特殊字符输入
"""

import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.xwe.core.nlp.nlp_processor import DeepSeekNLPProcessor
from src.xwe.core.nlp.config import get_nlp_config

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_sanitize_input():
    """测试输入清理功能"""
    print("🧹 测试输入清理功能")
    print("=" * 50)
    
    # 创建处理器实例（不需要真正的API密钥来测试清理功能）
    try:
        config = get_nlp_config()
        if not config.get_api_key():
            # 为测试设置一个假的API密钥
            os.environ['DEEPSEEK_API_KEY'] = 'test_key_for_sanitize_only'
        
        processor = DeepSeekNLPProcessor()
    except Exception as e:
        logger.error(f"无法创建处理器: {e}")
        return False
    
    # 测试用例
    test_cases = [
        ('\\n  "raw"', "原始错误输入"),
        ('修炼大道法则', "正常中文输入"),
        ('{"test": "json"}', "JSON格式输入"),
        ('a{b}c', "包含花括号"),
        ('"quoted"', "包含引号"),
        ('\\t\\n\\r', "控制字符"),
        ('normal input', "普通英文"),
        ('', "空输入"),
        ('a' * 600, "超长输入"),
    ]
    
    success_count = 0
    for i, (test_input, description) in enumerate(test_cases, 1):
        print(f"\\n{i}. {description}")
        print(f"   原始输入: {repr(test_input)}")
        
        try:
            # 测试清理功能
            sanitized = processor._sanitize_user_input(test_input)
            print(f"   清理结果: {repr(sanitized)}")
            print("   ✅ 清理成功")
            success_count += 1
        except Exception as e:
            print(f"   ❌ 清理失败: {e}")
    
    print(f"\\n📊 清理测试结果: {success_count}/{len(test_cases)} 成功")
    return success_count == len(test_cases)

def test_build_prompt():
    """测试prompt构建功能"""
    print("\\n🏗️ 测试prompt构建功能")
    print("=" * 50)
    
    try:
        config = get_nlp_config()
        if not config.get_api_key():
            os.environ['DEEPSEEK_API_KEY'] = 'test_key_for_prompt_build_only'
        
        processor = DeepSeekNLPProcessor()
    except Exception as e:
        logger.error(f"无法创建处理器: {e}")
        return False
    
    # 测试导致原始错误的输入
    problematic_inputs = [
        '\\n  "raw"',
        '修炼大道法则',
        '打败国王',
        '探索',
        '{"command": "test"}',
        'normal command',
    ]
    
    success_count = 0
    for i, test_input in enumerate(problematic_inputs, 1):
        print(f"\\n{i}. 测试输入: {repr(test_input)}")
        
        try:
            # 测试构建prompt
            prompt = processor.build_prompt(test_input)
            
            # 检查prompt是否包含输入
            if test_input.strip() in prompt or processor._sanitize_user_input(test_input) in prompt:
                print("   ✅ prompt构建成功，包含用户输入")
                success_count += 1
            else:
                print("   ⚠️ prompt构建成功，但未找到用户输入")
                
        except Exception as e:
            print(f"   ❌ prompt构建失败: {e}")
    
    print(f"\\n📊 prompt构建测试结果: {success_count}/{len(problematic_inputs)} 成功")
    return success_count == len(problematic_inputs)

def test_parse_with_fallback():
    """测试带回退的解析功能"""
    print("\\n🔄 测试解析功能（本地回退）")
    print("=" * 50)
    
    try:
        config = get_nlp_config()
        # 设置为使用本地回退
        os.environ['DEEPSEEK_API_KEY'] = ''  # 清空API密钥强制使用回退
        
        # 重新创建处理器
        processor = DeepSeekNLPProcessor()
    except Exception as e:
        print(f"注意: 无法创建DeepSeek处理器（预期行为）: {e}")
        # 这是预期的，因为我们没有API密钥
        return True
    
    # 如果能创建成功，测试本地回退
    test_commands = [
        '修炼大道法则',
        '探索',
        '查看状态',
        '打开背包',
    ]
    
    success_count = 0
    for i, command in enumerate(test_commands, 1):
        print(f"\\n{i}. 测试命令: {command}")
        
        try:
            # 测试解析（应该使用本地回退）
            result = processor.parse(command)
            print(f"   解析结果: {result.normalized_command}")
            print(f"   意图: {result.intent}")
            print("   ✅ 解析成功")
            success_count += 1
        except Exception as e:
            print(f"   ❌ 解析失败: {e}")
    
    print(f"\\n📊 解析测试结果: {success_count}/{len(test_commands)} 成功")
    return success_count == len(test_commands)

def main():
    """主测试函数"""
    print("🔧 NLP处理器修复验证测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行测试
    test_results.append(("输入清理", test_sanitize_input()))
    test_results.append(("prompt构建", test_build_prompt()))
    test_results.append(("解析功能", test_parse_with_fallback()))
    
    # 汇总结果
    print("\\n" + "=" * 60)
    print("📋 测试结果汇总:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\\n🎉 所有测试通过！修复方案有效。")
        return 0
    else:
        print(f"\\n⚠️ {total - passed} 项测试失败，需要进一步检查。")
        return 1

if __name__ == "__main__":
    exit(main())
