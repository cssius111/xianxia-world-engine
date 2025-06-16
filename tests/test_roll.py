#!/usr/bin/env python
"""
Roll系统测试脚本
用于演示和测试开局Roll系统
"""


# 添加项目路径

from xwe.core.roll_system import CharacterRoller
import time
import json


def display_banner():
    """显示欢迎横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                  修仙世界引擎 - 开局Roll系统              ║
    ║                                                          ║
    ║         每次Roll都会生成一个全新的随机角色面板            ║
    ║         包含灵根、命格、天赋、体质、系统等属性            ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def format_character_panel(character_data):
    """格式化角色面板显示"""
    # 兼容RollResult对象和字典
    if hasattr(character_data, 'display'):
        # 如果是RollResult对象，直接使用其display方法
        print(character_data.display())
        return

    # 如果是字典，转换格式
    if hasattr(character_data, 'to_dict'):
        character_data = character_data.to_dict()

    # 原有的显示逻辑（简化版）
    print("\n" + "="*60)
    print("【角色面板】")
    print("="*60)

    # 处理不同的数据格式
    if isinstance(character_data, dict):
        # 尝试从不同的键获取数据
        if '基础信息' in character_data:
            # to_dict()格式
            info = character_data['基础信息']
            print(f"\n姓名: {info.get('姓名', '未知')}")
            print(f"性别: {info.get('性别', '未知')}")
            print(f"身份: {info.get('身份', '未知')}")
        else:
            # 其他格式
            print(f"\n姓名: {character_data.get('name', '未知')}")
            print(f"性别: {character_data.get('gender', '未知')}")

        # 显示其他信息
        if '综合评价' in character_data:
            rating = character_data['综合评价']
            print(f"\n评级: {rating.get('总体评级', '未知')}")
            print(f"战斗力: {rating.get('战斗力', 0)}")

    print("\n" + "="*60)


def show_statistics(roll_count, best_character, best_score):
    """显示统计信息"""
    print("\n" + "="*50)
    print(f"【Roll统计】")
    print(f"总次数: {roll_count}")
    print(f"最高分: {best_score}")
    if best_character:
        print(f"最佳评级: {best_character['overall_rating']['rank']} - {best_character['overall_rating']['description']}")
    print("="*50)


def demo_mode():
    """演示模式 - 自动展示不同类型的角色"""
    print("\n=== 演示模式 ===")
    print("将生成5个角色展示系统的随机性")
    
    roller = CharacterRoller()
    
    for i in range(5):
        print(f"\n\n--- 角色 {i+1} ---")
        character = roller.roll()
        
        # 简化显示
        print(f"性别: {character.gender}")
        print(f"出身: {character.identity}")
        print(f"灵根: {character.spiritual_root_type} - {character.spiritual_root_desc}")
        print(f"体质: {character.physique.get('name', '凡体') if hasattr(character, 'physique') else '凡体'}")
        print(f"命格: {character.destiny}")
        print(f"天赋数量: {len(character.talents)}")
        print(f"系统: {character['system']['name'] if character['system'] else '无'}")
        print(f"评级: {character.overall_rating}")
        
        time.sleep(1)


def batch_statistics(count=1000):
    """批量统计模式"""
    print(f"\n=== 批量统计模式 ===")
    print(f"生成{count}个角色进行统计分析...\n")
    
    roller = CharacterRoller()
    
    # 统计数据
    rank_count = {"D": 0, "C": 0, "B": 0, "A": 0, "S": 0, "SS": 0, "SSS": 0}
    system_count = 0
    special_root_count = 0
    special_physique_count = 0
    tag_count = 0
    
    # 开始生成
    start_time = time.time()
    
    for i in range(count):
        character = roller.roll()
        
        # 统计评级
        rank = character.overall_rating.split()[0]
        if rank in rank_count:
            rank_count[rank] += 1
        
        # 统计系统
        if character.system:
            system_count += 1
        
        # 统计特殊灵根
        if hasattr(character, 'spiritual_root_quality') and character.spiritual_root_quality >= 7:
            special_root_count += 1
        
        # 统计特殊体质
        if hasattr(character, 'physique') and character.physique.get('rarity') in ['rare', 'legendary']:
            special_physique_count += 1
        
        # 统计特殊标签
        if character.special_tags:
            tag_count += 1
        
        # 进度显示
        if (i + 1) % 100 == 0:
            print(f"已完成: {i + 1}/{count}")
    
    # 计算耗时
    elapsed_time = time.time() - start_time
    
    # 显示结果
    print("\n【统计结果】")
    print(f"生成耗时: {elapsed_time:.2f}秒")
    print(f"平均速度: {count/elapsed_time:.0f}个/秒")
    
    print("\n评级分布:")
    for rank, num in rank_count.items():
        percentage = (num / count) * 100
        bar = '█' * int(percentage / 2)
        print(f"{rank:3s}: {num:4d} ({percentage:5.1f}%) {bar}")
    
    print(f"\n特殊属性出现率:")
    print(f"系统外挂: {system_count}/{count} ({system_count/count*100:.1f}%)")
    print(f"高品质灵根: {special_root_count}/{count} ({special_root_count/count*100:.1f}%)")
    print(f"特殊体质: {special_physique_count}/{count} ({special_physique_count/count*100:.1f}%)")
    print(f"特殊标签: {tag_count}/{count} ({tag_count/count*100:.1f}%)")


def interactive_mode():
    """交互模式 - 主要功能"""
    display_banner()
    
    roller = CharacterRoller()
    roll_count = 0
    best_character = None
    best_score = 0
    
    print("\n指令说明:")
    print("- 按Enter键进行Roll")
    print("- 输入 'best' 查看最佳记录")
    print("- 输入 'save' 保存当前角色")
    print("- 输入 'load' 加载角色")
    print("- 输入 'stat' 查看统计")
    print("- 输入 'q' 或 'quit' 退出")
    print("\n" + "-"*50)
    
    while True:
        command = input("\n按Enter开始Roll (或输入指令): ").strip().lower()
        
        if command in ['q', 'quit']:
            print("\n感谢使用，再见！")
            if best_character:
                print(f"\n你的最佳记录: {best_score}分 ({best_character['overall_rating']['rank']})")
            break
            
        elif command == 'best':
            if best_character:
                print("\n【最佳角色记录】")
                format_character_panel(best_character)
            else:
                print("\n还没有Roll过角色呢！")
            continue
            
        elif command == 'save':
            if roll_count > 0:
                # 获取最后一次roll的角色
                character = roller.roll()  # 这里应该保存上一次的结果
                filename = f"character_{int(time.time())}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(character.to_dict(), f, ensure_ascii=False, indent=2)
                print(f"\n角色已保存到: {filename}")
            else:
                print("\n还没有Roll过角色！")
            continue
            
        elif command == 'load':
            try:
                filename = input("请输入文件名: ").strip()
                with open(filename, 'r', encoding='utf-8') as f:
                    character = json.load(f)
                print("\n【加载的角色】")
                format_character_panel(character.to_dict())
            except Exception as e:
                print(f"\n加载失败: {e}")
            continue
            
        elif command == 'stat':
            show_statistics(roll_count, best_character, best_score)
            continue
            
        elif command == '':
            # 执行Roll
            print("\n正在Roll角色", end='')
            for _ in range(3):
                print(".", end='', flush=True)
                time.sleep(0.2)
            print()
            
            # 生成角色
            character = roller.roll()
            roll_count += 1
            
            # 显示结果
            format_character_panel(character.to_dict())
            
            # 更新最佳记录
            current_score = character.combat_power
            if current_score > best_score:
                best_score = current_score
                best_character = character.to_dict()
                print("\n🎉 恭喜！刷新了最高分记录！")
            
            # 特殊提示
            if 'SS' in character.overall_rating:
                print("\n✨ 哇！出现了超稀有的角色！")
            elif 'S级' in character.overall_rating and 'SS' not in character.overall_rating:
                print("\n⭐ 不错！这是个S级角色！")
                
            # 显示统计
            if roll_count % 10 == 0:
                show_statistics(roll_count, best_character, best_score)
        
        else:
            print(f"\n未知指令: {command}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="修仙世界引擎 - Roll系统测试")
    parser.add_argument("--demo", action="store_true", help="运行演示模式")
    parser.add_argument("--batch", type=int, help="批量生成并统计")
    parser.add_argument("--once", action="store_true", help="生成一个角色并退出")
    
    args = parser.parse_args()
    
    if args.demo:
        demo_mode()
    elif args.batch:
        batch_statistics(args.batch)
    elif args.once:
        roller = CharacterRoller()
        character = roller.roll()
        format_character_panel(character.to_dict())
    else:
        # 默认进入交互模式
        interactive_mode()


if __name__ == "__main__":
    main()
