#!/usr/bin/env python3
"""
修仙世界引擎优化效果演示
快速展示所有优化功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xwe.core.chinese_dragon_art import get_dragon_for_scene
from xwe.core.status_manager import StatusDisplayManager
from xwe.core.achievement_system import AchievementSystem
from xwe.core.command_router import CommandRouter
from xwe.core.event_system import SpecialEventHandler, ImmersiveEventSystem
import time

def demo_dragon_art():
    """演示中国龙艺术"""
    print("\n" + "="*60)
    print("🐲 演示1：中国龙ASCII艺术")
    print("="*60)
    
    print("\n欢迎场景的龙：")
    print(get_dragon_for_scene('welcome'))
    
    input("\n按回车继续...")
    
    print("\n战斗场景的龙：")
    print(get_dragon_for_scene('battle'))
    
    input("\n按回车继续...")

def demo_status_display():
    """演示状态显示管理"""
    print("\n" + "="*60)
    print("📊 演示2：智能状态显示")
    print("="*60)
    
    status_manager = StatusDisplayManager()
    
    print("\n1. 平时状态（不显示）：")
    print(f"   应该显示状态条？{status_manager.should_display()}")
    
    print("\n2. 进入战斗（自动显示）：")
    status_manager.enter_context('battle')
    print(f"   应该显示状态条？{status_manager.should_display()}")
    status_manager.exit_context()
    
    print("\n3. 玩家主动查看（临时显示5秒）：")
    status_manager.trigger_display()
    print(f"   应该显示状态条？{status_manager.should_display()}")
    
    input("\n按回车继续...")

def demo_achievement_system():
    """演示成就系统"""
    print("\n" + "="*60)
    print("🏆 演示3：渐进式成就系统")
    print("="*60)
    
    achievement_system = AchievementSystem()
    
    print(f"\n初始成就数：{len(achievement_system.unlocked_achievements)}")
    
    print("\n模拟游戏进程...")
    time.sleep(1)
    
    # 触发第一个成就
    print("\n触发事件：第一次进入游戏")
    unlocked = achievement_system.check_achievement('first_step', 1)
    if unlocked:
        print("🎉 解锁成就：初入江湖！")
    
    time.sleep(1)
    
    # 模拟战斗
    print("\n模拟战斗进程...")
    for i in range(5):
        achievement_system.check_achievement('warrior_10', i + 1)
        print(f"击败敌人数：{i + 1}")
        time.sleep(0.5)
    
    # 显示进度
    progress = achievement_system.get_achievement_progress('warrior_10')
    print(f"\n战士成就进度：{progress['current']}/{progress['required']}")
    
    input("\n按回车继续...")

def demo_command_priority():
    """演示命令优先级系统"""
    print("\n" + "="*60)
    print("🎯 演示4：命令优先级系统")
    print("="*60)
    
    router = CommandRouter()
    
    # 设置简单的NLP处理器
    def nlp_handler(text, context):
        print(f"   [NLP处理] 分析：'{text}'")
        if "修炼" in text:
            return {'command_type': 'cultivate', 'parameters': {}}
        elif "看看" in text and "周围" in text:
            return {'command_type': 'explore', 'parameters': {}}
        return {'command_type': 'unknown', 'parameters': {}}
    
    router.set_nlp_handler(nlp_handler)
    
    # 测试不同命令
    test_cases = [
        ("帮助", "系统命令 - 精确匹配"),
        ("帮助我", "NLP处理 - 不是精确匹配"),
        ("状态", "核心命令 - 精确匹配"),
        ("查看状态", "模糊匹配"),
        ("我想修炼一会", "NLP处理"),
        ("看看周围有什么", "NLP处理")
    ]
    
    print("\n命令处理演示：")
    for cmd, desc in test_cases:
        print(f"\n输入：'{cmd}' ({desc})")
        cmd_type, params = router.route_command(cmd)
        print(f"   识别结果：{cmd_type}")
        time.sleep(0.5)
    
    input("\n按回车继续...")

def demo_immersive_events():
    """演示沉浸式事件系统"""
    print("\n" + "="*60)
    print("📖 演示5：沉浸式事件系统")
    print("="*60)
    
    def mock_output(text):
        print(text)
    
    event_system = ImmersiveEventSystem(mock_output)
    
    print("\n注意观察打字机效果...")
    time.sleep(1)
    
    # 创建测试事件
    event_system.create_dynamic_event(
        "神秘的邂逅",
        "在青云山的小径上，你遇到了一位白衣飘飘的女子...",
        [
            ("上前搭话", None),
            ("保持距离观察", None),
            ("转身离开", None)
        ]
    )
    
    # 触发最新创建的事件
    event_id = list(event_system.events.keys())[-1]
    event_system.start_event(event_id)
    
    print("\n（在实际游戏中，玩家可以选择不同选项推进剧情）")
    
    input("\n按回车继续...")

def demo_cultivation_event():
    """演示修炼事件"""
    print("\n" + "="*60)
    print("🧘 演示6：沉浸式修炼体验")
    print("="*60)
    
    def mock_output(text):
        print(text)
    
    event_system = ImmersiveEventSystem(mock_output)
    
    print("\n模拟修炼过程...")
    time.sleep(1)
    
    # 模拟修炼
    player_data = {'attributes': {'comprehension': 10}}
    SpecialEventHandler.handle_cultivation_event(
        event_system,
        player_data,
        3  # 修炼3天
    )
    
    input("\n演示完成，按回车结束...")

def main():
    """主演示函数"""
    print("="*60)
    print("✨ 修仙世界引擎 - 优化效果演示")
    print("="*60)
    print("\n本演示将展示所有优化功能")
    print("按照提示操作即可")
    
    input("\n按回车开始演示...")
    
    try:
        # 依次演示各个功能
        demo_dragon_art()
        demo_status_display()
        demo_achievement_system()
        demo_command_priority()
        demo_immersive_events()
        demo_cultivation_event()
        
        print("\n" + "="*60)
        print("🎉 所有优化功能演示完成！")
        print("="*60)
        print("\n现在你可以运行 'python run_optimized_game.py' 体验完整游戏")
        print("或运行 'python test_optimizations.py' 进行详细测试")
        
    except KeyboardInterrupt:
        print("\n\n演示中断")
    except Exception as e:
        print(f"\n❌ 演示出错：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
