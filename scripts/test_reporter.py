import contextlib
import io
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import psutil
import pytest


class ResultCollector:
    """Pytest plugin to collect test results."""

    def __init__(self) -> None:
        self.results: List[Dict[str, Any]] = []

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:  # type: ignore[override]
        if report.when == "call":
            self.results.append(
                {
                    "name": report.nodeid,
                    "outcome": report.outcome,
                    "duration": getattr(report, "duration", 0.0),
                }
            )


REPORT_DIR = Path(__file__).resolve().parents[1] / "tests" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_pytests() -> Dict[str, Any]:
    collector = ResultCollector()
    stdout = io.StringIO()

    process = psutil.Process()
    start_mem = process.memory_info().rss
    start_cpu = process.cpu_times()
    start_time = time.time()

    # Run pytest with output captured so we can parse stress metrics
    with contextlib.redirect_stdout(stdout):
        ret = pytest.main(
            [
                "tests",
                "-s",
                "-vv",
            ],
            plugins=[collector],
        )

    duration = time.time() - start_time
    end_cpu = process.cpu_times()
    end_mem = process.memory_info().rss

    stats = {
        "exit_code": ret,
        "duration": duration,
        "cpu_user_time": end_cpu.user - start_cpu.user,
        "cpu_system_time": end_cpu.system - start_cpu.system,
        "memory_change_mb": (end_mem - start_mem) / 1024 / 1024,
    }

    return {
        "results": collector.results,
        "stats": stats,
        "output": stdout.getvalue(),
    }


def summarize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for r in results if r["outcome"] == "passed")
    failed = sum(1 for r in results if r["outcome"] == "failed")
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total if total else 0,
    }


def load_benchmark_report() -> Dict[str, Any]:
    path = REPORT_DIR / "performance_report.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def parse_stress_metrics(output: str) -> Dict[str, Dict[str, Any]]:
    metrics: Dict[str, Dict[str, Any]] = {}
    pattern = re.compile(r"^(\S+测试完成:)\s*$")
    lines = output.splitlines()
    for i, line in enumerate(lines):
        if pattern.search(line):
            name = pattern.search(line).group(1).replace("测试完成:", "")
            data: Dict[str, Any] = {}
            for j in range(i + 1, len(lines)):
                m = re.match(r"^\s*(\S+):\s*([\d.]+)", lines[j])
                if m:
                    key = m.group(1)
                    val = float(m.group(2)) if "." in m.group(2) else int(m.group(2))
                    data[key] = val
                else:
                    break
            metrics[name] = data
    return metrics


def generate_markdown(
    summary: Dict[str, Any], bench: Dict[str, Any], stress: Dict[str, Dict[str, Any]]
) -> str:
    lines = ["# 测试报告", ""]
    lines.append("## 总览")
    lines.append(f"- 总测试数: {summary['total']}")
    lines.append(f"- 通过: {summary['passed']}")
    lines.append(f"- 失败: {summary['failed']}")
    lines.append(f"- 通过率: {summary['pass_rate']:.1%}")
    lines.append(f"- 运行时长: {summary['stats']['duration']:.2f}s")
    lines.append(
        f"- CPU时间: {summary['stats']['cpu_user_time'] + summary['stats']['cpu_system_time']:.2f}s"
    )
    lines.append(f"- 内存变化: {summary['stats']['memory_change_mb']:.2f}MB")
    lines.append("")

    if bench:
        lines.append("## 基准测试")
        lines.append(f"测试时间: {bench.get('test_date')}")
        resource = bench.get("test_results", {}).get("resource_usage", {})
        if resource:
            lines.append(f"- 峰值CPU: {resource.get('max_cpu_percent')}%")
            lines.append(f"- 峰值内存: {resource.get('max_memory_mb')}MB")
        lines.append("")

    if stress:
        lines.append("## 压力测试")
        for name, data in stress.items():
            lines.append(f"### {name}")
            for k, v in data.items():
                lines.append(f"- {k}: {v}")
            lines.append("")

    return "\n".join(lines)


def main() -> int:
    run_data = run_pytests()
    summary = summarize_results(run_data["results"])
    summary["stats"] = run_data["stats"]
    bench = load_benchmark_report()
    stress = parse_stress_metrics(run_data["output"])

    md = generate_markdown(summary, bench, stress)
    report_path = REPORT_DIR / "test_summary.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"报告已生成: {report_path}")
    return run_data["stats"]["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
