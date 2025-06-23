#!/usr/bin/env python3
"""
综合测试运行器 - 运行所有测试并生成报告
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULT_DIR = PROJECT_ROOT / "tests" / "debug"
SCRIPT_DIR = RESULT_DIR / "debug_scripts"

print("=" * 70)
print("🚀 修仙世界引擎 - 综合测试运行器")
print("=" * 70)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"项目路径: {PROJECT_ROOT}")
print("=" * 70)

# 测试脚本列表
test_scripts = [
    {
        "name": "导入测试",
        "script": "imports_debug.py",
        "result_file": "import_test_results.json"
    },
    {
        "name": "文件系统测试",
        "script": "filesystem_debug.py",
        "result_file": "filesystem_test_results.json"
    },
    {
        "name": "Flask应用测试",
        "script": "flask_app_debug.py",
        "result_file": "flask_test_results.json"
    },
    {
        "name": "数据文件验证",
        "script": "data_files_debug.py",
        "result_file": "data_validation_results.json"
    }
]

# 运行结果汇总
overall_results = {
    "timestamp": datetime.now().isoformat(),
    "project_root": str(PROJECT_ROOT),
    "tests": {},
    "summary": {
        "total_tests": len(test_scripts),
        "passed": 0,
        "failed": 0,
        "errors": []
    }
}

# 运行每个测试
for test_info in test_scripts:
    print(f"\n📝 运行测试: {test_info['name']}")
    print("-" * 50)
    
    script_path = SCRIPT_DIR / test_info["script"]
    
    try:
        # 运行测试脚本
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        
        # 检查返回码
        if result.returncode == 0:
            print(f"✅ {test_info['name']} - 通过")
            overall_results["tests"][test_info["name"]] = {
                "status": "passed",
                "return_code": 0
            }
            overall_results["summary"]["passed"] += 1
        else:
            print(f"❌ {test_info['name']} - 失败 (返回码: {result.returncode})")
            overall_results["tests"][test_info["name"]] = {
                "status": "failed",
                "return_code": result.returncode,
                "error": result.stderr if result.stderr else "未知错误"
            }
            overall_results["summary"]["failed"] += 1
            overall_results["summary"]["errors"].append(
                f"{test_info['name']}: 返回码 {result.returncode}"
            )
        
        # 读取测试结果文件
        result_file = RESULT_DIR / test_info["result_file"]
        if result_file.exists():
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    test_result = json.load(f)
                overall_results["tests"][test_info["name"]]["details"] = test_result
            except Exception as e:
                print(f"  ⚠️  无法读取结果文件: {e}")
        
        # 显示测试输出的最后几行
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            print("  输出摘要:")
            for line in lines[-5:]:  # 最后5行
                print(f"    {line}")
                
    except Exception as e:
        print(f"❌ {test_info['name']} - 执行错误: {e}")
        overall_results["tests"][test_info["name"]] = {
            "status": "error",
            "error": str(e)
        }
        overall_results["summary"]["failed"] += 1
        overall_results["summary"]["errors"].append(
            f"{test_info['name']}: {str(e)}"
        )

# 生成综合报告
print("\n" + "=" * 70)
print("📊 测试总结")
print("=" * 70)

summary = overall_results["summary"]
print(f"总测试数: {summary['total_tests']}")
print(f"✅ 通过: {summary['passed']}")
print(f"❌ 失败: {summary['failed']}")

if summary["errors"]:
    print("\n主要问题:")
    for error in summary["errors"]:
        print(f"  - {error}")

# 分析具体问题
print("\n🔍 详细分析:")

# 1. 导入问题
if "导入测试" in overall_results["tests"]:
    import_test = overall_results["tests"]["导入测试"]
    if "details" in import_test:
        failed_imports = import_test["details"].get("failed", 0)
        if failed_imports > 0:
            print(f"\n❌ 有 {failed_imports} 个模块导入失败")
            print("  可能原因:")
            print("  - 缺少依赖包 (运行 pip install -r requirements.txt)")
            print("  - 模块路径错误")
            print("  - Python版本不兼容")

# 2. 文件系统问题
if "文件系统测试" in overall_results["tests"]:
    fs_test = overall_results["tests"]["文件系统测试"]
    if "details" in fs_test:
        missing_items = fs_test["details"].get("missing", [])
        if missing_items:
            print(f"\n❌ 有 {len(missing_items)} 个文件/目录缺失")
            print("  运行以下命令可以创建缺失的文件:")
            print(f"  python {RESULT_DIR}/fix_missing_files.py")

# 3. Flask应用问题
if "Flask应用测试" in overall_results["tests"]:
    flask_test = overall_results["tests"]["Flask应用测试"]
    if "details" in flask_test:
        if not flask_test["details"].get("flask_app", False):
            print("\n❌ Flask应用初始化失败")
            print("  可能原因:")
            print("  - 配置文件缺失")
            print("  - 环境变量未设置")
            print("  - 依赖模块导入失败")

# 4. 数据文件问题
if "数据文件验证" in overall_results["tests"]:
    data_test = overall_results["tests"]["数据文件验证"]
    if "details" in data_test:
        validation_errors = data_test["details"].get("validation_errors", {})
        total_data_errors = sum(len(errors) for errors in validation_errors.values())
        if total_data_errors > 0:
            print(f"\n❌ 数据文件有 {total_data_errors} 个验证错误")
            print("  查看修复建议:")
            print(f"  cat {RESULT_DIR}/data_fix_suggestions.txt")

# 保存综合报告
report_file = RESULT_DIR / "test_report.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(overall_results, f, indent=2, ensure_ascii=False)

# 生成HTML报告
html_report_file = RESULT_DIR / "test_report.html"
with open(html_report_file, 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>修仙世界引擎 - 测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        h2 { color: #666; margin-top: 30px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .summary-card { flex: 1; padding: 20px; border-radius: 8px; text-align: center; }
        .passed { background: #4CAF50; color: white; }
        .failed { background: #f44336; color: white; }
        .total { background: #2196F3; color: white; }
        .test-result { margin: 10px 0; padding: 15px; border-left: 4px solid; border-radius: 4px; }
        .test-passed { border-color: #4CAF50; background: #f1f8e9; }
        .test-failed { border-color: #f44336; background: #ffebee; }
        .error { color: #d32f2f; margin: 5px 0; }
        .timestamp { color: #999; font-size: 0.9em; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 修仙世界引擎 - 测试报告</h1>
        <p class="timestamp">生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        
        <div class="summary">
            <div class="summary-card total">
                <h3>总测试数</h3>
                <h2>""" + str(summary['total_tests']) + """</h2>
            </div>
            <div class="summary-card passed">
                <h3>通过</h3>
                <h2>""" + str(summary['passed']) + """</h2>
            </div>
            <div class="summary-card failed">
                <h3>失败</h3>
                <h2>""" + str(summary['failed']) + """</h2>
            </div>
        </div>
        
        <h2>测试详情</h2>
""")
    
    for test_name, test_result in overall_results["tests"].items():
        status = test_result.get("status", "unknown")
        css_class = "test-passed" if status == "passed" else "test-failed"
        f.write(f"""
        <div class="test-result {css_class}">
            <h3>{'✅' if status == 'passed' else '❌'} {test_name}</h3>
            <p>状态: {status}</p>
""")
        
        if "error" in test_result:
            f.write(f'<p class="error">错误: {test_result["error"]}</p>')
        
        if "details" in test_result and status == "failed":
            f.write("<details><summary>查看详情</summary><pre>")
            f.write(json.dumps(test_result["details"], indent=2, ensure_ascii=False))
            f.write("</pre></details>")
        
        f.write("</div>")
    
    f.write("""
        <h2>建议操作</h2>
        <ol>
            <li>如果有模块导入失败，运行: <code>pip install -r requirements.txt</code></li>
            <li>如果有文件缺失，运行: <code>python tests/debug/fix_missing_files.py</code></li>
            <li>检查 .env 文件是否配置正确</li>
            <li>查看详细日志文件获取更多信息</li>
        </ol>
    </div>
</body>
</html>
""")

print(f"\n📄 报告已生成:")
print(f"  - JSON报告: {report_file}")
print(f"  - HTML报告: {html_report_file}")
print("\n💡 提示: 在浏览器中打开 HTML 报告可以获得更好的阅读体验")

# 如果所有测试都通过
if summary["failed"] == 0:
    print("\n🎉 恭喜！所有测试都通过了！项目可以正常运行。")
    print("\n启动项目:")
    print(f"  cd {PROJECT_ROOT}")
    print("  python run_web_ui_v2.py")
else:
    print("\n⚠️  有测试失败，请根据上面的建议修复问题后再运行项目。")

print("\n" + "=" * 70)
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# 返回状态码
sys.exit(0 if summary["failed"] == 0 else 1)
