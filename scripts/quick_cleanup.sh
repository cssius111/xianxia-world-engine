#!/bin/bash
# 快速清理和重构项目

echo "🛠️  仙侠世界引擎 - 快速清理工具"
echo "=================================="
echo ""
echo "本脚本将执行以下操作："
echo "1. 运行项目重构脚本"
echo "2. 清理重复的模块"
echo "3. 删除终端相关代码"
echo "4. 统一使用xwe作为核心"
echo ""
echo "⚠️  警告：此操作将修改项目结构！"
echo "建议先备份项目或确保Git状态干净"
echo ""

read -p "是否继续？(y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "开始清理项目..."
    python3 scripts/cleanup_and_refactor.py
else
    echo "操作已取消"
fi
