#!/bin/bash

# 修仙世界引擎启动脚本

echo "=========================================="
echo "🎮 修仙世界引擎 (Xianxia World Engine)"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    echo "请先安装 Python 3.7 或更高版本"
    exit 1
fi

# 显示Python版本
echo "✅ Python 版本："
python3 --version
echo ""

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 检查是否存在 run.py
if [ ! -f "$SCRIPT_DIR/run.py" ]; then
    echo "❌ 错误：未找到 run.py 文件"
    exit 1
fi

# 检查并创建必要的目录
echo "📁 检查目录结构..."
for dir in saves logs static/audio static/images; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "   创建目录: $dir"
    fi
done
echo ""


# 设置环境变量
export FLASK_ENV=development
export DEBUG=true

# 启动服务器
echo "🚀 启动游戏服务器..."
echo "=========================================="
echo "访问地址: http://localhost:5001"
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

# 启动Python服务器
python3 "$SCRIPT_DIR/run.py"
