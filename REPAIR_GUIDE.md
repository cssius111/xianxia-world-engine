# 🔧 修复指南

## 快速开始

如果你遇到导入错误，运行以下命令：

```bash
python ultimate_fix.py
```

这个脚本会自动执行所有必要的修复步骤。

## 可用的修复工具

### 1. **ultimate_fix.py** - 一键修复
最推荐的方法。自动执行所有修复步骤。

### 2. **scripts/fix_typos.py** - 修复文件名错误
搜索并修复文件名拼写错误（如 xceptions.py → exceptions.py）

### 3. **scripts/clean_cache.py** - 清理缓存
删除所有 __pycache__ 目录和 .pyc 文件

### 4. **scripts/comprehensive_fix.py** - 综合修复
智能分析并修复缺失的模块和导入

### 5. **scripts/full_diagnosis.py** - 完整诊断
详细分析当前的所有问题

### 6. **scripts/test_imports.py** - 测试导入
测试关键模块是否能正确导入

### 7. **test_webui.py** - 测试Web UI
直接测试Web UI是否能启动

## 手动修复步骤

如果自动修复失败，请按以下顺序手动执行：

1. **清理缓存**
   ```bash
   python scripts/clean_cache.py
   ```

2. **修复文件名**
   ```bash
   python scripts/fix_typos.py
   ```

3. **运行综合修复**
   ```bash
   python scripts/comprehensive_fix.py
   ```

4. **生成快照**
   ```bash
   python scripts/quick_snapshot.py
   ```

5. **查看错误**
   ```bash
   cat project_snapshot.json | python -m json.tool
   ```

6. **测试结果**
   ```bash
   python scripts/final_verification.py
   ```

## 常见问题

### Q: 还是有 ValidationError 导入错误
A: 检查 `xwe/engine/expression/exceptions.py` 文件是否存在且包含 ValidationError 类

### Q: 找不到 content_ecosystem 模块
A: 确保 `xwe/features/content_ecosystem.py` 文件已创建

### Q: metrics_registry 导入失败
A: 检查 `xwe/metrics/__init__.py` 是否正确导入并创建了 metrics_registry

### Q: Web UI 无法启动
A: 1. 确保所有依赖已安装：`pip install -r requirements.txt`
   2. 运行 `python ultimate_fix.py`
   3. 检查端口 5000 是否被占用

## 启动游戏

修复完成后，运行：

```bash
python entrypoints/run_web_ui_optimized.py
```

然后在浏览器中访问：http://localhost:5000

## 获取帮助

如果问题仍然存在：
1. 查看 `project_snapshot.json` 了解具体错误
2. 查看 `fix_report.json` 了解修复历史
3. 检查 `FIX_SUMMARY.md` 了解详细的修复说明
