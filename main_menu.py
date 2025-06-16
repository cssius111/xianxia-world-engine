#!/usr/bin/env python
"""
修仙世界引擎 - 增强版主菜单
包含Roll系统和其他功能入口
"""

import sys
from pathlib import Path
import argparse

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from xwe.core import GameCore
from xwe.core.roll_system import CharacterRoller
import json
import os


def clear_screen():
    """清屏"""
    os.system('clear' if os.name == 'posix' else 'cls')


def show_main_menu():
    """显示主菜单"""
    print("\n" + "="*60)
    print("                   修仙世界引擎")
    print("                XianXia World Engine")
    print("="*60)
    print("\n1. 开始新游戏")
    print("2. 开局Roll系统（无限重置角色）")
    print("3. 测试Roll系统")
    print("4. 测试NLP功能")
    print("5. 继续游戏（开发中）")
    print("6. 设置")
    print("7. 退出")
    print("\n" + "="*60)
    
    choice = input("\n请选择 (1-7): ").strip()
    return choice


def start_new_game(game_mode: str) -> None:
    """普通开始游戏"""
    game = GameCore(game_mode=game_mode)
    if game_mode != "player":
        print(f"\n[开发者模式] 当前模式: {game_mode}")
    
    # 获取玩家名字
    player_name = input("请输入你的名字: ").strip() or "无名侠客"
    
    # 开始新游戏
    game.start_new_game(player_name)
    
    # 游戏主循环
    while game.is_running():
        # 显示输出
        output = game.get_output()
        for line in output:
            print(line)
        
        # 等待输入
        user_input = input("> ").strip()
        if user_input:
            game.process_command(user_input)
    
    # 显示最终输出
    output = game.get_output()
    for line in output:
        print(line)


def start_with_roll(game_mode: str) -> None:
    """带Roll的新游戏"""
    print("\n=== 开局Roll系统 ===")
    print("你可以无限次重置角色，直到满意为止！")
    if game_mode != "player":
        print(f"[开发者模式] 当前模式: {game_mode}")
    
    roller = CharacterRoller()
    
    while True:
        print("\n正在生成角色...")
        character = roller.roll()
        
        # 显示完整面板
        print(character.display())
        
        choice = input("\n使用这个角色开始游戏吗？(y/n): ").strip().lower()
        
        if choice == 'y':
            print("\n正在准备游戏...")
            print("（提示：Roll系统已集成到主游戏中）")
            
            # 创建游戏并设置角色名
            player_name = input("\n请输入角色名: ").strip() or character.name
            
            # 开始新游戏（会自动进入Roll流程）
            game = GameCore(game_mode=game_mode)
            game.start_new_game(player_name)
            
            # 游戏主循环
            while game.is_running():
                # 显示输出
                output = game.get_output()
                for line in output:
                    print(line)
                
                # 等待输入
                user_input = input("> ").strip()
                if user_input:
                    game.process_command(user_input)
            
            # 显示最终输出
            output = game.get_output()
            for line in output:
                print(line)
            
            break


def test_roll_system():
    """测试Roll系统"""
    clear_screen()
    from scripts.simple_roll import main as roll_main
    roll_main()


def test_nlp_system():
    """测试NLP系统"""
    clear_screen()
    from scripts.test_nlp import main as nlp_main
    nlp_main()


def show_settings():
    """显示设置"""
    print("\n=== 设置 ===")
    
    # 检查API密钥
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print("\nAPI配置状态：")
    print(f"- DeepSeek API: {'已配置' if deepseek_key else '未配置'}")
    print(f"- OpenAI API: {'已配置' if openai_key else '未配置'}")
    
    # 检查NLP配置
    config_path = Path(__file__).parent.parent / "xwe/data/interaction/nlp_config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"\n当前NLP配置：")
        print(f"- 提供者: {config.get('llm_provider', 'mock')}")
        print(f"- 启用状态: {config.get('enable_llm', False)}")
    
    print("\n设置API密钥：")
    print("export DEEPSEEK_API_KEY='your_api_key'")
    print("export OPENAI_API_KEY='your_api_key'")
    
    input("\n按Enter返回主菜单...")


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="player", help="game mode: player or dev")
    args = parser.parse_args()

    game_mode = args.mode

    while True:
        clear_screen()
        choice = show_main_menu()

        if choice == '1':
            start_new_game(game_mode)

        elif choice == '2':
            start_with_roll(game_mode)
            
        elif choice == '3':
            test_roll_system()
            
        elif choice == '4':
            test_nlp_system()
            
        elif choice == '5':
            print("\n继续游戏功能开发中...")
            input("按Enter返回主菜单...")
            
        elif choice == '6':
            show_settings()
            
        elif choice == '7':
            print("\n感谢游玩，再见！")
            break
            
        else:
            print("\n无效的选择，请重新输入")
            input("按Enter继续...")


if __name__ == "__main__":
    main()
