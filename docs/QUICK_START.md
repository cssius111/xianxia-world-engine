# 🚀 快速开始指南

## ✅ 项目状态

您的修仙世界引擎已经配置完成！

- **DeepSeek API**: ✅ 已配置并测试通过
- **所有依赖**: ✅ 已安装
- **项目结构**: ✅ 已修复所有导入问题

## 🎮 启动游戏

```bash
# Web UI 版本
python run.py

# 命令行版本 (已移除，统一使用 Web UI)
```
## 🛠 初次脚本设置
```bash
chmod +x scripts/*.py
python scripts/dev/gen_character.py
pre-commit install
```


## 🔧 实用工具

项目提供一些脚本用于诊断和维护，可按需执行。
## 📦 安装 NLP 依赖（可选）
```bash
pip install backoff
# 如果需要 DeepSeek SDK:
pip install deepseek
```

若拥有 DeepSeek API 密钥，请在 `.env` 中添加：
```bash
DEEPSEEK_API_KEY=your_api_key_here
```
安装完成后，可直接运行 `python run.py` 启动游戏。


## 📚 文档

所有文档已整理到 `docs/` 文件夹：
- `docs/INDEX.md` - 文档索引
- `docs/api/` - API 相关文档
- `docs/tools/` - 工具使用说明
- `docs/` - 所有文档入口在 `docs/INDEX.md`

## 🎯 下一步

1. 运行 Web UI 开始游戏
2. 查看 `docs/INDEX.md` 了解更多功能
3. 自定义游戏内容和规则

---

祝您游戏愉快！🎮
