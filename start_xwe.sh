#!/bin/bash
# XWE 启动脚本 - 确保正确的 Python 路径

export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/src"
export ENABLE_PROMETHEUS=true

echo "🚀 启动 XianXia World Engine..."
echo "📊 Prometheus 监控已启用"
echo "📍 访问 http://localhost:5000/metrics 查看指标"

python app.py
