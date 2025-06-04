#!/usr/bin/env python3
"""
优化后的修仙世界引擎 - 快速启动
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xwe.core.game_core import GameCore
import time

def show_optimization_info():
    """显示优化信息"""
    print("\n" + "="*60)
    print("🐉 修仙世界引擎 - 优化版")
    print("="*60)
    print("\n✨ 已完成的优化：")
    print("1. 🐲 中国龙ASCII艺术 - 更有仙侠氛围")
    print("2. 📊 智能状态显示 - 只在需要时显示")
    print("3. 🏆 渐进式成就系统 - 根据行为解锁")
    print("4. 🎯 命令优先级系统 - 精确匹配核心命令")
    print("5. 📖 沉浸式事件系统 - 分步展示剧情")
    print("\n" + "="*60)
    time.sleep(2)

def main():
    """主函数"""
    # 显示优化信息
    show_optimization_info()
    
    print("\n准备进入游戏...")
    time.sleep(1)
    
    try:
        # 创建游戏实例
        game = GameCore()
        
        # 清屏（可选）
        # os.system('clear' if os.name == 'posix' else 'cls')
        
        # 开始新游戏
        print("\n请输入你的角色名（直接回车使用默认名字）：")
        player_name = input().strip()
        if not player_name:
            player_name = "无名侠客"
        
        game.start_new_game(player_name)
        
        # 主游戏循环
        while game.is_running():
            # 获取并显示输出
            output = game.get_output()
            for line in output:
                print(line)
            
            # 等待玩家输入
            try:
                user_input = input("\n> ").strip()
                if user_input:
                    game.process_command(user_input)
            except KeyboardInterrupt:
                print("\n\n检测到中断信号...")
                game.process_command("退出")
            except EOFError:
                print("\n\n游戏结束。")
                break
        
        # 游戏结束
        final_output = game.get_output()
        for line in final_output:
            print(line)
        
        print("\n感谢游玩优化版修仙世界引擎！")
        
    except Exception as e:
        print(f"\n❌ 游戏出错：{e}")
        import traceback
        traceback.print_exc()
        print("\n如果遇到问题，请检查：")
        print("1. 是否所有依赖都已安装")
        print("2. 是否在项目根目录运行")
        print("3. Python版本是否为3.8+")

if __name__ == "__main__":
    main()
