#!/bin/bash
# 修复 Flask 启动阻塞问题的脚本

echo "=== 修仙世界引擎启动修复 ==="
echo ""

# 设置环境变量以禁用可能阻塞的组件
export DISABLE_NLP=true
export USE_NLP=false
export FLASK_ENV=development
export FLASK_DEBUG=1

echo "已设置以下环境变量："
echo "- DISABLE_NLP=true"
echo "- USE_NLP=false"
echo "- FLASK_ENV=development"
echo "- FLASK_DEBUG=1"
echo ""

echo "正在启动服务器..."
echo "访问地址: http://127.0.0.1:5001"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 启动服务器
python "$SCRIPT_DIR/run.py" --debug --port 5001
