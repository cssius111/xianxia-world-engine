#!/bin/bash

# 🧪 仙侠世界优化验证一键测试脚本

echo "🎮 仙侠世界游戏优化验证测试"
echo "=========================================="

# 检查Python版本
echo "🐍 检查Python环境..."
python3 --version

# 检查是否在正确目录
if [ ! -d "xwe" ]; then
    echo "❌ 错误: 请在项目根目录下运行此脚本"
    echo "当前目录: $(pwd)"
    echo "应该在: xianxia_world_engine目录下"
    exit 1
fi

echo "✅ 项目目录检查通过"

# 设置环境变量避免API调用
export LLM_PROVIDER="mock"
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "🧪 开始运行优化验证测试..."
echo ""

# 运行Python测试脚本
python3 optimization_test_script.py

# 检查测试结果
test_result=$?

echo ""
echo "=========================================="

if [ $test_result -eq 0 ]; then
    echo "🎉 所有测试通过！优化工具效果显著！"
    echo ""
    echo "🚀 建议下一步操作："
    echo "1. 运行游戏进行实际测试: python3 -m xwe.core.game_core"
    echo "2. 查看重构计划: cat refactor_plan_*.md"
    echo "3. 开始实施重构优化代码质量"
else
    echo "⚠️ 部分测试失败，请检查输出信息"
    echo ""
    echo "🔧 故障排除："
    echo "1. 检查Python版本（需要3.8+）"
    echo "2. 确保所有依赖包已安装"
    echo "3. 查看详细错误信息并修复"
fi

echo "=========================================="
