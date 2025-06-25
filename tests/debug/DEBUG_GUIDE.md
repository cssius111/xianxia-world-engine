# 🔍 修仙世界引擎 - 调试指南

## 快速诊断步骤

### 1. 运行启动前检查
这是最快速的方式来确认项目是否可以运行：

```bash
cd /path/to/xianxia_world_engine
python tests/debug/startup_check.py
```

如果所有检查都通过，您可以直接启动项目：
```bash
python entrypoints/run_web_ui_optimized.py
```

### 2. 如果启动检查失败

#### 常见问题和解决方案：

**问题1: 缺少依赖包**
```bash
# 确保在虚拟环境中
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# 或
.venv\Scripts\activate  # Windows

# 安装所有依赖
pip install -r requirements.txt
```

**问题2: 配置文件缺失**
```bash
# 如果.env文件不存在
cp .env.example .env

# 编辑.env文件设置必要的配置
# FLASK_SECRET_KEY=your-secret-key-here
```

**问题3: 目录结构不完整**
```bash
# 运行文件系统测试来创建缺失的目录
python tests/debug/test_filesystem.py
# 如果生成了修复脚本
python tests/debug/fix_missing_files.py
```

### 3. 运行完整测试套件

如果快速检查无法解决问题，运行完整的测试套件：

```bash
python tests/debug/run_all_tests.py
```

这会生成详细的HTML报告，在浏览器中打开查看：
```bash
open tests/debug/test_report.html  # Mac
# 或
start tests/debug/test_report.html  # Windows
```

### 4. 测试特定组件

如果只想测试特定部分：

```bash
# 测试导入
python tests/debug/test_imports.py

# 测试文件系统
python tests/debug/test_filesystem.py

# 测试Flask应用
python tests/debug/test_flask_app.py

# 测试数据文件
python tests/debug/test_data_files.py
```

### 5. 前端测试

启动服务器后，可以在浏览器中运行前端测试：
1. 启动服务器: `python entrypoints/run_web_ui_optimized.py`
2. 访问: `http://localhost:5001/static/../tests/debug/frontend_test.html`

## 🛠️ 调试工具说明

### 测试脚本列表

| 脚本名称 | 用途 | 输出 |
|---------|------|------|
| `startup_check.py` | 快速启动前检查 | 控制台输出 + startup_check_report.json |
| `quick_diagnose.py` | 诊断常见问题 | 控制台输出 + 可能生成quick_fix.sh |
| `test_imports.py` | 测试所有Python导入 | import_test_results.json |
| `test_filesystem.py` | 验证文件系统结构 | filesystem_test_results.json + fix_missing_files.py |
| `test_flask_app.py` | 测试Flask应用 | flask_test_results.json |
| `test_data_files.py` | 验证游戏数据文件 | data_validation_results.json |
| `run_all_tests.py` | 运行所有测试 | test_report.json + test_report.html |
| `simple_check.py` | 最基础的检查 | 控制台输出 |

### 生成的文件说明

- `*_results.json` - 各个测试的详细结果
- `test_report.html` - 可视化的综合测试报告
- `fix_missing_files.py` - 自动生成的修复脚本
- `quick_fix.sh` - 快速修复常见问题的脚本
- `data_fix_suggestions.txt` - 数据文件修复建议

## 📋 检查清单

启动项目前，确保以下各项都已完成：

- [ ] Python 3.8或更高版本
- [ ] 创建并激活虚拟环境
- [ ] 安装所有依赖 (`pip install -r requirements.txt`)
- [ ] 创建.env配置文件
- [ ] 所有必要的目录都存在
- [ ] 端口5001未被占用

## 🆘 获取帮助

如果按照以上步骤仍无法解决问题：

1. 查看详细的错误日志
2. 运行 `python tests/debug/run_all_tests.py` 获取完整诊断
3. 查看生成的 `test_report.html` 中的详细信息
4. 检查 `logs/` 目录中的日志文件

## 🎯 快速启动命令

如果一切正常，使用以下命令启动：

```bash
cd /path/to/xianxia_world_engine
python entrypoints/run_web_ui_optimized.py
```

然后访问：
- 主页: http://localhost:5001/welcome
- 开发模式: http://localhost:5001/intro?mode=dev

祝您调试顺利！🎮
