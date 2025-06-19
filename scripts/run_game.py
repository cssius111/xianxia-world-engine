"""
快速启动游戏

直接运行此文件即可开始游戏
"""

from pathlib import Path
import sys

# 添加项目路径
# 当前文件位于 scripts/ 目录下，项目根目录为上一级
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from xwe.core.orchestrator import GameConfig, GameMode, run_game
from xwe.core.command.handlers.launcher_handler import GameLauncherHandler


def main():
    """主函数"""
    # 创建游戏配置
    config = GameConfig(
        game_name="仙侠世界",
        version="1.0.0",
        game_mode=GameMode.PLAYER,
        
        # 启用功能
        enable_console=True,
        enable_file_log=True,
        enable_html=True,  # 生成HTML实时显示
        console_colored=True,
        
        # 自动保存
        auto_save_enabled=True,
        auto_save_interval=300.0,  # 5分钟
        
        # 开发选项
        debug_mode=False,
        show_traceback=False,
    )
    
    # 创建游戏
    from xwe.core.orchestrator import GameOrchestrator
    game = GameOrchestrator(config)
    
    # 添加启动器支持
    def setup_launcher(orchestrator):
        """设置启动器命令"""
        launcher = GameLauncherHandler(orchestrator)
        orchestrator.command_processor.register_handler(launcher)
    
    game.add_startup_hook(setup_launcher)
    
    # 显示欢迎信息
    print("=" * 60)
    print("欢迎来到【仙侠世界】")
    print("=" * 60)
    print()
    print("这是一个文字修仙游戏，你将扮演一个修仙者，")
    print("在这个充满机遇与挑战的世界中追求长生之道。")
    print()
    print("快速开始：")
    print("1. 输入 '新游戏 <你的名字>' 创建角色")
    print("2. 输入 '继续' 加载上次的进度")
    print("3. 输入 '帮助' 查看游戏指令")
    print("4. 输入 '退出' 离开游戏")
    print()
    print("=" * 60)
    
    # 运行游戏
    try:
        game.run_sync()
    except KeyboardInterrupt:
        print("\n\n游戏被中断")
    except Exception as e:
        print(f"\n游戏出错: {e}")
        if config.show_traceback:
            import traceback
            traceback.print_exc()
    
    print("\n感谢游玩！")


if __name__ == "__main__":
    main()
