# 项目清理工具集

本目录包含用于清理和重构仙侠世界引擎项目的工具脚本。

## 🛠️ 可用脚本

### 1. cleanup_all.py (推荐)
综合清理脚本，提供一键式清理和重构功能。

```bash
python cleanup_all.py
```

### 2. cleanup_duplicates.py
专门用于查找和删除重复文件。

```bash
python cleanup_duplicates.py
```

### 3. restructure_project.py
重新组织项目目录结构，将文件分类到合适的位置。

```bash
python restructure_project.py
```


## 📋 使用指南

详细使用说明请参见 [CLEANUP_GUIDE.md](CLEANUP_GUIDE.md)

## ⚠️ 注意事项

1. **备份**: 所有操作都会自动创建备份
2. **交互式**: 脚本会询问确认，可以随时取消
3. **报告**: 每次运行都会生成详细的Markdown报告
4. **路径更新**: 重构后需要更新代码中的文件路径引用

## 🔍 发现的主要问题

1. **文件重复严重**
   - spiritual_root.json 在4个位置
   - 多个版本的combat_system.json
   - 嵌套的重复目录结构

2. **目录结构混乱**
   - 缺乏统一的组织规范
   - 同类文件分散在不同位置
   - 存在无意义的嵌套目录

3. **版本管理不当**
   - 使用文件名后缀管理版本
   - 应该使用Git版本控制

## 🎯 清理目标

将混乱的结构：
```
data/restructured/
xwe/data/restructured/
xwe/data/refactored/
(各种重复的JSON文件)
```

整理为清晰的结构：
```
data/
├── game_configs/     # 游戏配置
├── game_data/        # 游戏数据
└── deprecated/       # 废弃文件
```

祝您清理顺利！ 🎉
