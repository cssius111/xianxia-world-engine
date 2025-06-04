#!/usr/bin/env python3
"""一键修复并运行游戏 - 增强版"""

import os
import sys
import subprocess

# 设置项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

print("=== 修仙世界引擎 - 一键启动 ===\n")

# 步骤1：快速验证修复
print("步骤1：验证修复...")
verify_result = subprocess.run(
    [sys.executable, os.path.join(PROJECT_ROOT, "scripts/utils/verify_fix.py")],
    capture_output=True,
    text=True
)

if "✅ 修复成功！" in verify_result.stdout:
    print("✅ 验证通过！")
    print(verify_result.stdout)
    
    # 步骤2：启动游戏
    print("\n步骤2：启动游戏...\n")
    print("="*50)
    
    # 运行游戏
    subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "scripts/quick_start.py")])
    
else:
    print("❌ 验证失败")
    print("\n输出：")
    print(verify_result.stdout)
    if verify_result.stderr:
        print("\n错误信息：")
        print(verify_result.stderr)
    
    print("\n尝试运行完整修复...")
    # 运行完整修复
    fix_result = subprocess.run(
        [sys.executable, os.path.join(PROJECT_ROOT, "scripts/utils/complete_fix.py")],
        capture_output=True,
        text=True
    )
    
    print("\n修复输出：")
    print(fix_result.stdout)
    
    print("\n请手动运行以下命令：")
    print("  python verify_fix.py")
    print("  python quick_start.py")
