"""
CommandProcessor 使用示例

展示如何使用命令处理系统
"""

import asyncio
from pathlib import Path
from xwe.core.state import GameStateManager
from xwe.core.output import OutputManager, ConsoleChannel, FileChannel
from xwe.core.command import (
    CommandProcessor,
    # 中间件
    LoggingMiddleware,
    ValidationMiddleware,
    CooldownMiddleware,
    RateLimitMiddleware,
    # 处理器
    CombatCommandHandler,
    InteractionCommandHandler,
    SystemCommandHandler,
    CultivationCommandHandler,
    MovementHandler,
    InfoHandler,
)
from xwe.core.character import Character, CharacterType


def setup_command_processor():
    """设置命令处理器"""
    # 创建依赖
    state_manager = GameStateManager()
    output_manager = OutputManager()
    
    # 添加输出通道
    output_manager.add_channel(ConsoleChannel(colored=True))
    output_manager.add_channel(FileChannel(Path("command_demo.log")))
    
    # 创建命令处理器
    processor = CommandProcessor(state_manager, output_manager)
    
    # 添加中间件
    processor.add_middleware(LoggingMiddleware())
    processor.add_middleware(ValidationMiddleware())
    processor.add_middleware(CooldownMiddleware())
    processor.add_middleware(RateLimitMiddleware(max_commands=30, window=60))
    
    # 注册命令处理器
    processor.register_handler(CombatCommandHandler())
    processor.register_handler(InteractionCommandHandler())
    processor.register_handler(SystemCommandHandler())
    processor.register_handler(CultivationCommandHandler())
    processor.register_handler(MovementHandler())
    processor.register_handler(InfoHandler())
    
    # 添加命令别名
    processor.add_alias("杀", "攻击")
    processor.add_alias("k", "攻击")
    processor.add_alias("逃", "逃跑")
    processor.add_alias("说", "和")
    processor.add_alias("买", "交易")
    processor.add_alias("练", "修炼")
    processor.add_alias("存", "保存")
    processor.add_alias("读", "加载")
    processor.add_alias("退", "退出")
    processor.add_alias("?", "帮助")
    
    return processor, state_manager, output_manager


def demo_basic_commands(processor, state_manager, output_manager):
    """演示基础命令"""
    print("\n=== 基础命令演示 ===\n")
    
    # 创建测试角色
    player = Character(name="测试侠", character_type=CharacterType.PLAYER)
    state_manager.set_player(player)
    state_manager.set_location("青云山")
    
    # 测试各种命令
    test_commands = [
        "帮助",
        "状态",
        "背包",
        "技能",
        "地图",
        "修炼",
        "探索",
        "去 主城",
        "和 掌门 说话",
        "保存 测试存档",
    ]
    
    for cmd in test_commands:
        print(f"\n>>> 执行命令: {cmd}")
        result = processor.process_command(cmd)
        
        if result.success:
            print(f"✓ 命令执行成功")
        else:
            print(f"✗ 命令执行失败: {result.error}")
        
        # 短暂延迟，便于观察
        import time
        time.sleep(0.5)


def demo_combat_commands(processor, state_manager, output_manager):
    """演示战斗命令"""
    print("\n=== 战斗命令演示 ===\n")
    
    # 模拟进入战斗
    state_manager.start_combat("combat_001")
    output_manager.narrative("你遭遇了一只凶恶的妖兽！")
    output_manager.combat("战斗开始！")
    
    # 战斗命令序列
    combat_commands = [
        "攻击",
        "攻击 妖兽",
        "使用 剑气斩 攻击 妖兽",
        "防御",
        "逃跑",
    ]
    
    for cmd in combat_commands:
        print(f"\n>>> 战斗命令: {cmd}")
        result = processor.process_command(cmd)
        
        # 短暂延迟
        import time
        time.sleep(0.5)
    
    # 结束战斗
    state_manager.end_combat({'winner': 'player'})


def demo_dialogue_commands(processor, state_manager, output_manager):
    """演示对话命令"""
    print("\n=== 对话命令演示 ===\n")
    
    # 对话相关命令
    dialogue_commands = [
        "和 商人 说话",
        "交易 商人",
        "拾取",
        "拾取 灵石",
    ]
    
    for cmd in dialogue_commands:
        print(f"\n>>> 对话/交互命令: {cmd}")
        result = processor.process_command(cmd)
        
        # 如果进入了特殊上下文，退出
        if state_manager.get_current_context() != state_manager.context_stack[0]:
            state_manager.pop_context()
        
        import time
        time.sleep(0.5)


def demo_cultivation_commands(processor, state_manager, output_manager):
    """演示修炼命令"""
    print("\n=== 修炼命令演示 ===\n")
    
    # 修炼相关命令
    cultivation_commands = [
        "修炼",
        "学习 剑气斩",
        "使用 气血药水",
        "突破",  # 可能会失败，因为条件不足
    ]
    
    for cmd in cultivation_commands:
        print(f"\n>>> 修炼命令: {cmd}")
        result = processor.process_command(cmd)
        
        import time
        time.sleep(0.5)


