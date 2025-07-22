#!/usr/bin/env python3
"""
运行所有测试并生成报告
"""

import os
import subprocess
import sys


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'=' * 60}")
    print(f"🔍 {description}")
    print(f"{'=' * 60}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("错误输出:")
        print(result.stderr)

    return result.returncode == 0


def main():
    """主函数"""
    print("🧪 修仙世界引擎 - 测试套件")
    print("=" * 60)

    all_passed = True

    # 安装依赖
    if not run_command("pip install -r requirements.txt", "安装Python依赖"):
        return 1

    # 1. 检查导入
    if os.path.exists("check_imports.py"):
        if not run_command("python check_imports.py", "检查模块导入"):
            print("\n❌ 导入检查失败，请先修复导入错误")
            return 1

    # 2. 安装 Playwright 浏览器及依赖
    skip_pw_install = os.getenv("SKIP_PLAYWRIGHT_INSTALL", "false").lower() in {
        "1",
        "true",
        "yes",
    }
    if not skip_pw_install:
        if not run_command("npx playwright install --with-deps", "安装 Playwright 浏览器依赖"):
            print("\n⚠️  Playwright 安装失败，继续执行测试")
    else:
        print("跳过 Playwright 安装步骤")

    # 3. 运行 pytest（只在 tests 目录）
    if not run_command("pytest tests/ -v", "运行单元测试"):
        all_passed = False

    # 4. 生成覆盖率报告（可选）
    # run_command("pytest tests/ --cov=src/xwe --cov-report=html", "生成覆盖率报告")

    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 有测试失败，请检查上面的输出")
        return 1


if __name__ == "__main__":
    sys.exit(main())
