# @dev_only
"""
服务层使用示例
展示如何在实际应用中使用新的Service层架构
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from xwe.services import (
    ServiceContainer, register_services,
    IGameService, IPlayerService, ICommandEngine, IEventDispatcher, ILogService
)
from xwe.events import subscribe_event


def example_game_flow():
    """示例游戏流程"""
    print("=== 修仙世界引擎 - Service层示例 ===\n")
    
    # 1. 初始化服务容器
    print("1. 初始化服务容器...")
    container = ServiceContainer()
    register_services(container)
    print("✓ 服务容器初始化完成")
    
    # 2. 获取核心服务
    print("\n2. 获取核心服务...")
    game_service = container.resolve(IGameService)
    player_service = container.resolve(IPlayerService)
    command_engine = container.resolve(ICommandEngine)
    event_dispatcher = container.resolve(IEventDispatcher)
    log_service = container.resolve(ILogService)
    print("✓ 所有服务已就绪")
    
    # 3. 设置事件监听
    print("\n3. 设置事件监听...")
    
    def on_player_level_up(event):
        print(f"  [事件] 玩家升级到 {event.data['new_level']} 级！")
    
    def on_combat_start(event):
        print(f"  [事件] 战斗开始！遭遇 {event.data.get('enemy', {}).get('name', '未知敌人')}")
    
    event_dispatcher.subscribe('player_level_up', on_player_level_up)
    event_dispatcher.subscribe('combat_start', on_combat_start)
    print("✓ 事件监听器已注册")
    
    # 4. 初始化游戏
    print("\n4. 初始化游戏...")
    success = game_service.initialize_game("张三丰")
    if success:
        print("✓ 游戏初始化成功")
        print(f"  欢迎来到修仙世界，{player_service.get_current_player().name}！")
    else:
        print("✗ 游戏初始化失败")
        return
    
    # 5. 执行游戏命令
    print("\n5. 执行游戏命令...")
    
    commands = [
        "帮助",
        "状态",
        "地图",
        "探索",
        "修炼"
    ]
    
    for cmd in commands:
        print(f"\n> 执行命令: {cmd}")
        result = game_service.process_command(cmd)
        print(f"  结果: {result.output[:100]}{'...' if len(result.output) > 100 else ''}")
        
        if result.suggestions:
            print(f"  建议: {result.suggestions}")
    
    # 6. 查看游戏状态
    print("\n6. 查看游戏状态...")
    state = game_service.get_game_state()
    print(f"  游戏时间: {game_service.get_game_time():.2f} 秒")
    print(f"  当前位置: {state.current_location}")
    print(f"  是否战斗: {state.in_combat}")
    
    # 7. 查看日志统计
    print("\n7. 查看日志统计...")
    log_stats = log_service.get_log_statistics()
    print(f"  总日志数: {log_stats['total_logs']}")
    print(f"  日志分类: {log_stats['logs_by_category']}")
    
    # 8. 查看事件统计
    print("\n8. 查看事件统计...")
    event_stats = event_dispatcher.get_statistics()
    print(f"  总事件数: {event_stats.total_events}")
    print(f"  事件类型: {event_stats.events_by_type}")
    
    # 9. 保存游戏
    print("\n9. 保存游戏...")
    save_success = game_service.save_game("测试存档")
    print(f"✓ 游戏保存{'成功' if save_success else '失败'}")
    
    print("\n=== 示例完成 ===")


def example_custom_command():
    """自定义命令示例"""
    print("\n=== 自定义命令示例 ===\n")
    
    container = ServiceContainer()
    register_services(container)
    
    command_engine = container.resolve(ICommandEngine)
    
    # 定义自定义命令处理器
    from xwe.services.command_engine import CommandHandler, CommandContext, CommandResult
    
    class MeditateCommandHandler(CommandHandler):
        def __init__(self, container):
            super().__init__(
                commands=['打坐', 'meditate'],
                aliases=['冥想', '静坐'],
                description='进行深度冥想，恢复状态并获得感悟',
                usage='打坐 [时长]'
            )
            self.container = container
            
        def _do_handle(self, context: CommandContext) -> CommandResult:
            # 获取玩家服务
            player_service = self.container.resolve(IPlayerService)
            player = player_service.get_current_player()
            
            if not player:
                return CommandResult(
                    success=False,
                    output="未找到玩家信息"
                )
            
            # 计算冥想效果
            duration = int(context.args[0]) if context.args else 60
            mana_restore = min(duration * 0.5, player.max_mana - player.mana)
            exp_gain = duration * 0.1
            
            # 恢复灵力
            player_service.restore_mana(int(mana_restore))
            
            # 获得经验
            result = player_service.add_experience(int(exp_gain))
            
            output = f"你静坐冥想了 {duration} 秒。\n"
            output += f"恢复了 {int(mana_restore)} 点灵力。\n"
            output += result['message']
            
            return CommandResult(
                success=True,
                output=output,
                state_changed=True,
                events=[{
                    'type': 'meditation_complete',
                    'duration': duration,
                    'mana_restored': mana_restore,
                    'exp_gained': exp_gain
                }]
            )
    
    # 注册自定义命令
    meditate_handler = MeditateCommandHandler(container)
    command_engine.register_handler(meditate_handler)
    
    # 初始化游戏
    game_service = container.resolve(IGameService)
    game_service.initialize_game("测试道友")
    
    # 测试自定义命令
    print("测试自定义命令...")
    result = command_engine.process_command("打坐 30")
    print(f"结果: {result.output}")
    
    # 测试别名
    result = command_engine.process_command("冥想")
    print(f"\n使用别名: {result.output}")


def example_event_driven():
    """事件驱动示例"""
    print("\n=== 事件驱动编程示例 ===\n")
    
    container = ServiceContainer()
    register_services(container)
    
    event_dispatcher = container.resolve(IEventDispatcher)
    log_service = container.resolve(ILogService)
    
    # 定义事件处理器
    class AchievementHandler:
        def __init__(self, log_service):
            self.log_service = log_service
            self.achievements = {}
            
        def on_enemy_defeated(self, event):
            player_id = event.data.get('player_id')
            enemy_type = event.data.get('enemy_type')
            
            # 记录击败数
            key = f"{player_id}:{enemy_type}"
            self.achievements[key] = self.achievements.get(key, 0) + 1
            
            # 检查成就
            if self.achievements[key] == 10:
                self.log_service.log_achievement(
                    f"获得成就：{enemy_type}杀手（击败10个{enemy_type}）",
                    player_id=player_id
                )
                
                # 发布成就事件
                event_dispatcher.dispatch_game_event(
                    'achievement_unlocked',
                    {
                        'player_id': player_id,
                        'achievement': f'{enemy_type}_slayer',
                        'count': 10
                    }
                )
    
    # 创建并注册处理器
    achievement_handler = AchievementHandler(log_service)
    event_dispatcher.subscribe('enemy_defeated', achievement_handler.on_enemy_defeated)
    
    # 模拟游戏事件
    print("模拟击败敌人...")
    for i in range(12):
        event_dispatcher.dispatch_combat_event(
            'enemy_defeated',
            {
                'player_id': 'player_001',
                'enemy_type': '妖兽',
                'enemy_level': 5
            }
        )
        
        if i == 9:  # 第10次
            print("  [成就解锁提示应该出现]")
    
    # 查看成就日志
    import time
    time.sleep(0.1)  # 等待异步处理
    
    from xwe.services.log_service import LogFilter, LogLevel
    filter = LogFilter(levels=[LogLevel.ACHIEVEMENT])
    achievement_logs = log_service.get_logs(filter=filter)
    
    print(f"\n成就日志 ({len(achievement_logs)} 条):")
    for log in achievement_logs:
        print(f"  - {log.message}")


if __name__ == "__main__":
    # 运行示例
    example_game_flow()
    example_custom_command()
    example_event_driven()
    
    print("\n✅ 所有示例运行完成！")
