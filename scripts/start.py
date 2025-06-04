#!/usr/bin/env python3
"""最简单的启动脚本 - 直接运行游戏"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from xwe.core.game_core import GameCore
    from xwe.core import GameCore  # 备用导入方式
    
    print("=== 修仙世界引擎 ===")
    print("正在启动游戏...\n")
    
    # 直接运行主程序
    import main
    main.main()
    
except Exception as e:
    print(f"启动失败: {e}")
    print("\n请运行以下命令修复问题：")
    print("  python verify_fix.py")
    print("\n或者尝试运行演示版本：")
    print("  python play_demo.py")
