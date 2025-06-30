#!/bin/bash
# 项目清理脚本

echo "🧹 修仙世界引擎 - 项目清理"
echo "=========================="

# 切换到脚本所在目录的上级目录（项目根目录）
cd "$(dirname "$0")/.."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    exit 1
fi

# 运行清理脚本
if [ "$1" = "--execute" ]; then
    echo "⚠️  警告：将实际删除文件！"
    echo ""
    python3 scripts/cleanup_project.py --execute
else
    echo "📋 演示模式（不会删除文件）"
    echo ""
    python3 scripts/cleanup_project.py
    echo ""
    echo "💡 提示：使用 './scripts/cleanup_project.sh --execute' 来实际执行清理"
fi
