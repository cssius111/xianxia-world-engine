"""
GameOrchestrator 演示

展示如何使用游戏协调器运行完整的游戏
"""

import asyncio
from pathlib import Path
import sys
import logging

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from xwe.core.orchestrator import (
    GameOrchestrator, GameConfig, GameMode,
    create_game, run_game
)
from xwe.core.command.handlers.launcher_handler import GameLauncherHandler


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('game_demo.log'),
            logging.StreamHandler()
        ]
    )


def demo_basic_game():
    """基础游戏演示"""
    print("\n=== 基础游戏演示 ===\n")
    
    # 使用默认配置运行游戏
    config = GameConfig(
        game_name="仙侠世界 - 演示版",
        enable_html=True,  # 启用HTML输出
        debug_mode=True,   # 调试模式
    )
    
    # 创建游戏
    game = create_game(config)
    
    # 添加启动器命令处理器
    async def setup_launcher(orchestrator):
        """设置启动器"""
        launcher = GameLauncherHandler(orchestrator)
        orchestrator.command_processor.register_handler(launcher)
        print("启动器命令已注册")
    
    game.add_startup_hook(setup_launcher)
    
    # 运行游戏
    print("开始运行游戏...")
    print("提示：")
    print("- 输入 '新游戏 <角色名>' 创建新角色")
    print("- 输入 '继续' 加载最新存档")
    print("- 输入 '帮助' 查看所有命令")
    print("- 输入 '退出' 结束游戏\n")
    
    game.run_sync()


def demo_custom_config():
    """自定义配置演示"""
    print("\n=== 自定义配置演示 ===\n")
    
    # 创建自定义配置
    config = GameConfig(
        game_mode=GameMode.DEV,
        game_name="仙侠世界 - 开发版",
        version="2.0.0-dev",
        
        # 路径配置
        save_dir=Path("custom_saves"),
        log_dir=Path("custom_logs"),
        
        # 输出配置
        enable_console=True,
        enable_file_log=True,
        enable_html=True,
        console_colored=True,
        
        # 命令配置
        enable_command_log=True,
        enable_cooldown=False,  # 开发模式关闭冷却
        enable_rate_limit=False,  # 开发模式关闭限流
        
        # 自动保存
        auto_save_enabled=True,
        auto_save_interval=60.0,  # 1分钟
        
        # 调试
        debug_mode=True,
        show_traceback=True,
    )
    
    # 保存配置
    config_file = Path("game_config.json")
    config.save_to_file(config_file)
    print(f"配置已保存到: {config_file}")
    
    # 从文件加载配置
    loaded_config = GameConfig.from_file(config_file)
    print(f"已加载配置: 游戏模式={loaded_config.game_mode.value}")
    
    # 使用配置创建游戏
    game = create_game(loaded_config)
    
    # 添加自定义钩子
    def on_startup(orchestrator):
        """启动时钩子"""
        print("=== 开发模式已启用 ===")
        print("- 命令无冷却时间")
        print("- 无速率限制") 
        print("- 显示调试信息")
    
    def on_command(orchestrator, command, result):
        """命令后钩子"""
        if result.success:
            print(f"[DEV] 命令成功: {command}")
        else:
            print(f"[DEV] 命令失败: {command} - {result.error}")
    
    game.add_startup_hook(on_startup)
    game.add_post_command_hook(on_command)
    
    # 运行游戏
    game.run_sync()


async def demo_async_game():
    """异步游戏演示"""
    print("\n=== 异步游戏演示 ===\n")
    
    # 创建游戏配置
    config = GameConfig(
        game_name="仙侠世界 - 异步版",
        game_mode=GameMode.SERVER,  # 服务器模式
    )
    
    # 创建游戏
    game = GameOrchestrator(config)
    
    # 自定义异步钩子
    async def async_startup_hook(orchestrator):
        """异步启动钩子"""
        print("执行异步启动任务...")
        await asyncio.sleep(1)  # 模拟异步操作
        print("异步启动完成")
        
        # 注册启动器
        launcher = GameLauncherHandler(orchestrator)
        orchestrator.command_processor.register_handler(launcher)
    
    async def periodic_task(orchestrator):
        """定期任务示例"""
        while orchestrator.running:
            await asyncio.sleep(30)  # 每30秒
            if orchestrator.get_player():
                orchestrator.output_manager.debug("[服务器] 定期任务执行")
    
    game.add_startup_hook(async_startup_hook)
    
    try:
        # 初始化
        await game.initialize()
        
        # 创建定期任务
        task = asyncio.create_task(periodic_task(game))
        
        # 运行游戏
        await game.run()
        
        # 取消定期任务
        task.cancel()
        
    except Exception as e:
        print(f"游戏错误: {e}")
        import traceback
        traceback.print_exc()


