# 修仙游戏测试启动指令

## 🎮 手动启动测试（推荐）

### 第一步：启动游戏服务器
在一个终端窗口中运行：
```bash
cd /Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine
python3 start_web.py
```

### 第二步：运行 Playwright 测试
在另一个终端窗口中运行：
```bash
cd /Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine

# 安装 Python 依赖
pip install -r requirements.txt

# 安装浏览器（首次运行需要）
npx playwright install

# 运行可视化测试
npx playwright test --headed --project=chromium xiuxian-game.spec.js

# 或者运行所有测试
npm run test:headed
```

## 🚀 快速启动（一键测试）

给启动脚本添加执行权限并运行：
```bash
chmod +x run-test.sh
./run-test.sh
```

## 📊 查看测试报告
```bash
npx playwright show-report
```

---

现在让我帮你直接运行测试！