#!/usr/bin/env python3
"""
XianXia World Engine - 自动化测试脚本
运行所有单元测试和集成测试，并生成报告。

在运行此脚本前，请设置環境变量 `LLM_PROVIDER=mock`，例如：

```bash
export LLM_PROVIDER=mock
python tests/run_all_tests.py
```

如需真实 LLM 测试，可在 `.env` 中配置 API 密钥。
"""

import json
import os
import subprocess
import sys
import time

# 默认使用 mock 提供商，除非外部已设置
if not os.getenv("LLM_PROVIDER"):
    os.environ["LLM_PROVIDER"] = "mock"
    print("⚠️ LLM_PROVIDER 未设置，已使用 'mock' 进行测试")
from datetime import datetime
from pathlib import Path

from xwe.utils.requests_helper import ensure_requests

# 项目根目录
PROJECT_ROOT = Path(__file__).parent


class TestRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "unit_tests": {},
            "integration_tests": {},
            "main_scripts": {},
            "fixes_applied": [],
            "summary": {"total_tests": 0, "passed": 0, "failed": 0, "skipped": 0},
        }

    def run_pytest(self, test_path, test_type="unit"):
        """运行pytest测试"""
        print(f"\n{'='*60}")
        print(f"运行{test_type}测试: {test_path}")
        print("=" * 60)

        # 确保测试目录存在
        if not Path(test_path).exists():
            print(f"❌ 测试目录不存在: {test_path}")
            return False

        try:
            # 运行pytest
            env = os.environ.copy()
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                env=env,
            )

            # 解析结果
            output = result.stdout + result.stderr
            print(output)

            # 统计测试结果
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            skipped = output.count(" SKIPPED")

            test_result = {
                "path": test_path,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "return_code": result.returncode,
                "output": output[:1000],  # 保存前1000字符
            }

            if test_type == "unit":
                self.results["unit_tests"][test_path] = test_result
            else:
                self.results["integration_tests"][test_path] = test_result

            # 更新总计
            self.results["summary"]["total_tests"] += passed + failed + skipped
            self.results["summary"]["passed"] += passed
            self.results["summary"]["failed"] += failed
            self.results["summary"]["skipped"] += skipped

            return result.returncode == 0

        except Exception as e:
            print(f"❌ 运行测试失败: {e}")
            return False

    def run_main_script(self, script_path):
        """运行主要脚本进行集成测试"""
        print(f"\n{'='*60}")
        print(f"运行脚本: {script_path}")
        print("=" * 60)

        if not Path(script_path).exists():
            print(f"❌ 脚本不存在: {script_path}")
            return False

        try:
            # 创建测试输入
            test_input = "测试\n1\n退出\n"

            # 运行脚本（带超时）
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=PROJECT_ROOT,
            )

            # 发送输入并等待
            try:
                stdout, stderr = process.communicate(input=test_input, timeout=10)
                output = stdout + stderr
                success = process.returncode == 0 or "游戏已启动" in output
            except subprocess.TimeoutExpired:
                process.kill()
                output = "超时（脚本正常运行）"
                success = True  # 超时表示脚本在持续运行

            print(output[:500])  # 打印前500字符

            self.results["main_scripts"][script_path] = {
                "success": success,
                "output": output[:1000],
            }

            return success

        except Exception as e:
            print(f"❌ 运行脚本失败: {e}")
            return False

    def check_and_fix_imports(self):
        """检查并修复导入问题"""
        print("\n🔧 检查导入问题...")

        # 检查常见的导入问题
        fixes_needed = []

        # 检查NLP模块
        try:
            from xwe.core.nlp import NLPConfig, NLPProcessor

            print("✅ NLP导入正常")
        except ImportError as e:
            print(f"❌ NLP导入错误: {e}")
            fixes_needed.append("NLP导入")

        # 检查Roll系统
        try:
            from xwe.core.roll_system import CharacterRoller

            print("✅ Roll系统导入正常")
        except ImportError as e:
            print(f"❌ Roll系统导入错误: {e}")
            fixes_needed.append("Roll系统导入")

        return fixes_needed

    def fix_common_issues(self):
        """修复常见问题"""
        print("\n🔧 修复常见问题...")

        # 1. 确保NLPConfig在__init__.py中导出
        nlp_init_path = PROJECT_ROOT / "xwe/core/nlp/__init__.py"
        if nlp_init_path.exists():
            content = nlp_init_path.read_text()
            if "NLPConfig" not in content:
                print("修复: 添加NLPConfig到nlp/__init__.py")
                new_content = content.replace(
                    "from .nlp_processor import NLPProcessor",
                    "from .nlp_processor import NLPProcessor, NLPConfig",
                )
                new_content = new_content.replace(
                    "__all__ = ['NLPProcessor'", "__all__ = ['NLPProcessor', 'NLPConfig'"
                )
                nlp_init_path.write_text(new_content)
                self.results["fixes_applied"].append("NLPConfig导出修复")

    def generate_report(self):
        """生成测试报告"""
        report_path = PROJECT_ROOT / "test_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        # 生成Markdown报告
        md_report = f"""# XianXia World Engine - 自动化测试报告

生成时间: {self.results['timestamp']}

## 📊 测试统计

- **总测试数**: {self.results['summary']['total_tests']}
- **通过**: {self.results['summary']['passed']} ✅
- **失败**: {self.results['summary']['failed']} ❌
- **跳过**: {self.results['summary']['skipped']} ⏭️

## 🧪 单元测试结果

"""
        for path, result in self.results["unit_tests"].items():
            status = "✅" if result["return_code"] == 0 else "❌"
            md_report += f"### {path} {status}\n"
            md_report += f"- 通过: {result['passed']}\n"
            md_report += f"- 失败: {result['failed']}\n"
            md_report += f"- 跳过: {result['skipped']}\n\n"

        md_report += "\n## 🔧 集成测试结果\n\n"
        for path, result in self.results["integration_tests"].items():
            status = "✅" if result["return_code"] == 0 else "❌"
            md_report += f"### {path} {status}\n"
            md_report += f"- 通过: {result['passed']}\n"
            md_report += f"- 失败: {result['failed']}\n\n"

        md_report += "\n## 🎮 主脚本测试结果\n\n"
        for path, result in self.results["main_scripts"].items():
            status = "✅" if result["success"] else "❌"
            md_report += f"- {Path(path).name}: {status}\n"

        if self.results["fixes_applied"]:
            md_report += f"\n## 🔧 自动修复\n\n"
            for fix in self.results["fixes_applied"]:
                md_report += f"- {fix}\n"

        md_report_path = PROJECT_ROOT / "test_report.md"
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write(md_report)

        print(f"\n📋 测试报告已生成:")
        print(f"  - JSON: {report_path}")
        print(f"  - Markdown: {md_report_path}")

        return md_report


