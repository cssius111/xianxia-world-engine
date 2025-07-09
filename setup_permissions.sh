#!/bin/bash
# 为脚本添加执行权限

chmod +x run_tests.py
chmod +x verify_fixes.py
chmod +x test_fixes.sh

echo "脚本权限已设置"
echo ""
echo "现在可以运行以下命令来验证修复："
echo "  ./run_tests.py           # 运行所有测试组"
echo "  ./run_tests.py nlp       # 只运行 NLP 测试"
echo "  ./run_tests.py context   # 只运行上下文压缩测试"
echo "  ./verify_fixes.py        # 生成修复验证报告"
echo ""
echo "或者使用 Python 运行："
echo "  python run_tests.py"
echo "  python verify_fixes.py"
