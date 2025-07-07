#!/bin/bash
# 使启动脚本可执行
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$SCRIPT_DIR/start_fixed.sh"
echo "start_fixed.sh 现在可以执行了"
echo "运行: $SCRIPT_DIR/start_fixed.sh"
