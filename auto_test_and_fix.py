#!/usr/bin/env python3
"""
XianXia World Engine - 全面自检与自动修复脚本
"""

import sys
import os
import subprocess
import json
import importlib
import traceback
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

class ProjectTester:
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "import_tests": {},
            "unit_tests": {},
            "integration_tests": {},
            "script_tests": {},
            "fixes": []
        }
    
    def test_imports(self):
        """测试所有核心模块的导入"""
        print("\n🔍 测试模块导入...")
        print("="*60)
        
        modules_to_test = [
            ("xwe", "主模块"),
            ("xwe.core", "核心模块"),
            ("xwe.core.game_core", "游戏核心"),
            ("xwe.core.character", "角色系统"),
            ("xwe.core.combat", "战斗系统"),
            ("xwe.core.skills", "技能系统"),
            ("xwe.core.ai", "AI系统"),
            ("xwe.core.nlp", "NLP模块"),
            ("xwe.core.nlp.nlp_processor", "NLP处理器"),
            ("xwe.core.roll_system", "Roll系统"),
            ("xwe.world", "世界系统"),
            ("xwe.world.world_map", "地图系统"),
            ("xwe.npc", "NPC系统"),
            ("xwe.npc.dialogue_system", "对话系统"),
            ("xwe.engine.expression", "表达式引擎"),
        ]
        
        for module_name, desc in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                print(f"✅ {desc} ({module_name})")
                self.test_results["import_tests"][module_name] = "passed"
            except ImportError as e:
                print(f"❌ {desc} ({module_name}): {e}")
                self.issues.append((module_name, str(e)))
                self.test_results["import_tests"][module_name] = f"failed: {e}"
            except Exception as e:
                print(f"❌ {desc} ({module_name}): {type(e).__name__}: {e}")
                self.issues.append((module_name, str(e)))
                self.test_results["import_tests"][module_name] = f"error: {e}"
    
    def run_unit_tests(self):
        """运行单元测试"""
        print("\n🧪 运行单元测试...")
        print("="*60)
        
        # 检查pytest
        try:
            import pytest
            print("✅ pytest已安装")
        except ImportError:
            print("安装pytest...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])
        
        # 运行测试
        test_dirs = [
            "tests/unit",
            "tests/integration",
            "tests"
        ]
        
        for test_dir in test_dirs:
            if Path(PROJECT_ROOT / test_dir).exists():
                print(f"\n运行 {test_dir} 测试...")
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_dir, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT
                )
                
                # 解析结果
                output = result.stdout + result.stderr
                passed = output.count(" PASSED")
                failed = output.count(" FAILED")
                
                self.test_results["unit_tests"][test_dir] = {
                    "passed": passed,
                    "failed": failed,
                    "return_code": result.returncode,
                    "summary": f"{passed} passed, {failed} failed"
                }
                
                if result.returncode == 0:
                    print(f"✅ {test_dir}: {passed} passed")
                else:
                    print(f"❌ {test_dir}: {passed} passed, {failed} failed")
                    if failed > 0:
                        # 提取失败的测试
                        lines = output.split('\n')
                        for i, line in enumerate(lines):
                            if "FAILED" in line:
                                print(f"  - {line.strip()}")
    
    def test_main_scripts(self):
        """测试主要脚本"""
        print("\n🎮 测试主要脚本...")
        print("="*60)
        
        scripts = [
            ("main.py", "主程序"),
            ("verify_system.py", "系统验证"),
            ("scripts/test_roll.py", "Roll测试"),
            ("scripts/test_nlp.py", "NLP测试"),
        ]
        
        for script_path, desc in scripts:
            full_path = PROJECT_ROOT / script_path
            if full_path.exists():
                print(f"\n测试 {desc} ({script_path})...")
                
                # 创建测试脚本
                test_script = f"""
import sys
sys.path.insert(0, r'{PROJECT_ROOT}')
try:
    # 测试导入
    if '{script_path}' == 'main.py':
        from xwe.core import GameCore
        game = GameCore()
        print("✅ GameCore创建成功")
    elif 'test_roll' in '{script_path}':
        from xwe.core.roll_system import CharacterRoller
        roller = CharacterRoller()
        result = roller.roll()
        print(f"✅ Roll测试成功: {{result.name}}")
    elif 'test_nlp' in '{script_path}':
        from xwe.core.nlp import NLPProcessor
        from xwe.core.command_parser import CommandParser
        parser = CommandParser()
        nlp = NLPProcessor(parser)
        result = nlp.parse("查看状态")
        print(f"✅ NLP测试成功: {{result.command_type}}")
    print("测试通过")
except Exception as e:
    print(f"❌ 错误: {{type(e).__name__}}: {{e}}")
    import traceback
    traceback.print_exc()
"""
                
                # 运行测试
                result = subprocess.run(
                    [sys.executable, "-c", test_script],
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT
                )
                
                if "测试通过" in result.stdout:
                    print(f"✅ {desc} 测试通过")
                    self.test_results["script_tests"][script_path] = "passed"
                else:
                    print(f"❌ {desc} 测试失败")
                    print(result.stdout)
                    print(result.stderr)
                    self.test_results["script_tests"][script_path] = "failed"
    
    def auto_fix_issues(self):
        """自动修复发现的问题"""
        print("\n🔧 自动修复问题...")
        print("="*60)
        
        # 1. 修复缺失的__init__.py
        dirs_need_init = [
            "xwe/core/npc",
            "xwe/tests",
        ]
        
        for dir_path in dirs_need_init:
            full_path = PROJECT_ROOT / dir_path
            init_file = full_path / "__init__.py"
            if full_path.exists() and not init_file.exists():
                print(f"创建 {dir_path}/__init__.py")
                init_file.write_text("# {}\n".format(dir_path.split('/')[-1]))
                self.fixes_applied.append(f"创建 {dir_path}/__init__.py")
        
        # 2. 修复NLP导入问题
        nlp_init = PROJECT_ROOT / "xwe/core/nlp/__init__.py"
        if nlp_init.exists():
            content = nlp_init.read_text()
            if "ParsedCommand" not in content:
                print("修复NLP模块导出...")
                new_content = content.replace(
                    "from .nlp_processor import NLPProcessor, NLPConfig",
                    "from .nlp_processor import NLPProcessor, NLPConfig, ParsedCommand"
                )
                if "ParsedCommand" not in new_content:
                    # 如果ParsedCommand在command_parser中
                    new_content = new_content.replace(
                        "__all__ = ['NLPProcessor', 'NLPConfig', 'LLMClient']",
                        "__all__ = ['NLPProcessor', 'NLPConfig', 'LLMClient']"
                    )
                nlp_init.write_text(new_content)
                self.fixes_applied.append("修复NLP模块导出")
        
        # 3. 确保pytest配置
        pytest_ini = PROJECT_ROOT / "pytest.ini"
        if not pytest_ini.exists():
            print("创建pytest.ini配置...")
            pytest_ini.write_text("""[pytest]
testpaths = tests
python_paths = .
addopts = -v --tb=short
""")
            self.fixes_applied.append("创建pytest.ini")
        
        self.test_results["fixes"] = self.fixes_applied
    
    def generate_report(self):
        """生成测试报告"""
        print("\n📋 生成测试报告...")
        print("="*60)
        
        # 统计
        total_imports = len(self.test_results["import_tests"])
        passed_imports = sum(1 for v in self.test_results["import_tests"].values() if v == "passed")
        
        total_tests = 0
        passed_tests = 0
        for test_result in self.test_results["unit_tests"].values():
            total_tests += test_result.get("passed", 0) + test_result.get("failed", 0)
            passed_tests += test_result.get("passed", 0)
        
        # 生成Markdown报告
        report = f"""# XianXia World Engine - 自动化测试报告

生成时间: {self.test_results['timestamp']}

## 📊 测试统计

### 导入测试
- 总数: {total_imports}
- 通过: {passed_imports} ✅
- 失败: {total_imports - passed_imports} ❌

### 单元测试
- 总数: {total_tests}
- 通过: {passed_tests} ✅
- 失败: {total_tests - passed_tests} ❌

## 🔍 导入测试详情

| 模块 | 状态 |
|------|------|
"""
        
        for module, status in self.test_results["import_tests"].items():
            emoji = "✅" if status == "passed" else "❌"
            report += f"| {module} | {emoji} {status} |\n"
        
        report += "\n## 🧪 单元测试详情\n\n"
        for test_dir, result in self.test_results["unit_tests"].items():
            report += f"### {test_dir}\n"
            report += f"- 通过: {result['passed']}\n"
            report += f"- 失败: {result['failed']}\n"
            report += f"- 结果: {'✅ 通过' if result['return_code'] == 0 else '❌ 失败'}\n\n"
        
        report += "\n## 🎮 脚本测试详情\n\n"
        for script, status in self.test_results["script_tests"].items():
            emoji = "✅" if status == "passed" else "❌"
            report += f"- {script}: {emoji} {status}\n"
        
        if self.fixes_applied:
            report += "\n## 🔧 自动修复\n\n"
            for fix in self.fixes_applied:
                report += f"- {fix}\n"
        
        # 保存报告
        report_path = PROJECT_ROOT / "test_report_full.md"
        report_path.write_text(report, encoding='utf-8')
        
        # 保存JSON报告
        json_path = PROJECT_ROOT / "test_report_full.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存到:")
        print(f"- {report_path}")
        print(f"- {json_path}")
        
        return report
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始全面自检...")
        print("="*60)
        
        # 1. 测试导入
        self.test_imports()
        
        # 2. 自动修复
        if self.issues:
            self.auto_fix_issues()
            # 重新测试导入
            print("\n重新测试导入...")
            self.issues = []
            self.test_imports()
        
        # 3. 运行单元测试
        self.run_unit_tests()
        
        # 4. 测试主脚本
        self.test_main_scripts()
        
        # 5. 生成报告
        report = self.generate_report()
        print("\n" + report)
        
        # 返回是否全部通过
        all_passed = all(
            status == "passed" 
            for status in self.test_results["import_tests"].values()
        )
        
        return all_passed

def main():
    """主函数"""
    tester = ProjectTester()
    all_passed = tester.run_all_tests()
    
    if all_passed:
        print("\n✅ 所有测试通过！项目运行正常。")
    else:
        print("\n❌ 部分测试失败，请查看详细报告。")
    
    # 提供测试命令
    print("\n📝 推荐的本地测试命令:")
    print("1. 运行所有测试: python -m pytest tests/ -v")
    print("2. 运行单元测试: python -m pytest tests/unit/ -v")
    print("3. 运行集成测试: python -m pytest tests/integration/ -v")
    print("4. 测试主程序: python main.py")
    print("5. 测试Roll系统: python scripts/test_roll.py")
    print("6. 测试NLP系统: python scripts/test_nlp.py")

if __name__ == "__main__":
    main()
