# 仙侠世界引导系统 - 实现指南

## 概述

本文档描述了仙侠世界引擎的新手引导系统实现，包括欢迎页面、世界观介绍和角色创建流程。

## 系统架构

### 1. 文件结构

```
xianxia_world_engine/
├── lore/                           # 世界观内容目录
│   └── intro.md                    # 世界观介绍文档
├── routes/                         # API路由模块
│   ├── __init__.py
│   ├── lore.py                     # 世界观API
│   └── character.py                # 角色API
├── templates_enhanced/components/   # UI组件
│   ├── welcome_modal.html          # 欢迎页面
│   ├── lore_modal.html             # 世界观展示
│   └── roll_modal.html             # 角色创建
└── static/js/
    └── lore.js                     # 世界观系统JS
```

### 2. 引导流程

1. **新玩家进入游戏**
   - 检测是否为新会话
   - 显示欢迎页面

2. **选择"开始新游戏"**
   - 隐藏欢迎页面
   - 显示世界观介绍（分页展示）

3. **完成世界观阅读**
   - 标记已读状态（localStorage）
   - 显示角色创建面板

4. **创建角色**
   - 填写角色信息
   - 分配属性点
   - 选择出身背景
   - 提交到后端创建

5. **进入游戏主界面**
   - 刷新游戏状态
   - 开始游戏

## API接口

### 世界观相关

- `GET /api/lore` - 获取默认世界观内容
- `GET /api/lore/<filename>` - 获取指定剧情文件
- `GET /api/lore/list` - 列出所有剧情文件

### 角色相关

- `POST /api/character/create` - 创建新角色
- `GET /api/character/info` - 获取角色信息

## 前端组件

### 1. LoreSystem（世界观系统）

```javascript
// 显示世界观
LoreSystem.showLore(onComplete)

// 检查是否新玩家
LoreSystem.isNewPlayer()

// 标记已看过介绍
LoreSystem.markIntroSeen()
```

### 2. WelcomeSystem（欢迎系统）

```javascript
// 显示欢迎页面
WelcomeSystem.show()

// 开始新游戏流程
WelcomeSystem.startNewGame()
```

### 3. RollSystem（角色创建系统）

```javascript
// 显示角色创建面板
RollSystem.show()

// 调整属性
RollSystem.adjustAttribute(attr, delta)

// 随机生成
RollSystem.randomAll()
```

## 后端集成

### 1. 注册蓝图

```python
# run_web_ui_optimized.py
from routes import lore, character

app.register_blueprint(lore.bp)
app.register_blueprint(character.bp)
```

### 2. 角色创建逻辑

```python
# 背景加成配置
BACKGROUND_BONUSES = {
    'poor': {...},      # 寒门子弟
    'merchant': {...},  # 商贾之家
    'scholar': {...},   # 书香门第
    'martial': {...}    # 武林世家
}
```

## 配置选项

### 1. 世界观内容

编辑 `lore/intro.md` 文件，使用 `---` 分隔章节：

```markdown
# 第一章标题
内容...

---

# 第二章标题
内容...
```

### 2. 角色属性配置

在 `routes/character.py` 中调整：

- 基础属性值
- 背景加成
- 初始金币

### 3. UI样式

各组件都包含独立的样式定义，可在对应的HTML文件中调整。

## 开发建议

### 1. 添加新的剧情章节

```bash
# 创建新章节文件
echo "# 章节内容" > lore/chapter1.md
```

### 2. 扩展背景选项

在 `character.py` 中添加新背景：

```python
BACKGROUND_BONUSES['新背景'] = {
    'name': '背景名称',
    'bonuses': {...},
    'gold_multiplier': 1.0
}
```

### 3. 添加动画效果

在对应的CSS中添加：

```css
@keyframes customAnimation {
    from { ... }
    to { ... }
}
```

## 测试清单

- [ ] 新玩家流程完整性
- [ ] 老玩家直接进入游戏
- [ ] 世界观分页切换
- [ ] 键盘快捷键支持
- [ ] 角色创建验证
- [ ] 属性点分配限制
- [ ] 移动端适配
- [ ] 错误处理

## 后续优化建议

1. **多语言支持**
   - 添加 `intro_en.md` 等文件
   - 实现语言切换功能

2. **语音旁白**
   - 集成Web Audio API
   - 为每个章节配音

3. **动态剧情**
   - 根据玩家选择展示不同内容
   - 使用模板变量

4. **成就系统**
   - 记录玩家阅读进度
   - 解锁隐藏内容

5. **视觉效果**
   - 添加粒子效果
   - 背景动画
   - 过渡效果优化