#!/usr/bin/env python3
"""
修仙世界引擎优化测试脚本
验证所有优化系统是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xwe.core.game_core import GameCore
from xwe.core.chinese_dragon_art import get_dragon_art, get_dragon_for_scene
from xwe.core.status_manager import StatusDisplayManager  
from xwe.core.achievement_system import AchievementSystem
from xwe.core.command_router import CommandRouter, CommandPriority
from xwe.core.event_system import ImmersiveEventSystem, EventType
import time

def test_dragon_art():
    """测试中国龙ASCII艺术"""
    print("\n=== 测试中国龙艺术 ===")
    
    # 测试不同场景的龙
    scenes = ['welcome', 'battle', 'victory', 'cultivation']
    for scene in scenes:
        print(f"\n{scene}场景的龙：")
        print(get_dragon_for_scene(scene))
        time.sleep(0.5)

def test_status_manager():
    """测试状态显示管理器"""
    print("\n=== 测试状态显示管理器 ===")
    
    status_manager = StatusDisplayManager()
    
    # 测试不同场景
    print("\n1. 正常场景（不显示状态）：")
    if status_manager.should_display():
        print("错误：不应该显示状态")
    else:
        print("✓ 正确：不显示状态")
    
    print("\n2. 战斗场景（自动显示）：")
    status_manager.enter_context('battle')
    if status_manager.should_display():
        print("✓ 正确：自动显示状态")
    else:
        print("错误：应该显示状态")
    status_manager.exit_context()
    
    print("\n3. 主动查看（临时显示）：")
    status_manager.trigger_display()
    if status_manager.should_display():
        print("✓ 正确：显示状态")
    else:
        print("错误：应该显示状态")

def test_achievement_system():
    """测试成就系统"""
    print("\n=== 测试成就系统 ===")
    
    achievement_system = AchievementSystem()
    
    print("\n1. 初始状态：")
    print(f"已解锁成就数：{len(achievement_system.unlocked_achievements)}")
    if len(achievement_system.unlocked_achievements) == 0:
        print("✓ 正确：开始时没有成就")
    else:
        print("错误：开始时不应该有成就")
    
    print("\n2. 触发第一个成就：")
    unlocked = achievement_system.check_achievement('first_step', 1)
    if unlocked:
        print("✓ 正确：解锁了'初入江湖'成就")
    else:
        print("错误：应该解锁成就")
    
    print("\n3. 进度型成就：")
    for i in range(5):
        achievement_system.check_achievement('warrior_10', i + 1)
    
    progress = achievement_system.get_achievement_progress('warrior_10')
    print(f"战士成就进度：{progress['current']}/{progress['required']}")

def test_command_router():
    """测试命令路由系统"""
    print("\n=== 测试命令路由系统 ===")
    
    router = CommandRouter()
    
    # 注册测试命令
    def test_handler(params):
        return f"执行命令：{params}"
    
    # 设置简单的NLP处理器
    def nlp_handler(text, context):
        if "修炼" in text:
            return {'command_type': 'cultivate', 'parameters': {}}
        return {'command_type': 'unknown', 'parameters': {}}
    
    router.set_nlp_handler(nlp_handler)
    
    # 测试不同命令
    test_cases = [
        ("帮助", "系统命令"),
        ("状态", "核心命令"),
        ("我想修炼一会", "NLP处理"),
        ("随便输入", "未知命令")
    ]
    
    print("\n命令测试：")
    for cmd, expected in test_cases:
        cmd_type, params = router.route_command(cmd)
        print(f"输入：'{cmd}' -> 类型：{cmd_type} ({expected})")

def test_event_system():
    """测试事件系统"""
    print("\n=== 测试事件系统 ===")
    
    output_buffer = []
    
    def mock_output(text):
        output_buffer.append(text)
        print(text)
    
    event_system = ImmersiveEventSystem(mock_output)
    
    print("\n1. 创建动态事件：")
    event = event_system.create_dynamic_event(
        "测试事件",
        "这是一个测试事件，展示打字机效果...",
        [("选项1", None), ("选项2", None)]
    )
    
    print("\n2. 触发事件（注意打字机效果）：")
    event_system.start_event(event.event_id)

def test_integration():
    """测试系统集成"""
    print("\n=== 测试系统集成 ===")
    
    # 创建游戏实例
    game = GameCore()
    
    print("\n1. 初始化检查：")
    print(f"✓ 状态管理器：{'已加载' if hasattr(game, 'status_manager') else '未加载'}")
    print(f"✓ 成就系统：{'已加载' if hasattr(game, 'achievement_system') else '未加载'}")
    print(f"✓ 命令路由：{'已加载' if hasattr(game, 'command_router') else '未加载'}")
    print(f"✓ 事件系统：{'已加载' if hasattr(game, 'immersive_event_system') else '未加载'}")
    
    print("\n2. 启动游戏测试：")
    game.running = True  # 手动设置运行状态
    
    # 测试命令处理
    test_commands = ["帮助", "状态", "我想看看周围"]
    for cmd in test_commands:
        print(f"\n处理命令：'{cmd}'")
        game.process_command(cmd)
        output = game.get_output()
        if output:
            print(f"输出行数：{len(output)}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("修仙世界引擎优化测试")
    print("=" * 60)
    
    try:
        test_dragon_art()
        time.sleep(1)
        
        test_status_manager()
        time.sleep(1)
        
        test_achievement_system()
        time.sleep(1)
        
        test_command_router()
        time.sleep(1)
        
        test_event_system()
        time.sleep(1)
        
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
