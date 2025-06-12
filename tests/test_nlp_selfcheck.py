#!/usr/bin/env python
"""
NLP系统自检脚本
快速验证NLP功能是否正常
"""

import sys
from typing import Any
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_nlp_basic():
    """基础NLP测试"""
    print("🧪 NLP系统自检")
    print("="*50)
    
    try:
        from xwe.core.nlp.nlp_processor import NLPProcessor
        from xwe.core.command_parser import CommandParser
        
        # 创建实例
        parser = CommandParser()
        nlp = NLPProcessor(parser)
        
        print("✅ NLP模块导入成功")
        
        # 测试用例
        test_cases = [
            ("我要修炼", "修炼命令"),
            ("攻击敌人", "攻击命令"),
            ("看状态", "查看状态"),
            ("用剑气斩攻击", "使用技能"),
            ("逃跑", "逃跑命令"),
            ("去天南坊市", "移动命令"),
            ("随便说点啥", "未知命令")
        ]
        
        print("\n开始测试解析功能:")
        print("-"*50)
        
        success_count = 0
        
        for text, desc in test_cases:
            try:
                result = nlp.parse(text)
                print(f"\n输入: '{text}' ({desc})")
                print(f"  命令类型: {result.command_type.value}")
                if result.target:
                    print(f"  目标: {result.target}")
                if result.parameters:
                    print(f"  参数: {result.parameters}")
                print(f"  置信度: {result.confidence:.2f}")
                success_count += 1
            except Exception as e:
                print(f"\n❌ 解析失败: '{text}'")
                print(f"  错误: {e}")
        
        print("\n" + "="*50)
        print(f"测试结果: {success_count}/{len(test_cases)} 成功")
        
        if success_count == len(test_cases):
            print("\n✅ NLP系统工作正常！")
        else:
            print("\n⚠️ 部分测试失败，请检查NLP实现")
        assert success_count == len(test_cases), (
            f"NLP解析成功{success_count}/{len(test_cases)}")

    except Exception as e:
        print(f"\n❌ NLP系统错误: {e}")
        print("\n请检查:")
        print("1. NLPProcessor是否正确实现")
        print("2. 依赖是否安装完整")
        print("3. 导入路径是否正确")
        assert False, f"NLP系统错误: {e}"

def test_compatibility():
    """测试兼容性"""
    print("\n\n🔄 测试兼容性...")
    print("="*50)
    
    try:
        from xwe.core.nlp.nlp_processor import NLPProcessor
        from xwe.core.command_parser import CommandParser
        
        parser = CommandParser()
        nlp = NLPProcessor(parser)
        
        # 测试process方法（应该有废弃警告）
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = nlp.parse("测试兼容性")
            
            if w and Any("process" in str(warning.message) for warning in w):
                print("✅ process()方法显示废弃警告（正常）")
            else:
                print("⚠️ process()方法没有显示废弃警告")
                
    except AttributeError:
        print("❌ process()方法不存在（需要添加兼容层）")
    except Exception as e:
        print(f"❌ 兼容性测试失败: {e}")

def main():
    """主函数"""
    # 基础测试
    success = test_nlp_basic()
    
    # 兼容性测试
    test_compatibility()
    
    # 总结
    print("\n\n📋 自检总结")
    print("="*50)
    
    if success:
        print("✅ NLP系统可以正常使用！")
        print("\n可以运行以下命令继续测试:")
        print("  python scripts/test_nlp.py")
        print("  python main_menu.py")
    else:
        print("❌ NLP系统存在问题，请运行修复脚本:")
        print("  python nlp_oneshot_fix.py")

if __name__ == "__main__":
    main()
