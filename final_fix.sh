#!/bin/bash
# 清理旧脚本并运行最终修复

echo "🧹 清理旧的修复脚本..."
rm -f scripts/complete_fix_and_cleanup.py

echo ""
echo "🚀 运行最终修复..."
python scripts/final_complete_fix.py

echo ""
echo "✅ 修复完成！"
echo ""
echo "📋 现在可以运行项目了："
echo "python entrypoints/run_web_ui_optimized.py"
