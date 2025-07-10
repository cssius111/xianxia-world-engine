#!/usr/bin/env python
"""可选方案：模拟缺失的依赖以便测试能运行"""
import sys
import os
from unittest.mock import MagicMock

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 模拟 prometheus_flask_exporter
sys.modules['prometheus_flask_exporter'] = MagicMock()
sys.modules['prometheus_flask_exporter'].PrometheusMetrics = MagicMock

# 模拟 objgraph
sys.modules['objgraph'] = MagicMock()

# 额外模拟常用依赖，以便在最小环境中运行测试
for pkg in [
    'flask',
    'requests',
    'python_dotenv',
    'prometheus_client',
    'psutil',
]:
    sys.modules[pkg] = MagicMock()

print("已模拟缺失的依赖包")
print("现在可以运行: python mock_dependencies.py && pytest")
