# 🚀 修仙世界引擎 - 开发者快速上手指南

**适用版本**：v2.0  
**更新日期**：2025年1月23日  
**阅读时间**：10分钟

---

## 🎯 一分钟了解项目

**修仙世界引擎**是一个基于Web的文本冒险游戏引擎，专为修仙题材游戏设计。如果你想：
- 创建自己的修仙游戏
- 学习现代Web游戏开发
- 为项目贡献代码
- 开发游戏MOD

这份指南将帮助你快速上手！

---

## 🛠️ 环境准备

### 必需环境
- **Python** 3.8+
- **Node.js** 14+（可选，用于前端工具）
- **Git** 2.0+
- **现代浏览器**（Chrome/Firefox/Safari）

### 推荐工具
- **VS Code** - 代码编辑器
- **Postman** - API测试
- **Chrome DevTools** - 前端调试

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-repo/xianxia_world_engine.git
cd xianxia_world_engine
```

### 2. 安装依赖
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 配置环境
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑.env文件，设置必要的配置
# FLASK_ENV=development
# FLASK_DEBUG=True
# SECRET_KEY=your-secret-key
```

### 4. 启动项目
```bash
# 运行开发服务器
python entrypoints/run_web_ui_optimized.py

# 访问游戏
# http://localhost:5001/welcome
```

---

## 📁 项目结构速览

```
xianxia_world_engine/
├── 📊 data/               # 游戏数据文件
│   └── restructured/      # JSON配置文件
├── 🎨 static/             # 静态资源
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript代码
│   └── audio/             # 音频资源
├── 📱 templates/          # HTML模板
├── 🔧 api/                # API接口
├── 🧪 tests/              # 测试文件
└── 📝 docs/               # 项目文档
```

---

## 💻 核心概念理解

### 1. 游戏数据结构
```json
// data/restructured/attribute_model.json
{
  "basic_attributes": {
    "health": { "base": 100, "growth": 10 },
    "mana": { "base": 50, "growth": 5 }
  }
}
```

### 2. 事件系统
```javascript
// 监听游戏事件
gameController.on('player:levelup', (data) => {
    console.log(`玩家升级到 ${data.level} 级！`);
});

// 触发事件
gameController.emit('player:levelup', { level: 10 });
```

### 3. 模块注册
```javascript
// 创建新模块
class MyCustomModule {
    init(eventBus) {
        this.eventBus = eventBus;
        // 模块初始化逻辑
    }
}

// 注册模块
gameController.registerModule('myModule', new MyCustomModule());
```

---

## 🔧 常见开发任务

### 1. 添加新的游戏命令
```javascript
// static/js/commands/my_command.js
export const myCommand = {
    name: 'mycommand',
    description: '我的自定义命令',
    execute(args, gameState) {
        // 命令逻辑
        return {
            success: true,
            message: '命令执行成功！'
        };
    }
};
```

### 2. 创建新的UI组件
```javascript
// static/js/components/my_component.js
export class MyComponent {
    constructor(container) {
        this.container = container;
    }
    
    render() {
        this.container.innerHTML = `
            <div class="my-component">
                <!-- 组件内容 -->
            </div>
        `;
    }
}
```

### 3. 添加API接口
```python
# api/routes/my_route.py
from flask import Blueprint, jsonify

my_bp = Blueprint('my_route', __name__)

@my_bp.route('/api/my-endpoint', methods=['GET'])
def my_endpoint():
    return jsonify({
        'status': 'success',
        'data': {}
    })
```

---

## 🧪 测试指南

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_player.py

# 查看覆盖率
pytest --cov=.

# 运行前端测试
npm test
```

### 编写测试
```python
# tests/test_my_feature.py
def test_my_feature():
    # 准备测试数据
    player = Player(name="测试玩家")
    
    # 执行测试
    result = player.level_up()
    
    # 断言结果
    assert player.level == 2
    assert result.success == True
```

---

## 🐛 调试技巧

### 1. 开启调试模式
```bash
# 在URL中添加 ?mode=dev
http://localhost:5001/game?mode=dev
```

### 2. 使用浏览器控制台
```javascript
// 查看游戏状态
window.gameController.state

// 手动触发事件
window.gameController.emit('debug:showState');

// 查看已注册模块
window.gameController.modules
```

### 3. 后端调试
```python
# 使用Flask调试器
import pdb; pdb.set_trace()

# 或使用日志
import logging
logging.debug(f"当前状态: {game_state}")
```

---

## 📦 打包部署

### 1. 生产构建
```bash
# 优化前端资源
npm run build

# 设置生产环境
export FLASK_ENV=production
```

### 2. Docker部署
```bash
# 构建镜像
docker build -t xianxia-world .

# 运行容器
docker run -p 5000:5000 xianxia-world
```

### 3. 性能优化检查
```bash
# 运行性能测试
python scripts/performance_test.py

# 检查资源大小
python scripts/check_bundle_size.py
```

---

## 🤝 贡献指南

### 1. 提交规范
```bash
# 功能添加
git commit -m "feat: 添加新的修炼系统"

# Bug修复
git commit -m "fix: 修复战斗计算错误"

# 文档更新
git commit -m "docs: 更新API文档"
```

### 2. 代码风格
- JavaScript: ESLint + Prettier
- Python: Black + Flake8
- CSS: Stylelint

### 3. Pull Request流程
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 编写测试
5. 提交PR

---

## 📚 进阶资源

### 官方文档
- [完整API文档](./docs/api/)
- [架构设计文档](./docs/architecture/)
- [游戏设计文档](./docs/design/)

### 示例代码
- [自定义模块示例](./examples/custom_module/)
- [MOD开发示例](./examples/mod_development/)
- [插件开发示例](./examples/plugin_development/)

### 社区资源
- [Discord开发者频道](#)
- [Wiki教程](#)
- [视频教程](#)

---

## ❓ 常见问题

### Q: 如何添加新的修炼境界？
A: 编辑 `data/restructured/cultivation_realm.json`，添加新的境界配置。

### Q: 如何自定义UI主题？
A: 创建新的CSS文件，覆盖 `static/css/ink_style.css` 中的变量。

### Q: 如何处理游戏存档？
A: 存档保存在 `saves/` 目录，使用JSON格式，可以直接编辑。

### Q: 如何提高游戏性能？
A: 启用缓存、使用CDN、开启Gzip压缩、优化数据库查询。

---

## 🎉 开始你的修仙之旅！

现在你已经掌握了基础知识，可以开始：
- 🎮 创建自己的游戏内容
- 🛠️ 开发新的游戏功能
- 🎨 设计独特的UI主题
- 🤝 为项目贡献代码

**祝你开发愉快，早日飞升！**

---

*如有问题，欢迎在GitHub提Issue或加入我们的Discord社区*
