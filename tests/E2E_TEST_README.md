# E2E 测试说明文档

## 概述
本测试套件为 xianxia-world-engine 提供全面的端到端测试，验证以下功能：

1. **Web UI 首屏渲染** - 验证页面加载和标题
2. **角色创建流程** - 测试新游戏开始功能
3. **异步探索 API** - 测试异步任务创建和状态轮询
4. **状态管理** - 验证状态转换日志记录
5. **缓存机制** - 测试响应缓存和 TTL
6. **日志轮转** - 验证日志文件自动压缩

## 安装依赖

```bash
# 安装 Node.js 依赖
npm install

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
npx playwright install

# 安装系统依赖（如果需要）
npx playwright install-deps
```

## 运行测试

### 运行完整 E2E 测试套件

```bash
# 有界面模式（推荐，可视化查看测试过程）
npx playwright test tests/e2e_full.spec.ts --headed

# 或使用 npm 脚本
npm run test:e2e

# 无界面模式（CI 环境）
npm run test:e2e:headless

# 调试模式（逐步执行）
npm run test:e2e:debug
```

### 运行特定测试

```bash
# 只运行某个测试
npx playwright test tests/e2e_full.spec.ts -g "Web UI"

# 运行性能测试
npx playwright test tests/e2e_full.spec.ts -g "Performance"
```

### 查看测试报告

```bash
# 生成并打开 HTML 报告
npx playwright show-report

# 或
npm run test:report
```

## 配置说明

### 环境变量

创建 `.env.test` 文件来覆盖测试环境配置：

```env
PORT=5001
LOG_MAX_BYTES=1048576
TTL=300
DEEPSEEK_API_KEY=test-key
```

### Playwright 配置

主要配置在 `playwright.config.ts` 中：

- **timeout**: 90秒（每个测试的最大运行时间）
- **video**: retain-on-failure（失败时保留录像）
- **screenshot**: only-on-failure（失败时截图）
- **trace**: on-first-retry（重试时记录追踪）

## 测试结构

```
tests/
├── e2e_full.spec.ts      # 主测试文件
├── helpers/
│   └── logHelper.ts      # 日志操作辅助函数
├── global-setup.ts       # 全局初始化
└── global-teardown.ts    # 全局清理
```

## 测试数据

- 测试角色名称：`测试道友`
- 测试位置：`青云城`
- 日志文件：`app.log`, `state_transitions.log`

## 故障排查

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :5001
   # 或更改 PORT 环境变量
   PORT=5002 npm run test:e2e
   ```

2. **浏览器未安装**
   ```bash
   npx playwright install chromium
   ```

3. **API 端点不存在**
   - 测试会自动降级到可用的端点
   - 查看控制台输出了解哪些功能未实现

### 调试技巧

1. **使用调试模式**
   ```bash
   npm run test:e2e:debug
   ```

2. **查看测试录像**
   - 失败的测试会在 `test-results/` 目录保存录像

3. **检查日志**
   - 应用日志：`logs/app.log`
   - 测试结果：`test-results/results.json`
   - 性能指标：`test-results/performance-metrics.json`

## CI/CD 集成

### GitHub Actions 示例

```yaml
- name: Install dependencies
  run: |
    npm ci
    npx playwright install --with-deps

- name: Run E2E tests
  run: npm run test:e2e:headless
  env:
    CI: true

- name: Upload test results
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 30
```

## 扩展测试

如需添加新的测试场景，可以在 `e2e_full.spec.ts` 中添加新的 `test()` 块，或创建新的测试文件。

### 测试模板

```typescript
test('新功能测试', async ({ page }) => {
  await test.step('步骤1：准备', async () => {
    // 测试准备代码
  });

  await test.step('步骤2：执行', async () => {
    // 测试执行代码
  });

  await test.step('步骤3：验证', async () => {
    // 使用 expect.soft() 进行非阻塞断言
    expect.soft(result).toBe(expected);
  });
});
```

## 性能基准

预期的性能指标：

- 首屏加载：< 3秒
- API 响应：< 1秒
- 缓存命中：< 100ms
- 日志写入：< 50ms

## 维护建议

1. 定期更新 Playwright 版本
2. 根据新功能添加相应测试
3. 保持测试独立性，避免相互依赖
4. 使用 `expect.soft()` 使测试继续执行
5. 添加充分的日志输出便于调试
