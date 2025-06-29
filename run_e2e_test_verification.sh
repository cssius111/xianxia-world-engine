#!/bin/bash

# 进入项目目录
cd /Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine

# 输出测试信息
echo "=== 运行 Playwright 测试 ==="
echo "工作目录: $(pwd)"

# 运行 Playwright 测试
npx playwright test --reporter=line 2>&1 | tee test-output.log

# 捕获退出码
EXIT_CODE=$?

# 提取测试摘要
echo ""
echo "=== 测试摘要 ==="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 所有测试通过"
    grep -E "(passed|failed|errors)" test-output.log | tail -1
else
    echo "❌ 测试失败"
    grep -E "(passed|failed|errors)" test-output.log | tail -1
fi

# 清理日志文件
rm -f test-output.log

exit $EXIT_CODE
