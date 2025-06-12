#!/usr/bin/env python3
"""
第4阶段功能验证脚本
验证所有新增功能是否正常工作
"""

import sys
import importlib
import requests
import json
from pathlib import Path

def check_import(module_name, feature_name):
    """检查模块是否可以导入"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {feature_name}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {feature_name}: {module_name} - {e}")
        return False

def check_file_exists(file_path, feature_name):
    """检查文件是否存在"""
    if Path(file_path).exists():
        print(f"✅ {feature_name}: {file_path}")
        return True
    else:
        print(f"❌ {feature_name}: {file_path} - 文件不存在")
        return False

def check_api_endpoint(url, feature_name):
    """检查API端点是否可访问"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code < 500:
            print(f"✅ {feature_name}: {url} (状态码: {response.status_code})")
            return True
        else:
            print(f"❌ {feature_name}: {url} - 服务器错误 {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  {feature_name}: {url} - 无法连接（服务可能未启动）")
        return None

def main():
    print("=" * 60)
    print("修仙世界引擎 - 第4阶段功能验证")
    print("=" * 60)
    
    results = []
    
    # 1. 检查Python模块
    print("\n1. 检查Python模块导入:")
    results.append(check_import("xwe.services.log_service", "结构化日志"))
    results.append(check_import("xwe.metrics.prometheus", "Prometheus指标"))
    results.append(check_import("api.v1.dev", "开发调试API"))
    results.append(check_import("api.specs.openapi_generator", "OpenAPI生成器"))
    
    # 2. 检查文件存在
    print("\n2. 检查配置文件:")
    results.append(check_file_exists("Dockerfile", "Docker镜像定义"))
    results.append(check_file_exists("docker-compose.yml", "Docker编排"))
    results.append(check_file_exists(".dockerignore", "Docker忽略文件"))
    results.append(check_file_exists("prometheus.yml", "Prometheus配置"))
    results.append(check_file_exists("docs/metrics_guide.md", "监控指南文档"))
    results.append(check_file_exists("tests/test_prometheus.py", "Prometheus测试"))
    
    # 3. 检查功能实现
    print("\n3. 检查功能实现:")
    try:
        from xwe.services.log_service import StructuredLogger
        logger = StructuredLogger()
        logger.info("Test message")
        print("✅ StructuredLogger: 可以创建并使用")
        results.append(True)
    except Exception as e:
        print(f"❌ StructuredLogger: {e}")
        results.append(False)
    
    try:
        from xwe.metrics import PrometheusMetrics
        metrics = PrometheusMetrics()
        metrics.register_counter("test_counter", "Test counter")
        metrics.inc_counter("test_counter", 1)
        export = metrics.export_metrics()
        if "test_counter 1" in export:
            print("✅ PrometheusMetrics: 指标导出正常")
            results.append(True)
        else:
            print("❌ PrometheusMetrics: 指标导出异常")
            results.append(False)
    except Exception as e:
        print(f"❌ PrometheusMetrics: {e}")
        results.append(False)
    
    # 4. 检查API端点（如果服务运行中）
    print("\n4. 检查API端点 (需要服务运行在 localhost:5001):")
    base_url = "http://localhost:5001"
    
    api_results = []
    api_results.append(check_api_endpoint(f"{base_url}/api/v1/system/metrics", "Prometheus指标端点"))
    api_results.append(check_api_endpoint(f"{base_url}/api/docs", "Swagger UI文档"))
    api_results.append(check_api_endpoint(f"{base_url}/api/openapi.json", "OpenAPI规范"))
    api_results.append(check_api_endpoint(f"{base_url}/api/v1/dev/debug", "调试信息端点"))
    
    # 5. 总结
    print("\n" + "=" * 60)
    print("验证结果总结:")
    print("=" * 60)
    
    # 统计结果
    success_count = sum(1 for r in results if r is True)
    fail_count = sum(1 for r in results if r is False)
    
    print(f"\n文件和模块检查: {success_count} 成功, {fail_count} 失败")
    
    # API检查结果
    api_success = sum(1 for r in api_results if r is True)
    api_fail = sum(1 for r in api_results if r is False)
    api_skip = sum(1 for r in api_results if r is None)
    
    if api_skip == len(api_results):
        print("API端点检查: 跳过（服务未运行）")
        print("\n提示: 运行以下命令启动服务后再次验证:")
        print("  python run_web_ui_optimized.py")
        print("  或")
        print("  docker-compose up")
    else:
        print(f"API端点检查: {api_success} 成功, {api_fail} 失败")
    
    # 整体结果
    if fail_count == 0:
        print("\n✅ 所有核心功能验证通过！")
        print("\n下一步:")
        print("1. 运行 'python phase4_integration_example.py' 查看集成示例")
        print("2. 运行 'docker-compose up' 启动完整环境")
        print("3. 访问 http://localhost:5001/api/docs 查看API文档")
        return 0
    else:
        print(f"\n❌ 有 {fail_count} 项验证失败，请检查实现")
        return 1

if __name__ == "__main__":
    sys.exit(main())
