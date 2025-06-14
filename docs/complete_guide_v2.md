# 修仙世界引擎 - 完整引导系统使用指南

## 系统概述

本系统实现了一个完整的新手引导流程，包括：
1. 欢迎页面（三个选项）
2. 背景音乐系统
3. 角色创建系统
4. 世界背景介绍
5. 功能面板系统
6. 开发者模式

## 快速开始

### 1. 安装依赖

```bash
pip install flask markdown
```

### 2. 添加背景音乐（可选）

在 `static/audio/` 目录下添加MP3音乐文件：
- bgm1.mp3
- bgm2.mp3
- bgm3.mp3

### 3. 启动游戏

```bash
python entrypoints/run_web_ui_optimized.py
```

访问：http://localhost:5001

## 游戏流程

### 新玩家流程

1. **欢迎页面** → 选择"开始游戏"
2. **角色创建** → 设置姓名、分配属性、选择背景
3. **世界介绍** → 了解游戏背景（可跳过）
4. **进入游戏** → 开始冒险

### 老玩家流程

1. **欢迎页面** → 选择"继续游戏"
2. **加载存档** → 自动恢复游戏状态
3. **直接游戏** → 继续冒险

### 开发者模式

1. **欢迎页面** → 选择"开发者模式"
2. **输入密码** → 默认：dev123
3. **启用调试** → 详细错误显示、调试日志

## 功能面板使用

### 左侧状态栏

- **角色信息**：姓名(阵营)、境界(进度%)
- **状态条**：气血值、灵力值（带进度条）
- **功能链接**：3x3表格布局的快捷功能
- **当前位置**：显示所在地点

### 功能面板详解

#### 1. 查看状态
显示角色所有属性：
- 基础信息（姓名、境界、修为）
- 属性点（根骨、悟性、神识、机缘）
- 其他状态（寿元、声望、金币等）

#### 2. 查看背包
- 6x4格子的物品栏
- 点击物品查看详情
- 显示物品数量和描述

#### 3. 修炼系统
- **当前功法**：显示名称和进度（如：青云诀 入门(25%)）
- **功法列表**：不同品阶用颜色区分
- **修炼设置**：输入修炼时长
- **限制提醒**：根据体力、寿元等计算最大修炼时长

#### 4. 成就系统
- 表格显示所有成就
- 未解锁显示"???"
- 包含成就描述

#### 5. 进行探索
- 点击按钮开始探索
- 显示探索结果
- 新地点会高亮显示"(新)"

#### 6. 地图系统
- 层级显示（大区域→子区域）
- 点击可前往的地点
- 新地点特殊标记

#### 7. 当前任务
- 新手引导任务
- 显示任务进度
- 无奖励，仅作指引

#### 8. 保存加载
- 快速保存/加载游戏
- 显示操作结果

#### 9. 帮助文档
- 基本命令列表
- 境界说明
- 游戏提示

## 命令系统

基本命令：
- `探索` - 探索当前区域
- `修炼 [时长]` - 进行修炼
- `前往 [地点]` - 移动到指定地点
- `交谈 [NPC]` - 与NPC对话
- `使用 [物品]` - 使用物品

## 自定义配置

### 修改背景音乐列表

编辑 `templates_enhanced/components/welcome_modal_v2.html`：

```javascript
musicList: [
    '/static/audio/your_music1.mp3',
    '/static/audio/your_music2.mp3'
]
```

### 修改开发者密码

编辑 `templates_enhanced/components/welcome_modal_v2.html`：

```javascript
if (password === 'your_password') {
    // ...
}
```

### 修改角色属性配置

编辑 `routes/character.py` 中的 `BACKGROUND_BONUSES`

### 自定义世界介绍

编辑 `templates_enhanced/components/world_intro.html` 中的文本内容

## 技术架构

### 前端组件

- **GameLauncher**: 游戏启动器，管理欢迎页面和音乐
- **RollSystem**: 角色创建系统
- **WorldIntroSystem**: 世界介绍系统
- **GamePanels**: 功能面板管理器
- **GameUI**: 核心游戏UI（原有系统）

### 后端API

- `/api/character/create` - 创建角色
- `/api/character/info` - 获取角色信息
- `/status` - 获取游戏状态
- `/command` - 处理游戏命令
- `/save_game` - 保存游戏
- `/load_game` - 加载游戏

### 数据流

1. 新会话检测 → 显示欢迎页面
2. 选择开始游戏 → 角色创建
3. 创建完成 → 更新游戏状态
4. 显示世界介绍 → 进入主游戏
5. 游戏中操作 → 通过命令或面板交互

## 常见问题

### Q: 音乐无法自动播放？
A: 现代浏览器限制自动播放，需要用户交互后才能播放。系统已处理此情况。

### Q: 如何重置游戏？
A: 清除浏览器的LocalStorage，或使用隐私模式打开。

### Q: 面板点击外部无法关闭？
A: 确保点击的是半透明遮罩区域，不是面板本身。

### Q: 开发者模式有什么用？
A: 显示详细错误信息，方便调试和开发。

## 后续优化建议

1. **性能优化**
   - 懒加载面板内容
   - 缓存常用数据
   - 优化动画效果

2. **功能扩展**
   - 添加更多背景选择
   - 实现装备系统
   - 添加社交功能

3. **视觉增强**
   - 添加粒子效果
   - 改进动画过渡
   - 响应式优化

4. **音效系统**
   - 添加操作音效
   - 战斗音效
   - 环境音效

## 调试技巧

1. 开启开发者模式查看详细日志
2. 使用浏览器控制台查看网络请求
3. 检查LocalStorage中的数据
4. 使用断点调试JavaScript

## 更新日志

### v2.0.0 (2025-01-XX)
- 重构欢迎页面，添加三选项设计
- 实现完整的功能面板系统
- 优化侧边栏显示
- 添加开发者模式
- 集成背景音乐系统

### v1.0.0
- 初始版本