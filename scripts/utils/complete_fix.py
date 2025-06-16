#!/usr/bin/env python3
# @dev_only
"""完整的修复和验证脚本 - 一键修复所有问题"""

import os
from typing import Any
import sys
import json

# 设置项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

print("=== 修仙世界引擎 - 完整修复脚本 ===\n")

# 1. 确保所有必要的目录存在
print("1. 创建所有必要的目录...")
required_dirs = [
    'xwe/data/npc',
    'xwe/data/templates', 
    'xwe/data/skills',
    'xwe/data/interaction',
    'xwe/data/character',
    'saves'
]

for dir_path in required_dirs:
    full_path = os.path.join(PROJECT_ROOT, dir_path)
    os.makedirs(full_path, exist_ok=True)
    print(f"  ✓ {dir_path}")

# 2. 确保所有必要的配置文件存在
print("\n2. 检查并创建必要的配置文件...")

# NLP配置文件
nlp_config_path = os.path.join(PROJECT_ROOT, 'xwe/data/interaction/nlp_config.json')
if not os.path.exists(nlp_config_path):
    nlp_config = {
        "enable_llm": False,
        "llm_provider": "mock",
        "fallback_to_rules": True,
        "cache_enabled": True,
        "cache_ttl": 300
    }
    with open(nlp_config_path, 'w', encoding='utf-8') as f:
        json.dump(nlp_config, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 创建 nlp_config.json")
else:
    print(f"  ✓ nlp_config.json 已存在")

# 3. 确保所有数据文件存在
print("\n3. 验证数据文件...")
data_files = {
    'xwe/data/npc/dialogues.json': '对话数据',
    'xwe/data/templates/character.json': '角色模板',
    'xwe/data/templates/npc.json': 'NPC模板',
    'xwe/data/templates/skill.json': '技能模板',
    'xwe/data/templates/item.json': '物品模板',
    'xwe/data/skills/martial_arts.json': '武技数据',
    'xwe/data/skills/spells.json': '法术数据',
    'xwe/data/skills/passive_skills.json': '被动技能数据',
    'xwe/data/character/character_creation.json': '角色创建配置'
}

all_files_ok = True
for file_path, desc in data_files.items():
    full_path = os.path.join(PROJECT_ROOT, file_path)
    if os.path.exists(full_path):
        print(f"  ✓ {desc}")
    else:
        print(f"  ❌ 缺失 {desc}: {file_path}")
        all_files_ok = False

# 4. 测试导入
print("\n4. 测试核心模块导入...")
try:
    from xwe.engine.expression import ExpressionParser
    print("  ✓ 表达式解析器")
    
    from xwe.core.data_loader import DataLoader
    print("  ✓ 数据加载器")
    
    from xwe.core.game_core import GameCore
    print("  ✓ 游戏核心")
    
    from xwe.world import WorldMap, LocationManager, EventSystem
    print("  ✓ 世界系统")
    
    from xwe.npc import NPCManager, DialogueSystem, TradingSystem
    print("  ✓ NPC系统")
    
    # 5. 创建游戏实例测试
    print("\n5. 创建游戏实例测试...")
    game = GameCore()
    print("  ✓ GameCore 实例创建成功")
    
    # 6. 启动新游戏测试
    print("\n6. 启动新游戏测试...")
    game.start_new_game("测试玩家")
    print("  ✓ 新游戏启动成功")
    
    # 获取初始输出
    output = game.get_output()
    if output:
        print("  ✓ 游戏输出正常")
        print("\n  游戏输出示例:")
        for line in output[:3]:
            print(f"    {line}")
    
    # 7. 测试基本命令
    print("\n7. 测试基本命令...")
    test_commands = [
        ("状态", "角色状态"),
        ("技能", "技能列表"),
        ("地图", "当前位置"),
        ("帮助", "可用命令")
    ]
    
    all_commands_ok = True
    for cmd, expected_text in test_commands:
        game.process_command(cmd)
        output = game.get_output()
        if any(expected_text in line for line in output):
            print(f"  ✓ {cmd} 命令正常")
        else:
            print(f"  ❌ {cmd} 命令异常")
            all_commands_ok = False
    
    # 8. 测试自然语言处理
    print("\n8. 测试自然语言处理...")
    nlp_tests = [
        "我想看看我的状态",
        "查看地图",
        "我要修炼一会儿"
    ]
    
    for test_input in nlp_tests:
        game.process_command(test_input)
        output = game.get_output()
        if output and not any("不太明白" in line for line in output):
            print(f"  ✓ \"{test_input}\" 理解正确")
        else:
            print(f"  ⚠️  \"{test_input}\" 可能未正确理解")
    
    # 总结
    print("\n" + "="*50)
    if all_files_ok and all_commands_ok:
        print("✅ 修复完成！游戏可以正常运行！")
        print("\n运行游戏:")
        print("  python play_demo.py  (推荐，有使用提示)")
        print("  python main.py")
        print("  python start_game.py")
    else:
        print("⚠️  修复完成，但仍有一些问题需要注意")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n调试信息:")
    print(f"Python版本: {sys.version}")
    print(f"当前目录: {os.getcwd()}")
    print(f"Python路径: {sys.path[:3]}")

print("\n=== 修复脚本结束 ===")
