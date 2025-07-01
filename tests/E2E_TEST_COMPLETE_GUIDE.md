# E2E 测试套件 - 完整测试报告

## 🎯 测试覆盖范围

本测试套件包含8个主要测试场景和1个性能测试套件，全面覆盖了xianxia-world-engine的核心功能：

### 主要测试场景

1. **Web UI 首屏正常渲染**
   - 验证首页加载（状态码200）
   - 验证页面标题包含"修仙世界引擎"
   - 验证核心UI元素存在
   - 支持不同的初始页面（intro/game）

2. **角色创建流程**
   - 导航到角色创建页面
   - 点击"开始新游戏"
   - 填写角色信息（姓名、性别、背景）
   - 创建角色并进入游戏
   - 验证角色名称正确显示

3. **异步探索API测试**
   - 尝试异步API（/api/explore_async）
   - 降级到同步API（/command）
   - 轮询任务状态
   - 验证返回结果包含reward

4. **状态管理测试**
   - 写入状态转换（IDLE → EXPLORING → COMBAT）
   - 验证state_transitions.log文件
   - 解析并验证JSON日志条目
   - 验证from/to字段的正确性

5. **缓存机制测试**
   - 第一次请求/api/data/lore记录时间
   - 第二次请求验证缓存命中（更快）
   - 模拟TTL过期后的请求
   - 支持降级到/lore/world端点

6. **日志轮转测试**
   - 写入数据超过LOG_MAX_BYTES（1MB）
   - 验证app.log.1.gz文件生成
   - 验证原始日志文件被截断
   - 检测不同的日志轮转机制

7. **Visual: 游戏界面截图**
   - 创建测试角色
   - 导航到游戏界面
   - 等待完全加载
   - 保存全页截图到test-results/screenshots/

8. **UI交互功能测试**（新增）
   - 测试探索功能的UI交互
   - 测试命令输入和执行
   - 验证响应和结果显示

### 性能测试

- **API响应时间测试**
  - 测试多个端点的响应时间
  - 验证响应时间 < 1秒
  - 生成性能测试总结报告

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装Node.js依赖
npm install

# 安装 Python 依赖
pip install -r requirements.txt

# 安装Playwright浏览器
npx playwright install
```

### 2. 设置E2E路由

运行自动设置脚本：
```bash
python3 scripts/setup_e2e.py
```

或手动在`run.py`中添加（在`app = create_app()`后）：
```python
# Register E2E test routes in development/test mode
if os.getenv('FLASK_ENV') in ['development', 'testing'] or os.getenv('ENABLE_E2E_API') == 'true':
    try:
        from routes.api_e2e import register_e2e_routes
        register_e2e_routes(app)
        logger.info("E2E test API endpoints enabled")
    except ImportError as e:
        logger.debug(f"E2E test routes not loaded: {e}")
```

### 3. 运行测试


#### 直接使用Playwright
```bash
# 运行所有浏览器的测试
npx playwright test tests/e2e_full.spec.ts --headed

# 只运行Chromium
npx playwright test tests/e2e_full.spec.ts --headed --project=chromium

# 运行特定测试
npx playwright test tests/e2e_full.spec.ts --headed -g "Web UI"
```

## 📊 测试结果

### 查看报告
```bash
# 生成并打开HTML报告
npx playwright show-report

# 查看测试截图
ls test-results/screenshots/

# 查看失败测试的视频
ls test-results/
```

### 测试产物
- **HTML报告**: `playwright-report/index.html`
- **JSON结果**: `test-results/results.json`
- **截图**: `test-results/screenshots/`
- **视频**: `test-results/` (失败的测试)
- **性能指标**: `test-results/performance-metrics.json`

## 🛠️ 测试配置

### 浏览器配置
- **Chromium**: 桌面版Chrome
- **Firefox**: 桌面版Firefox  
- **WebKit**: 桌面版Safari
- **Mobile Chrome**: Pixel 5设备
- **Mobile Safari**: iPhone 12设备

### 超时配置
- **测试超时**: 90秒
- **动作超时**: 15秒
- **导航超时**: 30秒

### 重试策略
- **本地**: 1次重试
- **CI环境**: 2次重试

## ⚙️ 高级功能

### 1. 软断言（Soft Assertions）
所有测试使用`expect.soft()`，即使某个断言失败也会继续执行，收集所有问题。

### 2. 测试步骤（Test Steps）
每个测试分解为多个步骤，便于调试和理解失败原因。

### 3. 智能降级
- API不存在时自动降级到替代端点
- 异步API降级到同步API
- 缺失功能时记录但不失败

### 4. 日志辅助类
`LogHelper`提供完整的日志操作功能：
- 读写日志文件
- 解析JSON日志
- 检查文件存在和大小
- 等待文件创建

### 5. 性能监控
- 记录每个API的响应时间
- 生成性能总结报告
- 识别最慢的端点

## 🐛 故障排查

### 常见问题

1. **服务器启动失败**
   ```bash
   # 检查端口占用
   lsof -i :5001
   
   # 查看服务器日志
   tail -f logs/flask_test.log
   ```

2. **E2E路由未找到**
   - 确保已运行`scripts/setup_e2e.py`
   - 检查`ENABLE_E2E_API=true`环境变量

3. **测试超时**
   - 增加`playwright.config.ts`中的timeout值
   - 检查网络连接
   - 确保服务器正常响应

4. **浏览器未安装**
   ```bash
   # 重新安装浏览器
   npx playwright install --force
   
   # 安装系统依赖
   npx playwright install-deps
   ```

### 调试技巧

1. **使用调试模式**
   ```bash
   npx playwright test tests/e2e_full.spec.ts --debug
   ```

2. **查看测试追踪**
   ```bash
   npx playwright show-trace test-results/.../trace.zip
   ```

3. **只运行失败的测试**
   ```bash
   npx playwright test --last-failed
   ```

## 📈 测试指标

### 预期性能基准
- 首页加载: < 3秒
- API响应: < 1秒  
- 缓存命中: < 100ms
- 角色创建: < 5秒
- 探索操作: < 2秒

### 测试覆盖率
- UI渲染: ✅
- 用户交互: ✅
- API端点: ✅
- 状态管理: ✅
- 缓存系统: ✅
- 日志系统: ✅
- 错误处理: ✅
- 性能监控: ✅

## 🔄 持续集成

### GitHub Actions配置示例
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm ci
          npx playwright install --with-deps
          
      - name: Run E2E tests
        run: |
          export ENABLE_E2E_API=true
          npx playwright test tests/e2e_full.spec.ts --headless
          
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: |
            playwright-report/
            test-results/
          retention-days: 30
```

## 📝 总结

这个E2E测试套件提供了：
- ✅ 全面的功能覆盖
- ✅ 多浏览器支持
- ✅ 性能监控
- ✅ 视觉回归测试
- ✅ 智能错误处理
- ✅ 详细的测试报告
- ✅ CI/CD集成支持

通过运行这些测试，可以确保xianxia-world-engine的所有核心功能正常工作，并且在不同浏览器和设备上都有良好的表现。
