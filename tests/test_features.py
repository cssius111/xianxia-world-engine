#!/usr/bin/env python3
"""
测试所有新功能
"""

import os

# 添加项目根目录到Python路径

from xwe.features import *
from xwe.features.player_experience import SmartCommandProcessor
from xwe.features.visual_enhancement import ProgressBar
import time


def test_player_experience():
    """测试玩家体验功能"""
    print("\n=== 测试玩家体验功能 ===")
    
    # 测试命令处理器
    processor = SmartCommandProcessor()
    
    test_inputs = [
        "工击敌人",  # 错别字
        "atk",       # 快捷键
        "我想打那个妖兽",  # 自然语言
        "?"          # 帮助
    ]
    
    for input_text in test_inputs:
        command, confidence = processor.process_input(input_text)
        print(f"输入: '{input_text}' -> 命令: '{command}' (置信度: {confidence:.2f})")
    
    # 测试建议
    suggestions = processor.get_suggestions("修")
    print(f"\n'修'的建议: {suggestions}")
    
    print("✅ 玩家体验功能测试通过")


def test_narrative_system():
    """测试叙事系统"""
    print("\n=== 测试叙事系统 ===")
    
    # 测试开局事件
    player_data = {"player_name": "测试玩家", "level": 1}
    opening = narrative_system.trigger_opening_event(player_data)
    
    if opening:
        print(f"触发开局事件: {opening['event'].name}")
        print(f"事件描述: {opening['event'].description}")
        print(f"选项数: {len(opening['choices'])}")
    
    # 测试成就系统
    player_stats = {
        "kills": 1,
        "level": 5,
        "cultivation_count": 10
    }
    
    achievements = narrative_system.update_achievements(player_stats)
    print(f"\n解锁成就数: {len(achievements)}")
    for ach in achievements:
        print(f"  - {ach.name}: {ach.description}")
    
    print("✅ 叙事系统测试通过")


def test_content_ecosystem():
    """测试内容生态系统"""
    print("\n=== 测试内容生态系统 ===")
    
    # 扫描MOD
    mods = content_ecosystem.mod_loader.scan_mods()
    print(f"发现MOD数: {len(mods)}")
    
    # 加载MOD
    for mod in mods[:1]:  # 只加载第一个
        success = content_ecosystem.mod_loader.load_mod(mod)
        print(f"加载MOD '{mod.name}': {'成功' if success else '失败'}")
    
    # 获取统计
    stats = content_ecosystem.get_ecosystem_stats()
    print(f"\n内容统计:")
    print(f"  - 已加载MOD: {stats['loaded_mods']}")
    print(f"  - 总内容数: {stats['total_content']}")
    
    print("✅ 内容生态系统测试通过")


def test_ai_personalization():
    """测试AI个性化"""
    print("\n=== 测试AI个性化 ===")
    
    player_id = "test_player"
    
    # 记录一些行为
    actions = [
        ("attack", "妖兽"),
        ("attack", "敌人"),
        ("explore", None),
        ("talk", "NPC"),
        ("cultivate", None)
    ]
    
    for action_type, target in actions:
        personalization_engine.record_player_action(
            player_id, action_type, target
        )
    
    # 获取个性化内容
    personalized = personalization_engine.get_personalized_content(player_id)
    print(f"玩家风格: {personalized['player_style']}")
    print(f"推荐内容: {len(personalized['recommendations'])}个")
    print(f"个性化提示: {len(personalized['tips'])}个")
    
    print("✅ AI个性化测试通过")


def test_community_system():
    """测试社区系统"""
    print("\n=== 测试社区系统 ===")
    
    # 提交反馈
    feedback_id = submit_feedback("这是一个测试反馈，游戏很棒！", "test_player")
    print(f"反馈已提交，ID: {feedback_id}")
    
    # 获取社区信息
    community_info = show_community()
    print(f"\n社区链接数: {len(community_system.community_hub.links)}")
    
    # 获取反馈统计
    stats = community_system.feedback_collector.get_feedback_stats()
    print(f"总反馈数: {stats['total_count']}")
    
    print("✅ 社区系统测试通过")


def test_technical_ops():
    """测试技术运营功能"""
    print("\n=== 测试技术运营功能 ===")
    
    # 测试存档
    test_game_state = {
        "player": {"name": "测试玩家", "level": 10},
        "game_time": 1000,
        "current_location": "测试地点"
    }
    
    save_id = tech_ops_system.create_game_save(test_game_state, "test")
    print(f"创建存档: {save_id}")
    
    # 列出存档
    saves = tech_ops_system.save_manager.list_saves("测试玩家")
    print(f"玩家存档数: {len(saves)}")
    
    # 测试错误处理
    try:
        raise ValueError("这是一个测试错误")
    except Exception as e:
        error_id = tech_ops_system.handle_game_error(e, {"test": True})
        print(f"错误已处理，ID: {error_id}")
    
    # 获取系统状态
    status = tech_ops_system.get_system_status()
    print(f"\n系统状态:")
    print(f"  - 平台: {status['system']['platform']}")
    print(f"  - CPU核心数: {status['system']['cpu_count']}")
    print(f"  - 内存: {status['system']['memory_total_gb']}GB")
    
    print("✅ 技术运营功能测试通过")


def test_visual_effects():
    """测试视觉效果"""
    print("\n=== 测试视觉效果 ===")
    
    # 测试颜色文字
    print(visual_effects.text_renderer.colorize("红色文字", "error"))
    print(visual_effects.text_renderer.colorize("绿色文字", "success"))
    print(visual_effects.text_renderer.colorize("蓝色文字", "info"))
    
    # 测试文字框
    box_text = visual_effects.text_renderer.box("这是一个文字框", style="double")
    print(box_text)
    
    # 测试进度条
    progress = ProgressBar(100, width=30)
    print("\n修炼进度:")
    for i in range(0, 101, 20):
        progress.update(i, prefix="修炼中", suffix=f"{i}%")
        time.sleep(0.1)
    
    # 测试ASCII艺术
    print("\n宝剑:")
    print(visual_effects.ascii_art.get_art("sword"))
    
    print("\n✅ 视觉效果测试通过")


def main():
    """主测试函数"""
    print("=== 修仙世界引擎 2.0 功能测试 ===")
    
    # 检查依赖
    try:
        import psutil
        print("✅ psutil 已安装")
    except ImportError:
        print("❌ 缺少 psutil，部分功能可能无法测试")
        print("请运行: pip install psutil")
    
    # 运行所有测试
    tests = [
        test_player_experience,
        test_narrative_system,
        test_content_ecosystem,
        test_ai_personalization,
        test_community_system,
        test_technical_ops,
        test_visual_effects
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_func.__name__} 失败: {e}")
            failed += 1
    
    print(f"\n\n=== 测试结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {len(tests)}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败")


if __name__ == "__main__":
    main()
