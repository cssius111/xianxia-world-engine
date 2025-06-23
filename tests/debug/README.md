# 🧪 修仙世界引擎 - 调试测试套件

本目录包含一系列测试脚本，用于诊断和修复项目中的常见问题。

## 📁 测试脚本说明

### 1. 快速诊断 (`quick_diagnose_debug.py`)
**用途**: 快速检查最常见的问题  
**运行方式**:
```bash
python tests/debug/debug_scripts/quick_diagnose_debug.py
```
**检查内容**:
- Python版本
- 虚拟环境状态
- 关键依赖安装情况
- 项目结构完整性
- 配置文件存在性
- 端口可用性

### 2. 导入测试 (`imports_debug.py`)
**用途**: 测试所有Python模块导入  
**运行方式**:
```bash
python tests/debug/debug_scripts/imports_debug.py
```
**输出文件**: `import_test_results.json`

### 3. 文件系统测试 (`filesystem_debug.py`)
**用途**: 验证项目文件和目录结构  
**运行方式**:
```bash
python tests/debug/debug_scripts/filesystem_debug.py
```
**输出文件**: 
- `filesystem_test_results.json`
- `fix_missing_files.py` (如果有缺失文件)

### 4. Flask应用测试 (`flask_app_debug.py`)
**用途**: 测试Flask应用初始化和路由  
**运行方式**:
```bash
python tests/debug/debug_scripts/flask_app_debug.py
```
**输出文件**: `flask_test_results.json`

### 5. 数据文件验证 (`data_files_debug.py`)
**用途**: 验证游戏数据文件的完整性和格式  
**运行方式**:
```bash
python tests/debug/debug_scripts/data_files_debug.py
```
**输出文件**: 
- `data_validation_results.json`
- `data_fix_suggestions.txt` (如果有问题)

### 6. 综合测试运行器 (`run_all_tests_debug.py`)
**用途**: 运行所有测试并生成综合报告  
**运行方式**:
```bash
python tests/debug/debug_scripts/run_all_tests_debug.py
```
**输出文件**: 
- `test_report.json`
- `test_report.html` (可在浏览器中查看)

### 7. 前端测试页面 (`frontend_test.html`)
**用途**: 在浏览器中测试前端功能  
**使用方式**:
1. 启动Flask服务器
2. 在浏览器中打开: `http://localhost:5001/static/../tests/debug/frontend_test.html`
3. 或直接双击打开HTML文件

## 🚀 推荐测试流程

### 首次运行或遇到问题时:

1. **快速诊断**
   ```bash
   python tests/debug/debug_scripts/quick_diagnose_debug.py
   ```
   这会快速识别最常见的问题。

2. **如果快速诊断发现问题，运行综合测试**
   ```bash
   python tests/debug/debug_scripts/run_all_tests_debug.py
   ```
   这会生成详细的测试报告。

3. **查看HTML报告**
   在浏览器中打开 `test_report.html` 查看可视化报告。

4. **根据报告修复问题**
   - 如果有文件缺失: `python tests/debug/fix_missing_files.py`
   - 如果有依赖问题: `pip install -r requirements.txt`
   - 如果有配置问题: `cp .env.example .env`

5. **重新运行测试确认修复**
   ```bash
   python tests/debug/debug_scripts/quick_diagnose_debug.py
   ```

## 🔧 常见问题解决

### 问题1: 模块导入失败
**解决方案**:
```bash
# 确保在虚拟环境中
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 问题2: 文件或目录缺失
**解决方案**:
```bash
# 运行自动生成的修复脚本
python tests/debug/fix_missing_files.py
```

### 问题3: 端口被占用
**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :5001  # Linux/Mac
# 或
netstat -ano | findstr :5001  # Windows

# 结束进程或更改端口
```

### 问题4: 配置文件缺失
**解决方案**:
```bash
cp .env.example .env
# 然后编辑 .env 文件设置必要的配置
```

## 📊 测试结果文件

所有测试结果都保存为JSON格式，便于程序化处理：

- `import_test_results.json` - 模块导入测试结果
- `filesystem_test_results.json` - 文件系统测试结果
- `flask_test_results.json` - Flask应用测试结果
- `data_validation_results.json` - 数据验证结果
- `test_report.json` - 综合测试报告

## 💡 开发提示

1. **添加新测试**: 创建新的测试脚本并在 `run_all_tests_debug.py` 中注册。

2. **自定义测试**: 可以修改现有测试脚本添加特定的检查。

3. **CI/CD集成**: 这些测试脚本可以集成到CI/CD流程中。

4. **调试模式**: 在开发时可以单独运行特定的测试脚本。

## 🆘 需要帮助？

如果测试发现的问题无法解决，请：

1. 保存所有测试结果文件
2. 查看 `test_report.html` 中的详细信息
3. 在项目Issue中报告问题，附上测试结果

---

祝测试顺利！🎮