def demo_alias_and_suggestions(processor, state_manager, output_manager):
    """演示别名和建议功能"""
    print("\n=== 别名和建议功能演示 ===\n")
    
    # 测试别名
    alias_commands = [
        "?",          # 帮助的别名
        "练",         # 修炼的别名
        "存 别名测试",  # 保存的别名
        "杀 妖兽",     # 攻击的别名
    ]
    
    for cmd in alias_commands:
        print(f"\n>>> 使用别名: {cmd}")
        result = processor.process_command(cmd)
        
        import time
        time.sleep(0.5)
    
    # 测试命令建议
    print("\n>>> 测试命令建议")
    partial_commands = ["攻", "使", "修", "帮"]
    
    for partial in partial_commands:
        suggestions = processor.get_suggestions(partial)
        print(f"\n输入 '{partial}' 的建议:")
        for s in suggestions:
            print(f"  - {s}")


def demo_middleware_effects(processor, state_manager, output_manager):
    """演示中间件效果"""
    print("\n=== 中间件效果演示 ===\n")
    
    # 测试冷却时间
    print(">>> 测试冷却时间（连续修炼）")
    for i in range(3):
        print(f"\n第{i+1}次修炼:")
        result = processor.process_command("修炼")
        if not result.success:
            print(f"被阻止: {result.error}")
        
        if i == 0:
            import time
            time.sleep(1)  # 等待时间不够
    
    # 测试速率限制
    print("\n>>> 测试速率限制（大量命令）")
    for i in range(12):
        processor.process_command("状态")
        if i == 10:
            print("触发速率限制...")


def demo_command_history(processor, state_manager, output_manager):
    """演示命令历史"""
    print("\n=== 命令历史演示 ===\n")
    
    # 获取命令历史
    history = processor.get_command_history(count=10)
    
    print("最近执行的命令:")
    for entry in history[-10:]:
        timestamp = entry['timestamp'].strftime("%H:%M:%S")
        status = "✓" if entry.get('success') else "✗"
        print(f"{timestamp} {status} {entry['raw_input']}")


async def demo_async_processing():
    """演示异步命令处理"""
    print("\n=== 异步命令处理演示 ===\n")
    
    processor, state_manager, output_manager = setup_command_processor()
    
    # 创建测试角色
    player = Character(name="异步侠", character_type=CharacterType.PLAYER)
    state_manager.set_player(player)
    
    # 异步执行多个命令
    commands = ["状态", "修炼", "探索", "帮助"]
    
    print("并发执行多个命令...")
    tasks = []
    for cmd in commands:
        task = processor.process_command_async(cmd)
        tasks.append(task)
    
    # 等待所有命令完成
    results = await asyncio.gather(*tasks)
    
    print("\n所有命令执行完成:")
    for cmd, result in zip(commands, results):
        status = "成功" if result.success else "失败"
        print(f"- {cmd}: {status}")


def interactive_demo():
    """交互式演示"""
    print("\n=== 交互式命令演示 ===")
    print("输入命令进行测试，输入 '退出' 结束演示\n")
    
    processor, state_manager, output_manager = setup_command_processor()
    
    # 创建测试角色
    player = Character(name="玩家", character_type=CharacterType.PLAYER)
    state_manager.set_player(player)
    state_manager.set_location("青云山主峰")
    
    # 显示初始状态
    processor.process_command("状态")
    
    # 主循环
    while True:
        try:
            command = input("\n> ").strip()
            
            if not command:
                continue
            
            # 处理命令
            result = processor.process_command(command)
            
            # 检查是否退出
            if result.data.get('should_quit'):
                break
                
        except KeyboardInterrupt:
            print("\n\n中断，退出演示")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("CommandProcessor 功能演示")
    print("=" * 60)
    
    # 设置命令处理器
    processor, state_manager, output_manager = setup_command_processor()
    
    # 运行各种演示
    demos = [
        ("基础命令", lambda: demo_basic_commands(processor, state_manager, output_manager)),
        ("战斗命令", lambda: demo_combat_commands(processor, state_manager, output_manager)),
        ("对话命令", lambda: demo_dialogue_commands(processor, state_manager, output_manager)),
        ("修炼命令", lambda: demo_cultivation_commands(processor, state_manager, output_manager)),
        ("别名和建议", lambda: demo_alias_and_suggestions(processor, state_manager, output_manager)),
        ("中间件效果", lambda: demo_middleware_effects(processor, state_manager, output_manager)),
        ("命令历史", lambda: demo_command_history(processor, state_manager, output_manager)),
    ]
    
    for name, demo_func in demos:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            demo_func()
        except Exception as e:
            print(f"演示 {name} 出错: {e}")
    
    # 异步演示
    print(f"\n{'='*20} 异步处理 {'='*20}")
    asyncio.run(demo_async_processing())
    
    # 询问是否进入交互模式
    print("\n" + "=" * 60)
    response = input("\n是否进入交互式演示？(y/n): ")
    if response.lower() == 'y':
        interactive_demo()
    
    print("\n所有演示完成！")
    print("\n生成的文件：")
    print("- command_demo.log (命令日志)")


if __name__ == "__main__":
    main()
