# 修仙世界引擎

一个基于Web的修仙世界模拟器，采用水墨风格界面。

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动游戏
```bash
python run.py
```

### 3. 访问游戏
打开浏览器访问: http://localhost:5001

## 项目清理

如果需要清理项目中的冗余文件：

```bash
# 安全清理（推荐）
bash cleanup_safe.sh

# 完整清理（谨慎使用）
bash cleanup.sh
```

## 功能特点

- 🎨 水墨风格界面
- 🎮 角色创建系统
- 🗺️ 探索和修炼
- 💾 自动保存功能
- 📱 响应式设计
- ⚡ 内置 `SmartCache` 与 `ExpressionJITCompiler` 提升运行效率

## 环境变量

可选配置（在 `.env` 文件中）：
- `PORT`: 服务器端口（默认: 5001）
- `DEBUG`: 调试模式（默认: true）

## 许可证

MIT License
