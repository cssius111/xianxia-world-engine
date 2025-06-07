#!/usr/bin/env python3
"""
验证V3系统文件完整性
"""

import os
import sys

def check_files():
    """检查所有V3系统文件"""
    print("检查V3系统文件完整性...\n")
    
    # 定义需要检查的文件
    required_files = {
        "核心模块": [
            "xwe/core/data_manager_v3.py",
            "xwe/core/formula_engine.py",
            "xwe/core/cultivation_system.py",
            "xwe/core/combat_system_v3.py",
            "xwe/core/event_system_v3.py",
            "xwe/core/npc_system_v3.py"
        ],
        "主程序和工具": [
            "main_v3_data_driven.py",
            "test_data_driven_system.py",
            "example_v3_comprehensive.py",
            "run_v3.py"
        ],
        "文档": [
            "OPTIMIZATION_SUMMARY_V3.md",
            "README_V3.md"
        ]
    }
    
    all_good = True
    
    for category, files in required_files.items():
        print(f"[{category}]")
        for filepath in files:
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"  ✓ {filepath} ({size:,} bytes)")
            else:
                print(f"  ✗ {filepath} (缺失)")
                all_good = False
        print()
    
    # 检查数据文件
    print("[数据文件]")
    data_dir = "xwe/data/restructured"
    if os.path.exists(data_dir):
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        print(f"  ✓ 找到 {len(json_files)} 个JSON配置文件")
        
        # 显示几个关键文件
        key_files = ["formula_library.json", "cultivation_realm.json", "combat_system.json"]
        for filename in key_files:
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"    - {filename} ({size:,} bytes)")
    else:
        print(f"  ✗ 数据目录不存在: {data_dir}")
        all_good = False
    
    print("\n" + "="*50)
    if all_good:
        print("✅ 所有V3系统文件都已就绪！")
        print("\n下一步:")
        print("1. 运行测试: python test_data_driven_system.py")
        print("2. 查看示例: python example_v3_comprehensive.py")
        print("3. 启动游戏: python run_v3.py")
    else:
        print("❌ 部分文件缺失，请检查上述错误")
    print("="*50)
    
    return all_good


if __name__ == "__main__":
    success = check_files()
    sys.exit(0 if success else 1)
