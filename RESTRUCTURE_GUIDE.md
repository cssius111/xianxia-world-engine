# 项目重构工具使用指南

本工具用于整理仙侠世界引擎项目的文件结构，将文件归类到合适的目录中。

## 工具说明

提供了两个版本的重构脚本：
- `restructure_project.py` - Python 版本
- `restructure_project.sh` - Shell 版本

两个脚本功能完全相同，您可以根据喜好选择使用。

## 使用方法

### 1. DRY RUN 模式（预览更改）

默认运行时为 dry-run 模式，只会显示将要执行的操作，不会实际移动任何文件：

**Python 版本：**
```bash
python restructure_project.py
```

**Shell 版本：**
```bash
chmod +x restructure_project.sh  # 首次使用需要添加执行权限
./restructure_project.sh
```

### 2. 执行重构

确认 dry-run 输出无误后，使用 `--execute` 参数执行实际重构：

**Python 版本：**
```bash
python restructure_project.py --execute
```

**Shell 版本：**
```bash
./restructure_project.sh --execute
```

### 3. 指定项目路径

如果不在项目根目录运行，可以指定项目路径：

```bash
python restructure_project.py --project-root /path/to/xianxia_world_engine
# 或
./restructure_project.sh --project-root /path/to/xianxia_world_engine
```

## 重构内容

### 目录创建
- `archive/deprecated/entrypoints/` - 存放废弃的入口文件
- `archive/backups/` - 存放备份文件
- `tests/unit/` - 单元测试
- `tests/web_ui/` - Web UI 相关测试
- `scripts/tools/` - 项目工具脚本
- `docs/progress/` - 开发进度文档
- `docs/guides/` - 使用指南文档
- `output/` - 输出文件

### 文件移动
1. **废弃入口文件** → `archive/deprecated/entrypoints/`
   - main.py, run_game.py, run_web_ui.py 等

2. **测试文件** → `tests/`
   - test_*.py 文件根据名称分类到 unit/ 或 web_ui/

3. **工具脚本** → `scripts/tools/`
   - optimize.sh, verify_*.py, update_imports.py 等

4. **文档** → `docs/`
   - 进度文档到 progress/
   - 指南文档到 guides/

5. **输出文件** → `output/`
   - *.html, *.save, *.json 等

6. **示例文件** → `scripts/`
   - *_example.py, demo_*.py 等

### 清理操作
- 删除所有 `__pycache__` 目录
- 删除所有 `.pyc` 文件

### README 更新
- 自动在 README.md 中添加项目结构说明
- 标注 `run_web_ui_optimized.py` 为主入口

## 注意事项

1. **备份重要数据**：虽然工具设计为非破坏性，但建议在执行前备份重要数据
2. **检查 dry-run 输出**：执行前务必检查 dry-run 模式的输出
3. **Git 状态**：如果项目使用 Git，建议在干净的工作区执行
4. **保留核心功能**：`xwe/` 核心模块目录不会被移动

## 回滚方法

如果需要回滚更改：
1. 使用 Git：`git checkout -- .`
2. 手动恢复：从 archive/ 目录将文件移回原位置

## 问题反馈

如果遇到问题，请检查：
1. 是否在正确的项目根目录运行
2. 是否有足够的文件权限
3. 查看具体的错误信息

祝重构顺利！
