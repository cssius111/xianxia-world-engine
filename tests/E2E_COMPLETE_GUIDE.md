# 🧪 E2E 测试套件完整说明

## 📋 测试覆盖范围

### 核心功能测试 (e2e_full.spec.ts)
1. **Web UI 首屏渲染** ✅
   - 验证 HTTP 200 状态码
   - 检查页面标题包含"修仙世界引擎"
   - 验证页面重定向和内容加载

2. **角色创建流程** ✅
   - 导航到角色创建页面
   - 点击"开始新游戏"按钮
   - 填写角色信息
   - 验证创建成功

3. **异步探索 API** ✅
   - POST `/api/explore_async` 创建任务
   - 等待 200ms
   - 轮询 `/api/explore_status/<task_id>` 直到完成
   - 支持降级到同步 API

4. **状态管理** ✅
   - 写入状态转换 (EXPLORING → COMBAT)
   - 验证 `state_transitions.log` 记录
   - 检查 JSON 格式的 from/to 字段

5. **缓存机制** ✅
   - 第一次请求记录时间
   - 第二次请求验证缓存命中（更快）
   - 模拟 TTL 过期测试

6. **日志轮转** ✅
   - 写入超过 LOG_MAX_BYTES 的数据
   - 验证 `app.log.1.gz` 生成
   - 检查原始日志文件被截断

### 扩展功能测试 (e2e_extended.spec.ts)
1. **游戏命令系统** ✅
   - 帮助、移动、背包、修炼等命令
   - 自然语言命令解析
   - 命令路由验证

2. **数据接口** ✅
   - 命格数据 (`/data/destiny`)
   - 气运数据 (`/data/fortune`)
   - 角色模板 (`/data/templates`)

3. **存档系统** ✅
   - 游戏保存
   - 游戏加载
   - 会话管理

4. **NLP 功能** ✅
   - 自然语言命令测试
   - NLP 缓存信息
   - 命令解析验证

5. **抽卡系统** ✅
   - 随机抽卡
   - 模板抽卡
   - 属性映射验证

6. **错误处理** ✅
   - 404 错误
   - 无效命令
   - 空请求处理

7. **并发测试** ✅
   - 并发创建角色
   - 并发探索请求
   - 性能压力测试

8. **界面交互** ✅
   - 响应式设计测试
   - 视口切换
   - 截图生成

9. **SSE 测试** ✅
   - Server-Sent Events 连接
   - 状态流推送验证

10. **性能基准** ✅
    - API 响应时间测试
    - 内存使用监控
    - 性能指标收集

## 🚀 快速开始

### 1. 安装依赖
```bash
# 安装 Node.js 依赖
npm install

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
npx playwright install

# 安装系统依赖（如需要）
npx playwright install-deps
```

### 2. 设置执行权限
```bash
chmod +x run-all-e2e-tests.sh
chmod +x run-e2e-tests.sh
chmod +x test-e2e-verify.sh
```

### 3. 运行测试

#### 完整测试套件（推荐）
```bash
# 有界面模式（可以看到浏览器操作）
npm run test:complete

# 无界面模式（CI/CD 环境）
npm run test:complete:headless

# 或直接运行脚本
./run-all-e2e-tests.sh
```

#### 单独运行测试
```bash
# 只运行核心测试
npm run test:e2e

# 只运行扩展测试
npm run test:extended

# 运行所有测试
npm run test:e2e:all

# 调试模式
npm run test:e2e:debug
```

#### 特定浏览器测试
```bash
# Chrome/Chromium
npm run test:chromium

# Firefox
npm run test:firefox

# Safari/WebKit
npm run test:webkit

# 移动端
npm run test:mobile
```

### 4. 查看结果
```bash
# 查看 HTML 报告
npm run test:report

# 查看测试录像
ls test-results/*.webm

# 查看截图
ls test-results/*.png

# 查看性能指标
cat test-results/performance-metrics.json
```

## 🛠️ 测试配置

### 环境变量
```bash
FLASK_ENV=development      # Flask 环境
ENABLE_E2E_API=true       # 启用 E2E 测试 API
PORT=5001                 # 服务器端口
LOG_MAX_BYTES=1048576     # 日志文件大小限制
TTL=300                   # 缓存 TTL（秒）
```

### Playwright 配置
- **超时时间**: 90秒/测试
- **重试次数**: CI 环境 2 次，本地 1 次
- **视频录制**: 失败时保留
- **截图**: 失败时截图
- **追踪**: 首次重试时记录

## 📊 测试指标

### 预期性能基准
- **首页加载**: < 3 秒
- **API 响应**: < 1 秒
- **缓存命中**: < 100ms
- **命令处理**: < 500ms
- **状态更新**: < 200ms

### 测试覆盖率
- ✅ UI 渲染测试
- ✅ API 功能测试
- ✅ 错误处理测试
- ✅ 性能基准测试
- ✅ 并发压力测试
- ✅ 跨浏览器测试
- ✅ 响应式设计测试
- ✅ 日志系统测试

## 🔧 故障排查

### 常见问题

1. **服务器启动失败**
   ```bash
   # 检查端口占用
   lsof -i :5001
   
   # 查看服务器日志
   tail -f logs/flask_server.log
   ```

2. **模板文件找不到**
   - 确保已修复 `app_factory.py` 中的路径问题
   - 检查 `templates/` 目录是否存在

3. **测试超时**
   - 增加 `playwright.config.ts` 中的 timeout
   - 检查网络连接
   - 确保服务器正常响应

4. **API 404 错误**
   - 确认已注册 E2E 路由
   - 检查 `ENABLE_E2E_API=true` 环境变量
   - 验证路由路径正确

### 调试技巧

1. **使用调试模式**
   ```bash
   npm run test:e2e:debug
   ```

2. **查看详细日志**
   ```bash
   # Flask 日志
   tail -f logs/flask_server.log
   
   # 测试日志
   tail -f logs/app.log
   ```

3. **单独测试某个功能**
   ```bash
   ./run-all-e2e-tests.sh --test "角色创建流程"
   ```

4. **保留测试产物**
   - 测试录像: `test-results/*.webm`
   - 截图: `test-results/*.png`
   - 追踪文件: `test-results/*.zip`

## 📈 持续集成

### GitHub Actions 示例
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
          python-version: '3.10'
          
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm ci
          npx playwright install --with-deps
          
      - name: Run E2E tests
        env:
          CI: true
          FLASK_ENV: testing
          ENABLE_E2E_API: true
        run: npm run test:complete:headless
        
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: |
            playwright-report/
            test-results/
```

## 🎯 测试最佳实践

1. **使用软断言**
   - 使用 `expect.soft()` 确保测试继续执行
   - 收集所有错误后统一报告

2. **添加测试步骤**
   - 使用 `test.step()` 组织测试逻辑
   - 便于调试和报告生成

3. **处理异步操作**
   - 适当使用 `waitFor` 和超时
   - 考虑网络延迟和服务器响应时间

4. **数据清理**
   - 测试后清理测试数据
   - 避免测试间相互影响

5. **截图和录像**
   - 关键步骤截图
   - 失败时保留录像

## 📝 总结

本 E2E 测试套件提供了全面的功能覆盖，包括：

- 🎮 **8 个核心功能测试**
- 🔧 **10+ 个扩展功能测试**
- 🌐 **4 种浏览器支持**
- 📊 **性能基准测试**
- 🔄 **并发和压力测试**
- 📱 **响应式设计测试**

通过运行这些测试，可以确保修仙世界引擎的所有主要功能正常工作，并且性能符合预期标准。