def demo_plugin_system():
    """插件系统演示"""
    print("\n=== 插件系统演示 ===\n")
    
    # 定义一个简单的插件
    class ExamplePlugin:
        """示例插件"""
        
        def __init__(self, name):
            self.name = name
        
        async def on_install(self, orchestrator):
            """安装时调用"""
            print(f"插件 {self.name} 正在安装...")
            
            # 添加自定义命令处理器
            from xwe.core.command import CommandHandler, CommandResult
            
            class PluginCommandHandler(CommandHandler):
                def __init__(self, plugin):
                    super().__init__(f"{plugin.name}_commands", [])
                    self.plugin = plugin
                
                def can_handle(self, context):
                    return context.raw_input.startswith("插件")
                
                def handle(self, context):
                    context.output_manager.info(f"来自插件 {self.plugin.name} 的问候！")
                    return CommandResult.success()
            
            handler = PluginCommandHandler(self)
            orchestrator.command_processor.register_handler(handler)
            
            # 添加命令别名
            orchestrator.command_processor.add_alias("pl", "插件")
            
            print(f"插件 {self.name} 安装完成")
        
        async def on_uninstall(self, orchestrator):
            """卸载时调用"""
            print(f"插件 {self.name} 已卸载")
    
    # 创建游戏
    config = GameConfig(
        game_name="仙侠世界 - 插件演示版",
        debug_mode=True,
    )
    
    game = create_game(config)
    
    # 创建插件
    plugin = ExamplePlugin("示例插件")
    
    # 安装插件（通过启动钩子）
    async def install_plugins(orchestrator):
        """安装插件"""
        await plugin.on_install(orchestrator)
        
        # 注册启动器
        launcher = GameLauncherHandler(orchestrator)
        orchestrator.command_processor.register_handler(launcher)
    
    game.add_startup_hook(install_plugins)
    
    # 运行游戏
    print("提示：输入 '插件' 或 'pl' 测试插件命令")
    game.run_sync()


