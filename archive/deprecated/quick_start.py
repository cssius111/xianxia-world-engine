#!/usr/bin/env python3
"""修仙世界引擎 - 快速启动器（已修复版）"""

import os
import sys

# 确保在正确的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
os.chdir(project_dir)
sys.path.insert(0, project_dir)

print("修仙世界引擎 - 正在启动...")
print("-" * 50)

try:
    # 直接导入并运行
    from xwe.core.game_core import GameCore
    
    # 创建简单的游戏界面
    class SimpleGame:
        def __init__(self):
            self.game = GameCore()
            
        def run(self):
            print("\n=== 欢迎来到修仙世界 ===")
            print("一个充满机遇与挑战的东方玄幻世界")
            print("\n提示：")
            print("- 输入 '帮助' 查看所有命令")
            print("- 输入 '地图' 查看当前位置")
            print("- 输入 '探索' 探索周围环境")
            print("- 支持自然语言，如 '我想看看周围有什么'")
            print("-" * 50)
            
            # 获取玩家名
            player_name = input("\n请输入你的角色名（直接回车使用默认）: ").strip()
            if not player_name:
                player_name = "无名侠客"
            
            # 开始游戏
            self.game.start_new_game(player_name)
            
            # 主循环
            while self.game.is_running():
                # 显示输出
                output = self.game.get_output()
                for line in output:
                    print(line)
                
                # 获取输入
                try:
                    command = input("\n> ").strip()
                    
                    if command.lower() in ['quit', 'exit', '退出']:
                        print("\n感谢游玩，再见！")
                        break
                    
                    self.game.process_command(command)
                    
                except KeyboardInterrupt:
                    print("\n\n游戏已退出")
                    break
                except Exception as e:
                    print(f"命令处理错误: {e}")
    
    # 运行游戏
    game = SimpleGame()
    game.run()
    
except Exception as e:
    print(f"\n启动失败: {e}")
    print("\n可能的解决方案：")
    print("1. 运行修复脚本: python complete_fix.py")
    print("2. 检查Python版本是否为3.8+")
    print("3. 确保在项目根目录运行")
    
    # 打印详细错误信息
    import traceback
    print("\n详细错误信息:")
    traceback.print_exc()
