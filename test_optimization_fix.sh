#!/bin/bash
# 快速测试优化模块修复

echo "🧪 测试优化模块修复..."
echo "========================"

# 只运行失败的测试
echo -e "\n运行失败的测试..."
pytest tests/test_optimizations.py::test_expression_jit_compile tests/test_optimizations.py::test_smart_cache_basic -v

# 如果成功，运行所有优化测试
if [ $? -eq 0 ]; then
    echo -e "\n✅ 修复成功！运行所有优化测试..."
    pytest tests/test_optimizations.py -v
    
    if [ $? -eq 0 ]; then
        echo -e "\n🎉 所有优化测试通过！"
        echo -e "\n现在运行完整测试套件："
        echo "   pytest tests/"
    fi
else
    echo -e "\n❌ 仍有问题需要修复"
fi
