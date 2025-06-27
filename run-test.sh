#!/bin/bash

# 遇到错误立即退出
set -e

# 修仙游戏测试启动脚本

echo "🎮 修仙游戏 Playwright 测试启动脚本"
echo "=================================="

# 检查是否安装了 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 请先安装 Node.js"
    exit 1
fi

# 检查是否安装了 Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ 错误: 请先安装 Python"
    exit 1
fi

# 安装 npm 依赖
echo "📦 安装 npm 依赖..."
npm install

# 安装 Python 依赖
echo "🐍 安装 Python 依赖..."
pip3 install -r requirements.txt

# 安装 Playwright 浏览器及依赖
echo "🌐 安装 Playwright 浏览器..."
if ! npx playwright install --with-deps; then
    echo "⚠️ 系统依赖安装失败，尝试仅安装浏览器..."
    npx playwright install
fi

# 启动游戏服务器（后台运行）
echo "🚀 启动游戏服务器..."
# 根据你的项目结构，可能需要调整启动命令
if [ -f "app.py" ]; then
    python3 app.py &
elif [ -f "main.py" ]; then
    python3 main.py &
elif [ -f "server.py" ]; then
    python3 server.py &
elif [ -f "run.py" ]; then
    python3 run.py &
elif [ -f "start_web.py" ]; then
    python3 start_web.py &
else
    # 使用简单的 HTTP 服务器作为回退
    python3 -m http.server 5001 &
fi

SERVER_PID=$!
echo "📝 服务器进程 ID: $SERVER_PID"

# 确保脚本退出时清理服务器进程
cleanup() {
    echo "🧹 清理资源..."
    kill $SERVER_PID 2>/dev/null || true
}
trap cleanup EXIT

# 等待服务器启动
echo "⏳ 等待服务器启动..."
sleep 5

# 检查服务器是否启动成功
if curl -s http://localhost:5001 > /dev/null; then
    echo "✅ 服务器启动成功!"
    
    # 运行 Playwright 测试
    echo "🎭 开始运行 Playwright 测试..."
    if [ "${HEADLESS:-1}" = "0" ]; then
        npx playwright test --headed --project=chromium xiuxian-game.spec.js
    else
        npx playwright test --project=chromium xiuxian-game.spec.js
    fi
    
    # 显示测试报告
    echo "📊 显示测试报告..."
    npx playwright show-report
else
    echo "❌ 服务器启动失败，请检查配置"
fi

echo "✨ 测试完成!"
