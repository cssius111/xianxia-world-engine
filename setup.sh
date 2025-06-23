#!/bin/bash
# 给所有脚本添加执行权限

chmod +x scripts/*.py
echo "✓ 已给所有Python脚本添加执行权限"

# 测试角色生成
echo -e "\n测试角色生成器..."
python scripts/gen_character.py

echo -e "\n完成! 现在可以运行:"
echo "python entrypoints/run_web_ui_optimized.py"
