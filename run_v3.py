#!/usr/bin/env python3
"""
修仙世界引擎 V3 - 快速启动脚本
一键启动数据驱动版本的游戏
"""

import os
import sys
import argparse

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    
    required_packages = ['requests', 'psutil']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少依赖包: {', '.join(missing_packages)}")
        print(f"请运行: pip install {' '.join(missing_packages)}")
        return False
    
    print("✓ 依赖检查通过")
    return True


def check_data_files():
    """检查数据文件"""
    print("\n检查数据文件...")
    
    data_dir = os.path.join(project_root, "xwe", "data", "restructured")
    
    if not os.path.exists(data_dir):
        print(f"✗ 数据目录不存在: {data_dir}")
        return False
    
    required_files = [
        "attribute_model.json",
        "formula_library.json",
        "cultivation_realm.json",
        "combat_system.json",
        "event_template.json",
        "npc_template.json"
    ]
    
    missing_files = []
    for filename in required_files:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
    
    if missing_files:
        print(f"✗ 缺少数据文件: {', '.join(missing_files)}")
        return False
    
    print("✓ 数据文件检查通过")
    return True


def run_tests():
    """运行测试"""
    print("\n运行系统测试...")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "test_data_driven_system.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ 所有测试通过")
            return True
        else:
            print("✗ 测试失败")
            print(result.stdout)
            print(result.stderr)
            return False
    
    except Exception as e:
        print(f"✗ 运行测试时出错: {e}")
        return False


def run_example():
    """运行示例"""
    print("\n运行综合示例...")
    
    try:
        import subprocess
        subprocess.run([sys.executable, "example_v3_comprehensive.py"])
    except Exception as e:
        print(f"运行示例时出错: {e}")


def run_game():
    """运行游戏"""
    print("\n启动游戏...")
    
    try:
        import subprocess
        subprocess.run([sys.executable, "main_v3_data_driven.py"])
    except Exception as e:
        print(f"启动游戏时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="修仙世界引擎 V3 快速启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_v3.py              # 运行完整检查并启动游戏
  python run_v3.py --test       # 仅运行测试
  python run_v3.py --example    # 运行示例
  python run_v3.py --skip-tests # 跳过测试直接启动游戏
        """
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="仅运行测试"
    )
    
    parser.add_argument(
        "--example",
        action="store_true",
        help="运行综合示例"
    )
    
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="跳过测试直接启动游戏"
    )
    
    parser.add_argument(
        "--no-check",
        action="store_true",
        help="跳过所有检查"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("修仙世界引擎 V3 - 数据驱动版本")
    print("="*60)
    
    # 执行检查
    if not args.no_check:
        if not check_dependencies():
            print("\n请先安装缺少的依赖")
            return 1
        
        if not check_data_files():
            print("\n请确保所有数据文件都存在")
            return 1
    
    # 根据参数执行不同操作
    if args.test:
        # 仅运行测试
        if run_tests():
            print("\n测试完成！")
            return 0
        else:
            return 1
    
    elif args.example:
        # 运行示例
        run_example()
        return 0
    
    else:
        # 正常启动流程
        if not args.skip_tests and not args.no_check:
            if not run_tests():
                print("\n测试未通过，是否继续？(y/n): ", end="")
                if input().lower() != 'y':
                    return 1
        
        # 启动游戏
        run_game()
        return 0


if __name__ == "__main__":
    sys.exit(main())
