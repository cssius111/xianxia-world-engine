#!/usr/bin/env python3
"""
快速验证游戏是否能启动
"""

import sys

print("🎮 修仙世界引擎 - 快速验证")
print("=" * 40)

try:
    print("导入游戏模块...", end="", flush=True)
    from run import app
    print(" ✅")
    
    print("检查Flask应用...", end="", flush=True)
    assert app is not None
    print(" ✅")
    
    print("检查核心模块...", end="", flush=True)
    from xwe.core.game_core import GameCore
    print(" ✅")
    
    print("创建游戏实例...", end="", flush=True)
    game = GameCore()
    print(" ✅")
    
    print("\n" + "=" * 40)
    print("✅ 游戏可以正常启动！")
    print("\n运行游戏:")
    print("  python run.py")
    print("\n然后访问:")
    print("  http://localhost:5001")
    print("=" * 40)
    
except Exception as e:
    print(" ❌")
    print(f"\n错误: {e}")
    print("\n请检查错误信息并修复问题")
    sys.exit(1)