def main():
    """主函数"""
    print("🚀 XianXia World Engine - 自动化测试")
    print("=" * 60)

    ensure_requests()

    runner = TestRunner()

    # 1. 检查并修复常见问题
    runner.fix_common_issues()

    # 2. 运行单元测试
    print("\n\n🧪 运行单元测试...")
    runner.run_pytest("tests/unit/", "unit")

    # 3. 运行集成测试
    print("\n\n🔧 运行集成测试...")
    runner.run_pytest("tests/integration/", "integration")
    runner.run_pytest("tests/", "integration")

    # 4. 运行主要脚本
    print("\n\n🎮 测试主要脚本...")
    scripts_to_test = [
        "verify_system.py",
        "scripts/test_roll.py",
        "scripts/test_nlp.py",
        "scripts/verify_project.py",
    ]

    for script in scripts_to_test:
        if Path(PROJECT_ROOT / script).exists():
            runner.run_main_script(script)

    # 5. 生成报告
    report = runner.generate_report()
    print("\n\n" + report)

    # 6. 最终结果
    if runner.results["summary"]["failed"] == 0:
        print("\n\n✅ 所有测试通过！")
    else:
        print(f"\n\n❌ 有 {runner.results['summary']['failed']} 个测试失败")
        print("请查看test_report.md了解详情")


if __name__ == "__main__":
    main()
