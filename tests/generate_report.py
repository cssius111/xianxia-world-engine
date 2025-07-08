"""
测试报告生成器
汇总所有测试结果并生成可视化报告
"""

import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Template


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self):
        self.test_results = {
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'duration': 0,
                'timestamp': datetime.now().isoformat()
            },
            'unit_tests': [],
            'integration_tests': [],
            'e2e_tests': [],
            'performance_tests': [],
            'stress_tests': [],
            'regression_tests': [],
            'coverage': {},
            'metrics': {}
        }
    
    def collect_test_results(self, test_dir: Path):
        """收集测试结果"""
        # 收集 pytest 结果
        pytest_results = test_dir / '.pytest_cache' / 'v' / 'cache' / 'lastfailed'
        if pytest_results.exists():
            with open(pytest_results, 'r') as f:
                failed_tests = json.load(f)
                self.test_results['summary']['failed'] += len(failed_tests)
        
        # 收集覆盖率数据
        coverage_file = test_dir / 'coverage.json'
        if coverage_file.exists():
            with open(coverage_file, 'r') as f:
                self.test_results['coverage'] = json.load(f)
        
        # 收集性能数据
        benchmark_dir = test_dir / '.benchmarks'
        if benchmark_dir.exists():
            for benchmark_file in benchmark_dir.glob('*.json'):
                with open(benchmark_file, 'r') as f:
                    benchmark_data = json.load(f)
                    self.test_results['performance_tests'].extend(
                        benchmark_data.get('benchmarks', [])
                    )
        
        # 收集各类测试结果
        self._collect_junit_results(test_dir)
        self._collect_custom_results(test_dir)
    
    def _collect_junit_results(self, test_dir: Path):
        """收集 JUnit 格式的测试结果"""
        import xml.etree.ElementTree as ET
        
        for junit_file in test_dir.glob('**/junit*.xml'):
            try:
                tree = ET.parse(junit_file)
                root = tree.getroot()
                
                for testsuite in root.findall('.//testsuite'):
                    suite_name = testsuite.get('name', 'unknown')
                    
                    for testcase in testsuite.findall('.//testcase'):
                        test_result = {
                            'name': testcase.get('name'),
                            'classname': testcase.get('classname'),
                            'time': float(testcase.get('time', 0)),
                            'status': 'passed'
                        }
                        
                        # 检查失败
                        if testcase.find('.//failure') is not None:
                            test_result['status'] = 'failed'
                            test_result['message'] = testcase.find('.//failure').get('message', '')
                        
                        # 检查跳过
                        elif testcase.find('.//skipped') is not None:
                            test_result['status'] = 'skipped'
                            test_result['message'] = testcase.find('.//skipped').get('message', '')
                        
                        # 分类存储
                        if 'unit' in suite_name.lower():
                            self.test_results['unit_tests'].append(test_result)
                        elif 'integration' in suite_name.lower():
                            self.test_results['integration_tests'].append(test_result)
                        elif 'e2e' in suite_name.lower():
                            self.test_results['e2e_tests'].append(test_result)
                        elif 'regression' in suite_name.lower():
                            self.test_results['regression_tests'].append(test_result)
                        
                        # 更新统计
                        self.test_results['summary']['total_tests'] += 1
                        if test_result['status'] == 'passed':
                            self.test_results['summary']['passed'] += 1
                        elif test_result['status'] == 'failed':
                            self.test_results['summary']['failed'] += 1
                        else:
                            self.test_results['summary']['skipped'] += 1
                        
                        self.test_results['summary']['duration'] += test_result['time']
            
            except Exception as e:
                print(f"解析 JUnit 文件失败 {junit_file}: {e}")
    
    def _collect_custom_results(self, test_dir: Path):
        """收集自定义格式的测试结果"""
        # 收集压力测试结果
        stress_results = test_dir / 'stress' / 'results.json'
        if stress_results.exists():
            with open(stress_results, 'r') as f:
                self.test_results['stress_tests'] = json.load(f)
        
        # 收集性能指标
        metrics_file = test_dir / 'metrics' / 'performance_metrics.json'
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                self.test_results['metrics'] = json.load(f)
    
    def generate_summary_charts(self, output_dir: Path):
        """生成摘要图表"""
        output_dir.mkdir(exist_ok=True)
        
        # 1. 测试结果饼图
        plt.figure(figsize=(8, 6))
        summary = self.test_results['summary']
        
        sizes = [summary['passed'], summary['failed'], summary['skipped']]
        labels = ['通过', '失败', '跳过']
        colors = ['#4CAF50', '#F44336', '#FFC107']
        
        # 过滤掉0值
        non_zero_indices = [i for i, size in enumerate(sizes) if size > 0]
        sizes = [sizes[i] for i in non_zero_indices]
        labels = [labels[i] for i in non_zero_indices]
        colors = [colors[i] for i in non_zero_indices]
        
        if sizes:  # 确保有数据
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('测试结果分布')
            plt.savefig(output_dir / 'test_results_pie.png')
            plt.close()
        
        # 2. 各类测试执行时间柱状图
        test_categories = ['unit', 'integration', 'e2e', 'performance', 'stress', 'regression']
        durations = []
        
        for category in test_categories:
            tests = self.test_results.get(f'{category}_tests', [])
            total_duration = sum(t.get('time', 0) for t in tests if isinstance(t, dict))
            durations.append(total_duration)
        
        plt.figure(figsize=(10, 6))
        plt.bar(test_categories, durations, color='skyblue')
        plt.xlabel('测试类别')
        plt.ylabel('总执行时间 (秒)')
        plt.title('各类测试执行时间')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / 'test_duration_bar.png')
        plt.close()
        
        # 3. 覆盖率图表
        if self.test_results.get('coverage'):
            coverage_data = self.test_results['coverage']
            
            if 'totals' in coverage_data:
                plt.figure(figsize=(8, 6))
                
                metrics = ['statements', 'missing', 'excluded', 'branches']
                values = [
                    coverage_data['totals'].get('num_statements', 0),
                    coverage_data['totals'].get('missing_lines', 0),
                    coverage_data['totals'].get('excluded_lines', 0),
                    coverage_data['totals'].get('num_branches', 0)
                ]
                
                plt.bar(metrics, values, color=['green', 'red', 'yellow', 'blue'])
                plt.xlabel('指标')
                plt.ylabel('数量')
                plt.title('代码覆盖率统计')
                plt.tight_layout()
                plt.savefig(output_dir / 'coverage_stats.png')
                plt.close()
    
    def generate_html_report(self, output_path: Path):
        """生成 HTML 报告"""
        template_str = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XianXia World Engine - NLP 模块测试报告</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #333;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }
        .summary-card .value {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .passed { color: #4CAF50; }
        .failed { color: #F44336; }
        .skipped { color: #FFC107; }
        .chart-container {
            margin: 30px 0;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .status-passed {
            color: #4CAF50;
            font-weight: bold;
        }
        .status-failed {
            color: #F44336;
            font-weight: bold;
        }
        .status-skipped {
            color: #FFC107;
            font-weight: bold;
        }
        .section {
            margin: 40px 0;
        }
        .timestamp {
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>XianXia World Engine - NLP 模块测试报告</h1>
        <p class="timestamp">生成时间: {{ summary.timestamp }}</p>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="value">{{ summary.total_tests }}</div>
            </div>
            <div class="summary-card">
                <h3>通过</h3>
                <div class="value passed">{{ summary.passed }}</div>
            </div>
            <div class="summary-card">
                <h3>失败</h3>
                <div class="value failed">{{ summary.failed }}</div>
            </div>
            <div class="summary-card">
                <h3>跳过</h3>
                <div class="value skipped">{{ summary.skipped }}</div>
            </div>
            <div class="summary-card">
                <h3>通过率</h3>
                <div class="value">{{ "%.1f"|format(pass_rate) }}%</div>
            </div>
            <div class="summary-card">
                <h3>总耗时</h3>
                <div class="value">{{ "%.2f"|format(summary.duration) }}s</div>
            </div>
        </div>
        
        <div class="section">
            <h2>测试结果分布</h2>
            <div class="chart-container">
                <img src="test_results_pie.png" alt="测试结果饼图">
            </div>
        </div>
        
        <div class="section">
            <h2>各类测试执行时间</h2>
            <div class="chart-container">
                <img src="test_duration_bar.png" alt="执行时间柱状图">
            </div>
        </div>
        
        {% if coverage %}
        <div class="section">
            <h2>代码覆盖率</h2>
            <div class="summary">
                <div class="summary-card">
                    <h3>行覆盖率</h3>
                    <div class="value">{{ "%.1f"|format(coverage.percent_covered) }}%</div>
                </div>
                <div class="summary-card">
                    <h3>总行数</h3>
                    <div class="value">{{ coverage.num_statements }}</div>
                </div>
                <div class="summary-card">
                    <h3>已覆盖</h3>
                    <div class="value passed">{{ coverage.num_statements - coverage.missing_lines }}</div>
                </div>
                <div class="summary-card">
                    <h3>未覆盖</h3>
                    <div class="value failed">{{ coverage.missing_lines }}</div>
                </div>
            </div>
        </div>
        {% endif %}
        
        {% for test_type, tests in test_details.items() %}
        {% if tests %}
        <div class="section">
            <h2>{{ test_type }} 详情</h2>
            <table>
                <thead>
                    <tr>
                        <th>测试名称</th>
                        <th>状态</th>
                        <th>耗时</th>
                        <th>备注</th>
                    </tr>
                </thead>
                <tbody>
                    {% for test in tests[:20] %}
                    <tr>
                        <td>{{ test.name }}</td>
                        <td class="status-{{ test.status }}">{{ test.status.upper() }}</td>
                        <td>{{ "%.3f"|format(test.time) }}s</td>
                        <td>{{ test.message|default('', true) }}</td>
                    </tr>
                    {% endfor %}
                    {% if tests|length > 20 %}
                    <tr>
                        <td colspan="4" style="text-align: center; color: #666;">
                            ... 还有 {{ tests|length - 20 }} 个测试结果未显示 ...
                        </td>
                    </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
        {% endif %}
        {% endfor %}
        
        {% if performance_tests %}
        <div class="section">
            <h2>性能测试结果</h2>
            <table>
                <thead>
                    <tr>
                        <th>测试名称</th>
                        <th>平均时间</th>
                        <th>最小时间</th>
                        <th>最大时间</th>
                        <th>标准差</th>
                    </tr>
                </thead>
                <tbody>
                    {% for test in performance_tests[:10] %}
                    <tr>
                        <td>{{ test.name }}</td>
                        <td>{{ "%.3f"|format(test.stats.mean * 1000) }}ms</td>
                        <td>{{ "%.3f"|format(test.stats.min * 1000) }}ms</td>
                        <td>{{ "%.3f"|format(test.stats.max * 1000) }}ms</td>
                        <td>{{ "%.3f"|format(test.stats.stddev * 1000) }}ms</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>建议和改进点</h2>
            <ul>
                {% for recommendation in recommendations %}
                <li>{{ recommendation }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
</body>
</html>
        """
        
        # 计算通过率
        pass_rate = 0
        if self.test_results['summary']['total_tests'] > 0:
            pass_rate = (self.test_results['summary']['passed'] / 
                        self.test_results['summary']['total_tests'] * 100)
        
        # 准备模板数据
        template_data = {
            'summary': self.test_results['summary'],
            'pass_rate': pass_rate,
            'coverage': self.test_results.get('coverage', {}).get('totals', {}),
            'test_details': {
                '单元测试': self.test_results['unit_tests'],
                '集成测试': self.test_results['integration_tests'],
                'E2E测试': self.test_results['e2e_tests'],
                '回归测试': self.test_results['regression_tests']
            },
            'performance_tests': self.test_results['performance_tests'],
            'recommendations': self._generate_recommendations()
        }
        
        # 渲染模板
        template = Template(template_str)
        html_content = template.render(**template_data)
        
        # 保存报告
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        summary = self.test_results['summary']
        
        # 基于测试结果的建议
        if summary['failed'] > 0:
            recommendations.append(f"⚠️ 有 {summary['failed']} 个测试失败，请优先修复这些问题")
        
        if summary['total_tests'] > 0:
            pass_rate = summary['passed'] / summary['total_tests'] * 100
            if pass_rate < 80:
                recommendations.append(f"⚠️ 测试通过率仅为 {pass_rate:.1f}%，建议提高到 80% 以上")
        
        # 基于覆盖率的建议
        coverage = self.test_results.get('coverage', {}).get('totals', {})
        if coverage:
            coverage_percent = coverage.get('percent_covered', 0)
            if coverage_percent < 80:
                recommendations.append(f"📊 代码覆盖率为 {coverage_percent:.1f}%，建议提高到 80% 以上")
        
        # 基于性能的建议
        if self.test_results['performance_tests']:
            slow_tests = [t for t in self.test_results['performance_tests'] 
                         if isinstance(t, dict) and t.get('stats', {}).get('mean', 0) > 1.0]
            if slow_tests:
                recommendations.append(f"🐌 有 {len(slow_tests)} 个性能测试超过 1 秒，考虑优化")
        
        # 通用建议
        if not recommendations:
            recommendations.append("✅ 测试结果良好，继续保持！")
        
        recommendations.extend([
            "💡 定期运行回归测试，确保修复的问题不会重现",
            "💡 考虑添加更多边界情况的测试用例",
            "💡 监控生产环境的性能指标，与测试基准对比"
        ])
        
        return recommendations
    
    def generate_json_report(self, output_path: Path):
        """生成 JSON 格式的报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
    
    def generate_markdown_report(self, output_path: Path):
        """生成 Markdown 格式的报告"""
        summary = self.test_results['summary']
        
        md_content = f"""# XianXia World Engine - NLP 模块测试报告

生成时间: {summary['timestamp']}

## 📊 测试摘要

| 指标 | 数值 |
|------|------|
| 总测试数 | {summary['total_tests']} |
| ✅ 通过 | {summary['passed']} |
| ❌ 失败 | {summary['failed']} |
| ⏭️ 跳过 | {summary['skipped']} |
| 通过率 | {summary['passed'] / summary['total_tests'] * 100:.1f}% |
| 总耗时 | {summary['duration']:.2f}秒 |

## 📈 各类测试结果

"""
        
        # 添加各类测试的统计
        for test_type in ['unit', 'integration', 'e2e', 'performance', 'stress', 'regression']:
            tests = self.test_results.get(f'{test_type}_tests', [])
            if tests:
                passed = sum(1 for t in tests if t.get('status') == 'passed')
                failed = sum(1 for t in tests if t.get('status') == 'failed')
                
                md_content += f"""### {test_type.title()} Tests
- 总数: {len(tests)}
- 通过: {passed}
- 失败: {failed}

"""
        
        # 添加改进建议
        md_content += "## 💡 改进建议\n\n"
        for rec in self._generate_recommendations():
            md_content += f"- {rec}\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生成测试报告')
    parser.add_argument('--test-dir', type=str, default='tests', help='测试目录')
    parser.add_argument('--output', type=str, default='test-report.html', help='输出文件')
    parser.add_argument('--format', choices=['html', 'json', 'markdown'], default='html', help='报告格式')
    
    args = parser.parse_args()
    
    # 创建报告生成器
    generator = TestReportGenerator()
    
    # 收集测试结果
    test_dir = Path(args.test_dir)
    if test_dir.exists():
        generator.collect_test_results(test_dir)
    
    # 生成图表
    output_dir = Path(args.output).parent
    generator.generate_summary_charts(output_dir)
    
    # 生成报告
    output_path = Path(args.output)
    
    if args.format == 'html':
        generator.generate_html_report(output_path)
    elif args.format == 'json':
        generator.generate_json_report(output_path)
    elif args.format == 'markdown':
        generator.generate_markdown_report(output_path)
    
    print(f"测试报告已生成: {output_path}")


if __name__ == "__main__":
    main()
