#!/bin/bash
# 快速运行清理脚本

echo "🚀 启动项目清理工具..."
echo ""

# 确保脚本有执行权限
chmod +x cleanup_all.py
chmod +x cleanup_duplicates.py
chmod +x restructure_project.py

# 运行综合清理脚本
python3 cleanup_all.py
