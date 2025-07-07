# 修仙世界引擎 Flask 启动问题解决方案

## 问题诊断

Flask 应用无法正常启动的原因是 `CommandRouter` 在初始化时尝试创建 `DeepSeekNLPProcessor` 实例，这个过程会进行网络连接，导致启动阻塞。

## 解决方案

### 方案 1：使用智能启动器（推荐）
```bash
python smart_start.py
```
这个脚本会自动：
- 检测并解决端口冲突
- 禁用可能阻塞的组件
- 应用运行时修补
- 启动 Flask 服务器

### 方案 2：使用修复版启动脚本
```bash
python fixed_run.py
```

### 方案 3：使用 Shell 脚本
```bash
chmod +x start_fixed.sh
./start_fixed.sh
```

### 方案 4：手动设置环境变量
```bash
export DISABLE_NLP=true
export USE_NLP=false
python run.py --debug
```

## 诊断工具

如果上述方案仍有问题，使用以下诊断工具：

1. **检查端口占用**
   ```bash
   python check_ports.py
   ```

2. **测试最简 Flask**
   ```bash
   python test_minimal_flask.py
   ```

3. **诊断 NLP 模块**
   ```bash
   python diagnose_nlp.py
   ```

4. **快速启动（跳过所有复杂组件）**
   ```bash
   python quick_start.py
   ```

## 永久修复

要永久解决这个问题，建议修改 `src/xwe/core/command_router.py`，将 NLP 处理器改为懒加载模式，只在第一次使用时才初始化。

## 常见问题

1. **端口被占用**
   - 使用 `lsof -i :5001` 查看占用进程
   - 使用 `kill -9 <PID>` 终止进程
   - 或使用其他端口启动

2. **日志文件权限问题**
   - 确保 `logs/` 目录存在且有写权限
   - `mkdir -p logs && chmod 755 logs`

3. **Python 环境问题**
   - 确保使用正确的虚拟环境
   - 重新安装依赖：`pip install -r requirements.txt`

## 联系支持

如果问题仍未解决，请检查：
- `logs/app.log` 中的错误信息
- Python 版本是否兼容
- 所有依赖是否正确安装
