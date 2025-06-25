# 📚 修仙世界引擎文档

## 🚀 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境**
   - 确保 `.env` 文件包含 `DEEPSEEK_API_KEY`

3. **运行项目**
   ```bash
   python run.py
   ```

## 📖 文档结构

### 📁 setup/ - 安装和配置
- [CLEANUP_PLAN.md](setup/CLEANUP_PLAN.md) - 项目清理计划

### 📁 api/ - API 文档
- DeepSeek API 集成说明

### 📁 tools/ - 工具文档
- [SNAPSHOT_README.md](tools/SNAPSHOT_README.md) - 项目快照系统使用说明

### 📁 archive/ - 历史文档
- 早期清理和重构报告

### ROADMAP
- [ROADMAP.md](ROADMAP.md) - 后续开发计划

## 🔧 实用工具

### 项目健康检查
```bash
python scripts/quick_snapshot.py
```

### 测试 DeepSeek API
```bash
python scripts/test_deepseek_api.py
```

### 完整项目扫描
```bash
python scripts/generate_project_snapshot.py
```

## 🎮 游戏特性

- 修仙世界背景
- 角色成长系统
- 技能系统
- 拍卖行系统
- AI 驱动的 NPC 对话

## 📞 支持

如有问题，请查看相关文档或运行诊断工具。
