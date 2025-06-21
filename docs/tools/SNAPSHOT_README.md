# 项目快照系统使用说明

## 🚀 快速开始

项目快照系统已经部署到你的项目中，包含以下组件：

### 1. 生成的文件

- `scripts/generate_project_snapshot.py` - 完整的项目扫描器
- `scripts/quick_snapshot.py` - 简化版快速扫描器
- `scripts/auto_fix_imports.py` - 自动修复脚本
- `project_snapshot.json` - 当前项目健康状态快照
- `PROJECT_HEALTH_REPORT.md` - 人类可读的分析报告

### 2. 使用步骤

#### 步骤1: 运行自动修复
```bash
cd /Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine
python scripts/auto_fix_imports.py
```

这将会：
- ✅ 创建 deepseek 存根模块
- ✅ 添加缺失的 ContentPreference 类
- ✅ 创建 expression.exceptions 模块
- ✅ 创建 prometheus 监控模块
- ✅ 更新 requirements.txt

#### 步骤2: 安装依赖
```bash
pip install -r requirements.txt
```

#### 步骤3: 设置环境变量
在 `.env` 文件中添加：
```
DEEPSEEK_API_KEY=your-api-key-here
```

#### 步骤4: 验证修复
```bash
python scripts/quick_snapshot.py
```

### 3. 当前问题总结

根据分析，你的项目主要有以下问题：

1. **DeepSeek API 缺失** - 影响 6 个核心模块
2. **ContentPreference 类未定义** - 影响 2 个模块  
3. **子模块文件缺失** - 影响 2 个模块

### 4. AI 分析 Prompt

如果你想让 AI 进一步分析，可以使用：

```
请分析附件中的 project_snapshot.json 文件，这是我的 Python 项目的模块导入健康状况报告。

请帮我：
1. 识别最关键的问题并排序
2. 提供详细的修复步骤
3. 生成可以直接运行的修复代码
4. 建议项目结构优化方案

特别关注 DeepSeek API 的集成问题，这似乎是一个自定义的 LLM 客户端。
```

### 5. 项目结构优化建议

基于扫描结果，建议：

1. **整理导入依赖**
   - 将所有 LLM 相关代码集中到 `xwe.core.nlp` 模块
   - 使用依赖注入避免循环导入

2. **完善存根系统**
   - 为所有外部 API 创建存根接口
   - 支持离线开发模式

3. **改进错误处理**
   - 添加导入失败的优雅降级
   - 提供清晰的错误提示

## 📊 项目健康监控

定期运行以下命令监控项目健康：

```bash
# 生成新快照
python scripts/generate_project_snapshot.py

# 查看错误统计
cat project_snapshot.json | grep "failed_imports"

# 查看具体错误
cat PROJECT_HEALTH_REPORT.md
```

## 🛠 故障排除

如果遇到问题：

1. **权限错误**: 确保对项目目录有写入权限
2. **导入循环**: 检查模块间的依赖关系
3. **环境问题**: 确保使用正确的 Python 版本 (3.12)

## 📧 需要帮助？

- 查看 `PROJECT_HEALTH_REPORT.md` 获取详细分析
- 运行 `python scripts/auto_fix_imports.py` 自动修复
- 将 `project_snapshot.json` 提供给 AI 进行深度分析
