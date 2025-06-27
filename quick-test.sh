#!/bin/bash
# 一键运行E2E测试脚本

echo "🎮 修仙世界引擎 - 一键E2E测试"
echo "============================="

# 1. 检查并设置E2E路由
if ! grep -q "register_e2e_routes" run.py 2>/dev/null; then
    echo "📝 正在设置E2E测试路由..."
    python3 scripts/setup_e2e.py || {
        echo "❌ 无法自动设置路由，请手动添加到run.py"
        exit 1
    }
fi

# 2. 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 安装npm依赖..."
    npm install || exit 1
fi

# 3. 确保Playwright浏览器已安装
if [ ! -d "$HOME/.cache/ms-playwright" ] && [ ! -d "$HOME/Library/Caches/ms-playwright" ]; then
    echo "🌐 安装Playwright浏览器..."
    npx playwright install || exit 1
fi

# 4. 运行测试
echo ""
echo "🚀 开始运行E2E测试..."
echo ""

# 设置环境变量
export ENABLE_E2E_API=true

# 运行增强版测试脚本
if [ -f "run-e2e-tests-enhanced.sh" ]; then
    chmod +x run-e2e-tests-enhanced.sh
    ./run-e2e-tests-enhanced.sh --chromium
else
    # 备用方案：直接运行playwright
    npx playwright test tests/e2e_full.spec.ts --headed --project=chromium
fi
