# 修仙世界水墨风格UI

## 快速开始

1. **运行修复脚本**
   ```bash
   python scripts/quick_fix.py
   ```

2. **启动服务器**
   ```bash
   python entrypoints/run_web_ui_optimized.py
   ```

3. **访问页面**
   打开浏览器访问 http://localhost:5001

## 页面流程

1. **开始页面** (`/`) - 水墨风格的欢迎界面
2. **选择开局** (`/choose`) - 三种开局方式
3. **抽卡页面** (`/roll`) - 生成角色属性
4. **游戏主界面** (`/game`) - 游戏核心界面

## 特性

- ✅ 水墨主题CSS设计
- ✅ LongCang字体（通过Google Fonts）
- ✅ 角色8维属性系统
- ✅ 保底机制（小保底/大保底）
- ✅ 三种角色生成方式（随机/模板/自定义）
- ✅ 左侧属性面板布局
- ✅ 响应式设计

## 已知问题修复

1. **背景纹理404**: 已使用CSS渐变作为fallback
2. **路由冲突**: 已注释掉可能冲突的模块
3. **输入框bug**: 已在main.js中修复

## 目录结构

```
xianxia_world_engine/
├── static/
│   ├── css/
│   │   ├── ink_theme.css    # 水墨主题样式
│   │   └── layout.css       # 布局工具类
│   └── js/
│       ├── main.js          # 主界面逻辑
│       └── roll.js          # 抽卡逻辑
├── templates/
│   ├── base.html            # 基础模板
│   └── screens/
│       ├── start_screen.html # 开始页面
│       ├── choose_start.html # 选择页面
│       ├── roll_screen.html  # 抽卡页面
│       └── game.html        # 游戏主界面
├── scripts/
│   ├── gen_character.py     # 角色生成器
│   ├── quick_fix.py         # 快速修复脚本
│   └── test_ui.py           # UI测试脚本
└── docs/
    └── character_design.md  # 角色设计文档
```

## 开发提示

- 所有样式遵循水墨风格，避免使用阴影和高光
- 使用CSS变量方便主题定制
- 按钮悬停效果使用背景色变化，不使用阴影
- 属性值根据数值显示不同颜色（人/黄/玄/地/天）

## 下一步计划

- [ ] 实现模板选择UI
- [ ] 添加自定义输入界面
- [ ] 集成DeepSeek API
- [ ] 完善游戏主界面功能
- [ ] 添加更多动画效果
