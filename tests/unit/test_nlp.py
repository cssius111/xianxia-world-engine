# test_nlp.py
"""
测试自然语言处理功能

测试NLP模块的命令理解能力。
"""


# 添加项目根目录到Python路径

from xwe.core import CommandParser
from xwe.core.nlp import NLPProcessor, NLPConfig


def test_nlp_basic():
    """测试基础NLP功能"""
    print("=== 测试NLP基础功能 ===")
    
    # 创建命令解析器和NLP处理器
    command_parser = CommandParser()
    nlp_config = NLPConfig(
        enable_llm=True,
        llm_provider="mock",
        fallback_to_rules=True
    )
    nlp_processor = NLPProcessor(command_parser, nlp_config)
    
    # 测试各种自然语言输入
    test_inputs = [
        # 战斗相关
        ("我想攻击那个妖兽", "应该解析为攻击命令"),
        ("打他！", "应该解析为攻击命令"),
        ("用剑气斩攻击敌人", "应该解析为使用技能命令"),
        ("我要防御", "应该解析为防御命令"),
        ("快跑！", "应该解析为逃跑命令"),
        
        # 信息查询
        ("看看我的状态", "应该解析为状态命令"),
        ("查看一下我的属性", "应该解析为状态命令"),
        ("我有什么技能", "应该解析为技能列表命令"),
        ("打开背包", "应该解析为背包命令"),
        
        # 修炼相关
        ("我想修炼一会儿", "应该解析为修炼命令"),
        ("打坐恢复一下", "应该解析为修炼命令"),
        
        # 探索相关
        ("探索这里", "应该解析为探索命令"),
        ("四处看看", "应该解析为探索命令"),
        
        # 模糊输入
        ("emmm...我该做什么", "应该无法解析"),
        ("", "空输入应该无法解析")
    ]
    
    for user_input, expected in test_inputs:
        print(f"\n输入: '{user_input}'")
        print(f"期望: {expected}")
        
        command = nlp_processor.parse(user_input)
        print(f"解析结果: {command.command_type.value}")
        
        if command.target:
            print(f"目标: {command.target}")
        if command.parameters:
            print(f"参数: {command.parameters}")
        
        # 获取命令解释
        explanation = nlp_processor.explain_command(command)
        print(f"解释: {explanation}")
    
    print("\n✓ NLP基础功能测试完成")


def test_nlp_context():
    """测试带上下文的NLP功能"""
    print("\n=== 测试带上下文的NLP功能 ===")
    
    command_parser = CommandParser()
    nlp_processor = NLPProcessor(command_parser)
    
    # 战斗上下文
    combat_context = {
        'in_combat': True,
        'enemies': [
            {'name': '低阶妖兽', 'health_percent': 0.7},
            {'name': '魔化野狼', 'health_percent': 0.9}
        ],
        'available_skills': ['剑气斩', '疾风步', '金刚护体']
    }
    
    test_inputs = [
        "攻击低阶妖兽",
        "用剑气斩",
        "使用金刚护体",
        "攻击血少的那个"
    ]
    
    print("战斗上下文:")
    print(f"  敌人: {[e['name'] for e in combat_context['enemies']]}")
    print(f"  可用技能: {combat_context['available_skills']}")
    
    for user_input in test_inputs:
        print(f"\n输入: '{user_input}'")
        command = nlp_processor.parse(user_input, combat_context)
        print(f"解析: {command.command_type.value}")
        if command.target:
            print(f"目标: {command.target}")
        if command.parameters:
            print(f"参数: {command.parameters}")
    
    print("\n✓ 上下文NLP测试完成")


def test_nlp_suggestions():
    """测试命令建议功能"""
    print("\n=== 测试命令建议功能 ===")
    
    command_parser = CommandParser()
    nlp_processor = NLPProcessor(command_parser)
    
    # 测试不同的部分输入
    partial_inputs = ["攻", "使用", "查看", ""]
    
    for partial in partial_inputs:
        print(f"\n部分输入: '{partial}'")
        suggestions = nlp_processor.get_suggestions(partial)
        print("建议:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"  {i}. {suggestion}")
    
    # 测试战斗中的建议
    combat_context = {
        'in_combat': True,
        'available_skills': ['剑气斩', '火球术']
    }
    
    print("\n战斗中的建议:")
    suggestions = nlp_processor.get_suggestions("", combat_context)
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"  {i}. {suggestion}")
    
    print("\n✓ 命令建议测试完成")


def test_nlp_fuzzy_matching():
    """测试模糊匹配功能"""
    print("\n=== 测试模糊匹配功能 ===")
    
    command_parser = CommandParser()
    nlp_processor = NLPProcessor(command_parser)
    
    # 测试各种模糊输入
    fuzzy_inputs = [
        "揍他",
        "砍死敌人",
        "我要跑路",
        "看看自己的属性",
        "瞅瞅背包",
        "练功去",
        "闭关修炼"
    ]
    
    for user_input in fuzzy_inputs:
        print(f"\n输入: '{user_input}'")
        command = nlp_processor.parse(user_input)
        print(f"解析: {command.command_type.value}")
        print(f"置信度: {command.confidence}")
    
    print("\n✓ 模糊匹配测试完成")


def main():
    """运行所有NLP测试"""
    print("仙侠世界引擎 - NLP功能测试")
    print("=" * 50)
    
    try:
        test_nlp_basic()
        test_nlp_context()
        test_nlp_suggestions()
        test_nlp_fuzzy_matching()
        
        print("\n" + "=" * 50)
        print("所有NLP测试通过！")
        print("\n提示：")
        print("1. 当前使用Mock LLM提供者进行测试")
        print("2. 要使用真实的LLM，请设置环境变量：")
        print("   - DEEPSEEK_API_KEY=你的API密钥")
        print("   - 或 OPENAI_API_KEY=你的API密钥")
        print("3. 然后在代码中将llm_provider改为'deepseek'或'openai'")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
