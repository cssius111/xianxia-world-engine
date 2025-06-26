#!/bin/bash
# 快速测试角色创建系统

echo "===================="
echo "测试角色创建系统"
echo "===================="

# 检查服务器是否在运行
if ! curl -s http://localhost:5001 > /dev/null; then
    echo "❌ 服务器未运行，请先启动: python run.py"
    exit 1
fi

echo "✅ 服务器正在运行"
echo ""

# 运行API测试
echo "运行API测试..."
python tests/test_character_roll.py

echo ""
echo "===================="
echo "测试完成!"
echo ""
echo "手动测试步骤:"
echo "1. 访问 http://localhost:5001"
echo "2. 点击'开始游戏'"
echo "3. 点击'随机生成'按钮"
echo "4. 检查所有4个属性是否显示"
echo "5. 检查命格是否显示"
echo "6. 点击'确认创建'"
echo "===================="
