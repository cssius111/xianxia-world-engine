# 修仙游戏 Playwright 自动化测试

## 📋 测试概述

这个测试套件专门为修仙游戏设计，能够自动化测试从首页到游戏主界面的完整流程，包括：

- ✅ 页面加载检测
- ✅ "开始游戏"按钮点击
- ✅ 角色抽卡流程
- ✅ 角色创建确认
- ✅ 游戏界面加载验证
- ✅ 错误监控和处理

## 🚀 快速开始

### 方法一：使用自动化脚本（推荐）

```bash
# 1. 给脚本添加执行权限
chmod +x run-test.sh

# 2. 运行测试
./run-test.sh
```

### 方法二：手动运行

```bash
# 1. 安装依赖
npm install

# 安装 Python 依赖
pip install -r requirements.txt

# 2. 安装 Playwright 浏览器
npx playwright install

# 3. 启动你的游戏服务器（另一个终端）
python3 app.py
# 或者
python3 -m http.server 5001

# 4. 运行测试（可视化模式）
npm run test:headed

# 5. 运行特定测试
npx playwright test xiuxian-game.spec.js --headed

# 6. 调试模式
npm run test:debug
```

## 📊 测试报告

测试完成后，会自动生成详细的 HTML 报告：

```bash
# 查看测试报告
npm run test:report
```

## 🔧 配置选项

### playwright.config.js 配置

- **可视化模式**: `headless: false` - 可以看到浏览器操作过程
- **慢速模式**: `slowMo: 500` - 每个操作间隔500ms，便于观察
- **超时设置**: 各种超时配置，避免测试卡死
- **视频录制**: 失败时自动录制视频
- **截图**: 失败时自动截图

### 测试用例

1. **完整游戏流程测试** (`xiuxian-game.spec.js`)
   - 验证从首页到游戏主界面的完整流程
   - 智能检测各种按钮和界面元素
   - 处理抽卡和角色创建流程

2. **游戏界面元素检查**
   - 详细检查游戏界面的各个组件
   - 验证界面元素是否正确显示

3. **错误处理和恢复测试**
   - 监控JavaScript错误
   - 验证页面稳定性

## 🎯 测试目标元素

测试脚本会智能寻找以下元素：

### 开始游戏按钮
- `button:has-text("开始游戏")`
- `button:has-text("开始")`
- `[id*="start"]`
- `[class*="start"]`

### 抽卡界面
- `#roll_modal`
- `.roll-modal`
- `[id*="roll"]`
- `[class*="roll"]`

### 游戏界面
- `#sidebar`
- `#narrative_log`
- `.game-interface`
- `.character-info`

## 🛠️ 自定义测试

如果你的游戏界面元素不同，可以修改 `tests/xiuxian-game.spec.js` 中的选择器：

```javascript
// 例如：添加新的按钮选择器
const startButtonSelectors = [
  'button:has-text("开始游戏")',
  'button:has-text("开始")',
  '#your-custom-start-button',  // 添加你的自定义选择器
  '.your-custom-class'
];
```

## 📝 测试输出

测试运行时会输出详细的步骤信息：

```
=== 开始测试修仙游戏完整流程 ===
步骤 1: 导航到游戏页面
✓ 页面加载完成
步骤 2: 寻找并点击开始游戏按钮
✓ 找到开始按钮: button:has-text("开始游戏")
✓ 已点击开始游戏按钮
步骤 3: 等待抽卡界面加载
✓ 找到抽卡界面: #roll_modal
✓ 抽卡界面已显示
步骤 4: 进行抽卡和角色创建
✓ 找到抽卡按钮: button:has-text("抽取")
✓ 已点击抽卡按钮
✓ 找到创建角色按钮: button:has-text("确认")
✓ 已点击创建角色按钮
步骤 5: 验证游戏主页面加载
✓ 找到游戏界面元素: #sidebar
✓ 游戏界面加载成功，找到 1 个界面元素
✓ 游戏界面元素可见
✓ 页面内容不为空
=== 修仙游戏流程测试完成 ===
```

## 🐛 故障排除

### 常见问题

1. **连接被拒绝 (ERR_CONNECTION_REFUSED)**
   - 确保游戏服务器正在运行
   - 检查端口是否正确（默认5001）

2. **找不到元素**
   - 检查元素选择器是否正确
   - 增加等待时间
   - 查看测试截图了解页面状态

3. **测试超时**
   - 增加超时时间设置
   - 检查网络连接
   - 确保页面加载正常

### 调试技巧

```bash
# 1. 使用调试模式，可以暂停测试
npx playwright test --debug

# 2. 只运行特定测试
npx playwright test --grep "完整游戏流程"

# 3. 查看测试录制的视频
# 视频保存在 test-results/ 目录下

# 4. 查看详细日志
npx playwright test --reporter=list
```

## 📚 更多资源

- [Playwright 官方文档](https://playwright.dev/)
- [CSS 选择器参考](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- [测试最佳实践](https://playwright.dev/docs/best-practices)

## 🤝 贡献

如果你发现测试脚本有问题或者想要添加新的测试用例，欢迎：

1. 创建 Issue 报告问题
2. 提交 Pull Request 改进代码
3. 分享测试经验和技巧

---

**祝你测试愉快！** 🎉