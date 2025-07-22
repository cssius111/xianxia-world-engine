#!/bin/bash
# 快速测试命令集合

echo "修仙世界引擎 - 测试工具"
echo "========================"
echo ""
echo "可用命令:"
echo "  1) 应用最终修复"
echo "  2) 运行所有测试"
echo "  3) 运行快速测试 (跳过慢速和不稳定)"
echo "  4) 运行特定测试组"
echo "  5) 生成测试报告"
echo "  6) 查看测试覆盖率"
echo "  0) 退出"
echo ""

read -p "请选择 (0-6): " choice

case $choice in
    1)
        echo "应用最终修复..."
        python final_fixes.py
        ;;
    2)
        echo "运行所有测试..."
        pytest -v
        ;;
    3)
        echo "运行快速测试..."
        pytest -v -m "not slow and not flaky"
        ;;
    4)
        echo "选择测试组:"
        echo "  a) NLP 测试"
        echo "  b) Context 测试"
        echo "  c) Async 测试"
        echo "  d) API 测试"
        read -p "请选择: " group
        case $group in
            a) python run_tests.py nlp ;;
            b) python run_tests.py context ;;
            c) python run_tests.py async ;;
            d) python run_tests.py api ;;
            *) echo "无效选择" ;;
        esac
        ;;
    5)
        echo "生成测试报告..."
        python verify_fixes.py
        ;;
    6)
        echo "生成测试覆盖率报告..."
        pytest --cov=src/xwe --cov-report=html --cov-report=term
        echo "HTML 报告已生成到 htmlcov/index.html"
        ;;
    0)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选择"
        ;;
esac

echo ""
echo "完成！按回车键继续..."
read
