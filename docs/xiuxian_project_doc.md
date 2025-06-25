# 修仙世界模拟器 - 项目开发文档

## 目录
1. [项目概述](#1-项目概述)
2. [技术架构](#2-技术架构)
3. [项目结构](#3-项目结构)
4. [开发步骤](#4-开发步骤)
5. [详细实施计划](#5-详细实施计划)

---

## 1. 项目概述

### 1.1 项目信息
- **项目名称**：修仙世界模拟器 (Cultivation World Simulator)
- **版本**：v1.0.0
- **开发周期**：预计4-6周
- **目标平台**：Web浏览器（桌面端优先）

### 1.2 核心特性
- 水墨风格UI设计
- 角色创建与成长系统
- 探索与战斗系统
- 修炼与境界系统
- 成就收集系统
- 本地存档功能

### 1.3 技术栈
- **后端**：Python Flask
- **前端**：HTML5 + Tailwind CSS + Vanilla JavaScript
- **数据存储**：JSON文件 + LocalStorage
- **部署**：本地开发服务器 → 云服务器

---

## 2. 技术架构

### 2.1 系统架构图
```
┌─────────────────────────────────────────────────┐
│                   前端界面                        │
│  ┌─────────────┬──────────────┬──────────────┐  │
│  │  HTML模板   │  Tailwind CSS │  JavaScript  │  │
│  └─────────────┴──────────────┴──────────────┘  │
│                       ↕                          │
│                  AJAX/Fetch API                  │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                Flask Web服务器                    │
│  ┌──────────┬────────────┬──────────────────┐  │
│  │  路由层  │   业务逻辑  │    数据访问层    │  │
│  └──────────┴────────────┴──────────────────┘  │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                  数据存储层                       │
│  ┌────────────────┬─────────────────────────┐  │
│  │   JSON文件     │      LocalStorage       │  │
│  └────────────────┴─────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 2.2 核心模块
1. **游戏引擎模块**：处理游戏逻辑、状态管理
2. **角色系统模块**：角色创建、属性管理、成长计算
3. **事件系统模块**：随机事件、剧情推进
4. **战斗系统模块**：战斗逻辑、伤害计算
5. **UI渲染模块**：界面更新、动画效果
6. **存档系统模块**：游戏保存/加载

---

## 3. 项目结构

```
xiuxian-simulator/
├── README.md                    # 项目说明
├── requirements.txt             # Python依赖
├── run.py                       # 主程序入口
├── config.py                    # 配置文件
│
├── xwe/                         # 核心游戏逻辑
│   ├── __init__.py
│   ├── game_engine.py           # 游戏引擎
│   ├── character.py             # 角色系统
│   ├── cultivation.py           # 修炼系统
│   ├── battle.py                # 战斗系统
│   ├── events.py                # 事件系统
│   └── data/                    # 游戏数据
│       └── restructured/        # JSON数据文件
│           ├── attribute_model.json
│           ├── cultivation_realm.json
│           ├── skill_library.json
│           ├── spiritual_root.json
│           ├── faction_data.json
│           └── achievement.json
│
├── templates/                   # HTML模板
│   ├── base.html                # 基础模板
│   ├── game_enhanced_optimized.html  # 主游戏界面
│   └── components/              # UI组件
│       ├── character_panel.html
│       ├── inventory.html
│       └── map_view.html
│
├── static/                      # 静态资源
│   ├── css/
│   │   ├── style.css            # 主样式
│   │   └── tailwind.css         # Tailwind配置
│   ├── js/
│   │   ├── main.js              # 主逻辑
│   │   ├── player_profile.js    # 角色管理
│   │   ├── game_ui.js           # UI控制
│   │   └── utils.js             # 工具函数
│   ├── images/                  # 图片资源
│   │   ├── backgrounds/
│   │   ├── items/
│   │   └── ui/
│   └── audio/                   # 音频资源
│       ├── intro/
│       ├── bgm/
│       └── sfx/
│
├── tests/                       # 测试文件
│   ├── test_game_engine.py
│   └── test_character.py
│
└── docs/                        # 文档
    ├── API.md                   # API文档
    ├── DESIGN.md                # 设计文档
    └── DEPLOYMENT.md            # 部署文档
```

---

## 4. 开发步骤

### 第一阶段：基础框架搭建（Week 1）
- [ ] 1.1 创建项目结构
- [ ] 1.2 配置Flask应用
- [ ] 1.3 设置基础路由
- [ ] 1.4 创建HTML基础模板
- [ ] 1.5 配置Tailwind CSS

### 第二阶段：核心系统开发（Week 2-3）
- [ ] 2.1 实现角色系统
- [ ] 2.2 实现修炼系统
- [ ] 2.3 实现事件系统
- [ ] 2.4 实现基础战斗系统
- [ ] 2.5 创建JSON数据结构

### 第三阶段：UI界面开发（Week 3-4）
- [ ] 3.1 实现欢迎界面
- [ ] 3.2 实现角色创建界面
- [ ] 3.3 实现主游戏界面
- [ ] 3.4 实现侧边栏功能
- [ ] 3.5 实现弹窗系统

### 第四阶段：功能完善（Week 4-5）
- [ ] 4.1 实现存档系统
- [ ] 4.2 实现成就系统
- [ ] 4.3 添加音效系统
- [ ] 4.4 实现地图系统
- [ ] 4.5 优化用户体验

### 第五阶段：测试与优化（Week 5-6）
- [ ] 5.1 单元测试
- [ ] 5.2 集成测试
- [ ] 5.3 性能优化
- [ ] 5.4 Bug修复
- [ ] 5.5 文档完善

---

## 5. 详细实施计划

### 5.1 第一步：创建基础Flask应用

#### 5.1.1 安装依赖
```bash
pip install flask
pip install flask-cors
```

#### 5.1.2 创建主程序文件
```python
# run.py
from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'your-secret-key'

# 路由定义
@app.route('/')
def index():
    return render_template('game_enhanced_optimized.html')

@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    # 返回游戏状态
    pass

@app.route('/api/game/action', methods=['POST'])
def game_action():
    # 处理游戏动作
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 5.2 第二步：创建HTML基础模板

#### 5.2.1 基础模板结构
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}修仙世界模拟器{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block extra_head %}{% endblock %}
</head>
<body class="bg-gray-100">
    {% block content %}{% endblock %}
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 5.3 第三步：实现角色系统

#### 5.3.1 角色类设计
```python
# xwe/character.py
class Character:
    def __init__(self, name, age, spiritual_root):
        self.name = name
        self.age = age
        self.spiritual_root = spiritual_root
        self.realm = "炼气期"
        self.level = 1
        self.hp = 100
        self.mp = 100
        # ... 其他属性
```

### 5.4 第四步：创建水墨风格CSS

#### 5.4.1 主题样式
```css
/* static/css/style.css */
:root {
    --ink-black: #1a1a1a;
    --ink-gray: #4a4a4a;
    --paper-white: #f5f5f5;
    --accent-red: #8b0000;
}

.ink-border {
    border: 2px solid var(--ink-black);
    border-radius: 0;
    box-shadow: 3px 3px 0 rgba(0,0,0,0.1);
}

.ink-wash {
    background: linear-gradient(135deg, 
        rgba(26,26,26,0.05) 0%, 
        rgba(26,26,26,0.1) 50%, 
        rgba(26,26,26,0.05) 100%);
}
```

### 5.5 后续步骤预览

- **第五步**：实现游戏状态管理
- **第六步**：创建事件系统
- **第七步**：实现UI交互逻辑
- **第八步**：添加动画效果
- **第九步**：实现存档功能
- **第十步**：测试与部署

---

## 附录

### A. 开发规范
- 代码注释使用中文
- 函数命名使用下划线命名法
- 类命名使用驼峰命名法
- Git提交信息格式：`[模块] 功能描述`

### B. 调试技巧
- 使用Chrome开发者工具
- Flask Debug模式
- console.log调试前端
- Python断点调试

### C. 常见问题
- Q: 如何处理中文编码？
- A: 确保所有文件使用UTF-8编码

### D. 参考资源
- Flask官方文档
- Tailwind CSS文档
- MDN Web文档

---

*文档版本：v1.0 | 最后更新：2024*