def demo_game_scenarios():
    """游戏场景演示"""
    print("\n=== 游戏场景演示 ===\n")
    
    # 创建一个预设场景的游戏
    config = GameConfig(
        game_name="仙侠世界 - 场景演示",
        enable_html=True,
    )
    
    game = create_game(config)
    
    async def setup_demo_scenario(orchestrator):
        """设置演示场景"""
        # 注册启动器
        launcher = GameLauncherHandler(orchestrator)
        orchestrator.command_processor.register_handler(launcher)
        
        # 创建演示角色
        from xwe.core.character import Character, CharacterType
        
        # 创建一个高级角色用于演示
        demo_player = Character(
            name="演示道长",
            character_type=CharacterType.PLAYER
        )
        
        # 设置高级属性
        demo_player.attributes.level = 20
        demo_player.attributes.cultivation_level = 9  # 炼气期九层
        demo_player.attributes.max_health = 500
        demo_player.attributes.current_health = 500
        demo_player.attributes.max_mana = 200
        demo_player.attributes.current_mana = 200
        demo_player.attributes.attack_power = 100
        demo_player.attributes.defense = 50
        
        # 添加演示命令
        from xwe.core.command import CommandHandler, CommandResult, CommandPriority
        
        class DemoCommandHandler(CommandHandler):
            def __init__(self):
                super().__init__("demo_commands", [], CommandPriority.SYSTEM)
            
            def can_handle(self, context):
                cmd = context.raw_input.strip().lower()
                return cmd.startswith("演示")
            
            def handle(self, context):
                parts = context.raw_input.strip().split(maxsplit=1)
                
                if len(parts) < 2:
                    # 显示演示菜单
                    context.output_manager.menu([
                        "演示 战斗 - 进入战斗演示",
                        "演示 修炼 - 快速修炼演示",
                        "演示 探索 - 探索区域演示",
                        "演示 对话 - NPC对话演示",
                        "演示 交易 - 商店交易演示",
                    ], "演示场景")
                    return CommandResult.success()
                
                demo_type = parts[1].strip()
                
                if demo_type == "战斗":
                    return self._demo_combat(context)
                elif demo_type == "修炼":
                    return self._demo_cultivation(context)
                elif demo_type == "探索":
                    return self._demo_exploration(context)
                elif demo_type == "对话":
                    return self._demo_dialogue(context)
                elif demo_type == "交易":
                    return self._demo_trade(context)
                else:
                    context.output_manager.error(f"未知的演示类型: {demo_type}")
                    return CommandResult.failure("未知演示")
            
            def _demo_combat(self, context):
                """战斗演示"""
                # 设置玩家
                context.state_manager.set_player(demo_player)
                
                # 开始战斗
                context.state_manager.start_combat("demo_combat")
                context.output_manager.narrative("突然，一只凶猛的妖兽出现在你面前！")
                context.output_manager.combat("【炎魔兽】（等级15）向你发起攻击！")
                context.output_manager.system("进入战斗模式！可用命令：攻击、防御、使用技能、逃跑")
                
                return CommandResult.success("战斗演示开始")
            
            def _demo_cultivation(self, context):
                """修炼演示"""
                context.state_manager.set_player(demo_player)
                context.state_manager.set_location("灵气洞府")
                
                context.output_manager.narrative("你来到了灵气充沛的洞府，这里是绝佳的修炼场所。")
                context.output_manager.info("当前境界：炼气期九层（即将突破）")
                context.output_manager.system("可用命令：修炼、突破")
                
                return CommandResult.success("修炼演示开始")
            
            def _demo_exploration(self, context):
                """探索演示"""
                context.state_manager.set_player(demo_player)
                context.state_manager.set_location("神秘森林")
                
                context.output_manager.narrative("你进入了一片神秘的森林，这里似乎隐藏着许多秘密。")
                context.output_manager.info("发现了一些特殊地点：")
                context.output_manager.info("- 古老祭坛（北方）")
                context.output_manager.info("- 灵泉（东方）")
                context.output_manager.info("- 废弃洞穴（西方）")
                context.output_manager.system("可用命令：探索、去 <地点>、拾取")
                
                return CommandResult.success("探索演示开始")
            
            def _demo_dialogue(self, context):
                """对话演示"""
                context.state_manager.set_player(demo_player)
                
                context.output_manager.narrative("你遇到了一位神秘的老者。")
                context.output_manager.dialogue("神秘老者", "年轻人，我看你骨骼清奇，可愿意接受我的考验？")
                context.output_manager.menu([
                    "愿意接受考验",
                    "询问考验内容",
                    "婉言谢绝"
                ], "选择回应")
                
                # 进入对话状态
                context.state_manager.push_context(
                    context.state_manager.GameContext.DIALOGUE,
                    {'npc': '神秘老者'}
                )
                
                return CommandResult.success("对话演示开始")
            
            def _demo_trade(self, context):
                """交易演示"""
                context.state_manager.set_player(demo_player)
                
                context.output_manager.narrative("你来到了灵宝阁，这里出售各种修炼物资。")
                
                items = [
                    {"物品": "聚气丹", "价格": "100灵石", "效果": "增加50点修为"},
                    {"物品": "回春丹", "价格": "50灵石", "效果": "恢复100点生命"},
                    {"物品": "破障丹", "价格": "500灵石", "效果": "突破时成功率+20%"},
                    {"物品": "灵器长剑", "价格": "300灵石", "效果": "攻击力+30"},
                ]
                
                context.output_manager.system("=== 灵宝阁商品 ===")
                context.output_manager.output_table(items)
                context.output_manager.info(f"\n你的灵石：1000")
                context.output_manager.system("输入物品名称购买，输入 '离开' 结束交易")
                
                return CommandResult.success("交易演示开始")
        
        # 注册演示命令
        demo_handler = DemoCommandHandler()
        orchestrator.command_processor.register_handler(demo_handler)
        
        print("=== 演示场景已准备就绪 ===")
        print("可用演示命令：")
        print("- 演示 - 显示所有演示场景")
        print("- 演示 战斗")
        print("- 演示 修炼")
        print("- 演示 探索")
        print("- 演示 对话")
        print("- 演示 交易")
    
    game.add_startup_hook(setup_demo_scenario)
    
    # 运行游戏
    game.run_sync()


def main():
    """主函数"""
    print("=" * 60)
    print("GameOrchestrator 功能演示")
    print("=" * 60)
    
    demos = [
        ("1", "基础游戏", demo_basic_game),
        ("2", "自定义配置", demo_custom_config),
        ("3", "异步游戏", lambda: asyncio.run(demo_async_game())),
        ("4", "插件系统", demo_plugin_system),
        ("5", "游戏场景", demo_game_scenarios),
    ]
    
    print("\n请选择演示：")
    for num, name, _ in demos:
        print(f"{num}. {name}")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请输入选项 (0-5): ").strip()
            
            if choice == "0":
                print("退出演示")
                break
            
            for num, name, demo_func in demos:
                if choice == num:
                    print(f"\n{'='*20} {name} {'='*20}")
                    demo_func()
                    print("\n演示完成")
                    break
            else:
                print("无效的选项，请重新输入")
            
        except KeyboardInterrupt:
            print("\n\n中断，退出演示")
            break
        except Exception as e:
            print(f"演示出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # 设置日志
    setup_logging()
    
    # 运行演示
    main()
