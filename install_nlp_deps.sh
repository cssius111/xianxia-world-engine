#!/bin/bash
# 快速安装 NLP 依赖

echo "🔧 安装修仙世界引擎 NLP 依赖..."
echo "================================"

# 安装 backoff（可选，用于重试机制）
echo "📦 安装 backoff..."
pip install backoff

# 检查是否需要安装其他依赖
echo ""
echo "✅ 依赖安装完成！"
echo ""
echo "注意："
echo "1. backoff 是可选依赖，系统在没有它的情况下也能运行"
echo "2. DeepSeek SDK 需要单独安装（如果需要）："
echo "   pip install deepseek"
echo ""
echo "如果您有 DeepSeek API 密钥，请在 .env 文件中设置："
echo "DEEPSEEK_API_KEY=your_api_key_here"
echo ""
echo "现在可以运行: python start_web.py"
