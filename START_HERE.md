# 修仙世界水墨UI - 快速启动指南

## 🎯 立即运行

```bash
# 1. 快速修复（创建必要目录）
python scripts/quick_fix.py

# 2. 启动服务器
python entrypoints/run_web_ui_optimized.py

# 3. 打开浏览器访问
http://localhost:5001
```

## ✅ 已修复的问题

1. **路由冲突**: 注释掉了可能不存在的模块导入
2. **背景图片404**: 使用CSS渐变模拟宣纸纹理效果
3. **静态文件路径**: 修正了static文件夹的路径配置
4. **输入框bug**: 在main.js中修复了事件处理

## 🎨 水墨风格特性

- 使用Google Fonts的LongCang字体
- 淡雅的宣纸背景色 (#f7f7f5)
- 无阴影、无高光的极简设计
- 属性值根据品阶显示不同颜色（人/黄/玄/地/天）
- 流畅的动画效果

## 📁 核心文件

- `/static/css/ink_theme.css` - 水墨主题样式
- `/static/js/roll.js` - 抽卡逻辑
- `/scripts/gen_character.py` - 角色生成器
- `/templates/screens/` - 所有页面模板

## 🎮 游戏流程

1. 开始页面 → 选择开局方式
2. 抽卡页面 → 生成8维属性
3. 确认角色 → 进入游戏主界面

## 💡 提示

- 如果看不到背景纹理，这是正常的（使用了CSS渐变替代）
- 抽卡时可能触发保底（至少1项属性≥8）
- 所有页面都遵循统一的水墨风格设计

## 🚀 下一步

运行 `python scripts/test_ui.py` 进行完整测试
