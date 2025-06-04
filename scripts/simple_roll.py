#!/usr/bin/env python
"""
简单的Roll系统测试 - 立即可用版本
直接测试Roll功能，无需复杂的格式化
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xwe.core.roll_system import CharacterRoller
import time


def simple_roll():
    """简单的Roll测试"""
    print("="*60)
    print("修仙世界引擎 - Roll系统（简化版）")
    print("="*60)
    
    roller = CharacterRoller()
    
    while True:
        command = input("\n按Enter进行Roll (输入'q'退出): ").strip().lower()
        
        if command == 'q':
            print("再见！")
            break
        
        # 执行Roll
        print("\n正在Roll...")
        result = roller.roll()
        
        # 使用内置的display方法
        print(result.display())
        
        # 显示一些额外信息
        if result.system:
            print(f"\n🎊 恭喜！获得了{result.system['rarity']}系统！")
        
        if "SSS" in result.overall_rating:
            print("\n🌟 超稀有！SSS级角色！")
        elif "SS" in result.overall_rating:
            print("\n✨ 稀有！SS级角色！")
        elif "S级" in result.overall_rating:
            print("\n⭐ 优秀！S级角色！")


def demo_roll(count=5):
    """演示Roll"""
    print(f"\n演示模式 - 生成{count}个角色")
    print("="*60)
    
    roller = CharacterRoller()
    
    for i in range(count):
        print(f"\n--- 第{i+1}个角色 ---")
        result = roller.roll()
        
        # 简单显示
        print(f"姓名: {result.name}")
        print(f"身份: {result.identity}")
        print(f"灵根: {result.spiritual_root_type}")
        print(f"命格: {result.destiny} ({result.destiny_rarity})")
        print(f"天赋数: {len(result.talents)}")
        print(f"系统: {'有' if result.system else '无'}")
        print(f"评级: {result.overall_rating}")
        print(f"战力: {result.combat_power}")
        
        time.sleep(0.5)


def batch_test(count=100):
    """批量测试统计"""
    print(f"\n批量测试 - 生成{count}个角色进行统计")
    
    roller = CharacterRoller()
    
    # 统计
    ratings = {}
    system_count = 0
    
    print("生成中", end='')
    for i in range(count):
        if i % 10 == 0:
            print(".", end='', flush=True)
        
        result = roller.roll()
        
        # 统计评级
        rating = result.overall_rating.split()[0]  # 获取评级部分
        ratings[rating] = ratings.get(rating, 0) + 1
        
        # 统计系统
        if result.system:
            system_count += 1
    
    print("\n\n统计结果：")
    print(f"总数: {count}")
    print(f"系统出现率: {system_count}/{count} ({system_count/count*100:.1f}%)")
    print("\n评级分布:")
    for rating, num in sorted(ratings.items()):
        percent = num / count * 100
        bar = '█' * int(percent / 2)
        print(f"{rating:4s}: {num:3d} ({percent:5.1f}%) {bar}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="简单Roll系统测试")
    parser.add_argument("--demo", action="store_true", help="演示模式")
    parser.add_argument("--batch", type=int, help="批量测试")
    parser.add_argument("--once", action="store_true", help="Roll一次")
    
    args = parser.parse_args()
    
    if args.demo:
        demo_roll()
    elif args.batch:
        batch_test(args.batch)
    elif args.once:
        roller = CharacterRoller()
        result = roller.roll()
        print(result.display())
    else:
        # 默认交互模式
        simple_roll()


if __name__ == "__main__":
    main()
