#!/usr/bin/env python3
"""
一键修复并启动 - 自动执行所有修复步骤并启动项目
"""

import subprocess
import sys
import time
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'=' * 60}")
    print(f"🚀 {description}")
    print(f"{'=' * 60}")
    
    try:
        result = subprocess.run(
            [sys.executable, cmd],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"\n⚠️ 警告:\n{result.stderr}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """主函数"""
    print("🔧 一键修复并启动")
    print("=" * 60)
    print("这个脚本将自动:")
    print("1. 清理项目")
    print("2. 修复所有问题")
    print("3. 启动Web服务器")
    print("\n开始执行...\n")
    
    # 步骤1：清理
    if not run_command("cleanup.py", "步骤 1/3: 清理项目"):
        print("\n⚠️ 清理步骤出现问题，继续执行...")
    
    time.sleep(1)  # 短暂等待
    
    # 步骤2：修复
    if not run_command("complete_fix.py", "步骤 2/3: 完整修复"):
        print("\n❌ 修复失败！")
        print("\n请手动检查:")
        print("1. 查看 project_snapshot.json")
        print("2. 确保所有依赖已安装: pip install -r requirements.txt")
        return
    
    time.sleep(1)  # 短暂等待
    
    # 步骤3：启动
    print("\n" + "=" * 60)
    print("🎉 修复完成！正在启动服务器...")
    print("=" * 60)
    
    run_command("quick_start.py", "步骤 3/3: 启动Web服务器")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
