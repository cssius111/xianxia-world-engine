# E2E 测试快速开始指南

## 1. 设置权限（Linux/Mac）
```bash
chmod +x run-e2e-tests.sh
```

## 2. 安装依赖
```bash
# 安装 Node.js 依赖
npm install

# 安装 Playwright 浏览器
npx playwright install
```

## 3. 注册 E2E API 路由
在 `run.py` 文件中，找到 `app = create_app()` 这一行，在其后添加：

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

## 4. 运行测试

### 方法 1：使用测试脚本（推荐）
```bash
# 有界面模式
./run-e2e-tests.sh

# 无界面模式
./run-e2e-tests.sh --headless

# 调试模式
./run-e2e-tests.sh --debug
```

### 方法 2：手动运行
```bash
# 1. 启动服务器
ENABLE_E2E_API=true python run.py

# 2. 在另一个终端运行测试
npx playwright test tests/e2e_full.spec.ts --headed
```

### 方法 3：使用 npm 脚本
```bash
# 确保服务器已启动，然后：
npm run test:e2e
```

## 5. 查看测试结果
```bash
# 查看 HTML 报告
npx playwright show-report

# 查看测试录像（失败的测试）
ls test-results/

# 查看性能指标
cat test-results/performance-metrics.json
```

## 故障排查

### 端口被占用
```bash
# 查找占用 5001 端口的进程
lsof -i :5001

# 终止进程
kill -9 <PID>
```

### 测试超时
- 增加 `playwright.config.ts` 中的 timeout 值
- 检查服务器是否正常启动

### API 端点 404
- 确保已添加 E2E 路由注册代码到 `run.py`
- 设置环境变量 `ENABLE_E2E_API=true`

## 测试覆盖的功能

✅ Web UI 首屏渲染
✅ 角色创建流程
✅ 异步探索 API (带降级支持)
✅ 状态管理和日志
✅ 缓存机制测试
✅ 日志轮转验证
✅ 性能基准测试

## 扩展测试

要添加新的测试场景，编辑 `tests/e2e_full.spec.ts` 文件，参考现有测试的结构。
