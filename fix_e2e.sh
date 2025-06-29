#!/bin/bash

echo "🔧 开始修复 Playwright E2E 测试问题..."

# 1. 备份原始文件
echo "📦 备份原始文件..."
cp tests/e2e_full.spec.ts tests/e2e_full.spec.ts.backup

# 2. 修复 adminRequestContext 问题
echo "🔨 修复 adminRequestContext 问题..."

# 创建一个 Python 脚本来修复文件
cat > fix_e2e.py << 'EOF'
import re

# 读取文件
with open('tests/e2e_full.spec.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修复导入语句
old_import = "import { test, expect, Page, BrowserContext } from '@playwright/test';"
new_import = "import { test, expect, Page, BrowserContext, APIRequestContext, request } from '@playwright/test';"
content = content.replace(old_import, new_import)

# 2. 删除 adminRequestContext 函数
# 查找并删除整个函数
pattern = r'// Admin request context fixture for bypassing CSRF\s*\n.*?const adminRequestContext.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n};'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# 3. 在类型声明中添加 apiContext
# 查找 let logHelper: LogHelper; 并在其后添加
if 'let logHelper: LogHelper;' in content and 'let apiContext: APIRequestContext;' not in content:
    content = content.replace(
        'let logHelper: LogHelper;',
        'let logHelper: LogHelper;\n  let apiContext: APIRequestContext;'
    )

# 4. 修复 beforeAll 中的 apiContext 初始化
# 查找 apiContext = await adminRequestContext({ playwright }); 并替换
old_api_init = re.search(r'apiContext = await adminRequestContext\({ playwright }\);', content)
if old_api_init:
    new_api_init = '''apiContext = await request.newContext({
      baseURL: config.BASE_URL,
      extraHTTPHeaders: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    });'''
    content = re.sub(r'apiContext = await adminRequestContext\({ playwright }\);', new_api_init, content)

# 写回文件
with open('tests/e2e_full.spec.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 文件修复完成！")
EOF

# 运行修复脚本
python fix_e2e.py

# 清理临时文件
rm fix_e2e.py

echo "✅ 所有修复已完成！"
echo ""
echo "📋 下一步："
echo "1. 运行测试验证修复："
echo "   npx playwright test tests/e2e_full.spec.ts --headed"
echo ""
echo "2. 如果还有问题，查看备份文件："
echo "   tests/e2e_full.spec.ts.backup"
echo ""
echo "3. 查看测试报告："
echo "   npx playwright show-report"