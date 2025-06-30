#!/bin/bash
# 快速修复导入错误并运行测试

echo "🔧 修仙世界引擎 - 快速修复"
echo "=========================="

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 1. 运行修复脚本
echo -e "\n1️⃣ 运行导入修复..."
python fix_imports.py

# 2. 运行测试
echo -e "\n2️⃣ 运行测试套件..."
pytest tests/ -v --tb=short

# 3. 显示结果
if [ $? -eq 0 ]; then
    echo -e "\n✅ 所有测试通过！"
    echo -e "\n现在可以运行游戏："
    echo "   python run.py"
else
    echo -e "\n❌ 仍有测试失败"
    echo -e "\n建议："
    echo "1. 查看上面的错误信息"
    echo "2. 手动修复剩余的问题"
    echo "3. 或者尝试运行游戏看是否能正常启动"
fi
