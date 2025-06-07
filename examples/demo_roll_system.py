#!/usr/bin/env python3
"""
开局 Roll 系统演示脚本

可以直接运行此脚本体验角色重骰功能。
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xwe.core.roll_system import CharacterRoller


def main():
    """主函数"""
    print("="*80)
    print("欢迎使用【修仙世界引擎 - 开局Roll系统】")
    print("="*80)
    print()
    
    roller = CharacterRoller()
    current_result = None
    
    while True:
        print("请选择操作：")
        print("1. Roll一个新角色")
        print("2. 显示当前角色详情")
        print("3. 批量Roll（10次）")
        print("4. Roll直到出现SSS级")
        print("5. 查看统计信息")
        print("0. 退出")
        print()
        
        choice = input("请输入选项（0-5）：").strip()
        
        if choice == '0':
            print("感谢使用，再见！")
            break
            
        elif choice == '1':
            print("\n正在Roll新角色...\n")
            current_result = roller.roll()
            print(current_result.display())
            print()
            
            # 询问是否满意
            while True:
                satisfied = input("是否满意这个角色？(y/n): ").strip().lower()
                if satisfied == 'y':
                    print("恭喜！祝您游戏愉快！")
                    break
                elif satisfied == 'n':
                    print("\n重新Roll中...\n")
                    current_result = roller.roll()
                    print(current_result.display())
                    print()
                else:
                    print("请输入 y 或 n")
                    
        elif choice == '2':
            if current_result:
                print("\n当前角色详情：")
                print(current_result.display())
                print()
            else:
                print("\n还没有Roll角色，请先选择选项1\n")
                
        elif choice == '3':
            print("\n批量Roll 10次，显示简要信息：\n")
            results = roller.multi_roll(10)
            
            print(f"{'序号':<4} {'姓名':<8} {'评级':<15} {'灵根':<10} {'命格':<12} {'系统':<12}")
            print("-" * 70)
            
            for i, result in enumerate(results, 1):
                system_name = result.system['name'] if result.system else "无"
                print(f"{i:<4} {result.name:<8} {result.overall_rating:<15} "
                      f"{result.spiritual_root_type:<10} {result.destiny:<12} {system_name:<12}")
            print()
            
        elif choice == '4':
            print("\n尝试Roll出SSS级角色（最多尝试1000次）...\n")
            attempts = 0
            
            from xwe.core.roll_system.character_roller import roll_until_satisfied
            
            def is_sss(result):
                nonlocal attempts
                attempts += 1
                if attempts % 100 == 0:
                    print(f"已尝试 {attempts} 次...")
                return result.overall_rating.startswith("SSS")
            
            sss_result = roll_until_satisfied(is_sss, 1000)
            
            if sss_result:
                print(f"\n成功！在第 {attempts} 次roll出了SSS级角色！\n")
                print(sss_result.display())
            else:
                print(f"\n很遗憾，尝试了1000次都没有roll出SSS级角色。")
                print("SSS级角色极其稀有，请继续努力！")
            print()
            
        elif choice == '5':
            stats = roller.get_statistics()
            print("\n统计信息：")
            print(f"本次会话总Roll次数：{stats['total_rolls']}")
            print("\n可用内容：")
            for key, value in stats['features'].items():
                print(f"  {key}：{value} 种")
            print()
            
        else:
            print("\n无效的选项，请重新输入。\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被中断，再见！")
    except Exception as e:
        print(f"\n发生错误：{e}")
        import traceback
        traceback.print_exc()
