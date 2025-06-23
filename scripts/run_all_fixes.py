#!/usr/bin/env python3
"""
快速运行所有修复和验证步骤
"""

import os
import sys
import subprocess
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'=' * 60}")
    print(f"🚀 {description}")
    print(f"{'=' * 60}")
    
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=str(project_root),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"\n❌ 错误输出:\n{result.stderr}")
    
    return result.returncode == 0

def main():
    """主函数"""
    print("🔧 开始执行完整的修复和验证流程...")
    
    # 1. 运行快速快照
    if not run_command(
        f"{sys.executable} scripts/quick_snapshot.py",
        "生成项目快照"
    ):
        print("⚠️ 快照生成失败，继续执行...")
    
    # 2. 运行综合修复
    if not run_command(
        f"{sys.executable} scripts/comprehensive_fix.py",
        "运行综合修复"
    ):
        print("⚠️ 综合修复遇到问题，继续执行...")
    
    # 3. 运行导入测试
    if not run_command(
        f"{sys.executable} scripts/check_imports.py",
        "测试模块导入"
    ):
        print("⚠️ 导入测试失败")
    
    # 4. 运行最终验证
    if not run_command(
        f"{sys.executable} scripts/final_verification.py",
        "最终验证"
    ):
        print("⚠️ 最终验证失败")
    
    print("\n" + "=" * 60)
    print("✅ 所有步骤执行完毕！")
    print("\n📌 接下来你可以:")
    print("1. 查看 project_snapshot.json 了解当前状态")
    print("2. 查看 fix_report.json 了解修复详情")
    print("3. 运行 python entrypoints/run_web_ui_optimized.py 启动游戏")

if __name__ == "__main__":
    main()
