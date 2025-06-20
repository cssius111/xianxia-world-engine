#!/usr/bin/env python3
# @dev_only
"""快速验证修复是否成功"""

import os
import sys

# 设置项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

print("验证修复...")
print("-" * 50)

try:
    # 测试导入
    print("1. 测试导入 NPCManager...")
    from xwe.npc.npc_manager import NPCManager

    print("   ✅ NPCManager 导入成功")

    print("\n2. 测试导入 GameCore...")
    from xwe.core.game_core import GameCore

    print("   ✅ GameCore 导入成功")

    print("\n3. 创建游戏实例...")
    game = GameCore()
    print("   ✅ 游戏实例创建成功")

    print("\n4. 启动新游戏...")
    game.start_new_game("测试玩家")
    print("   ✅ 新游戏启动成功")

    print("\n" + "=" * 50)
    print("✅ 修复成功！游戏现在可以正常运行！")
    print("\n运行游戏：")
    print("  python play_demo.py")
    print("  或")
    print("  python quick_start.py")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback

    traceback.print_exc()
