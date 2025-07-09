# NLP 模块更新日志

所有关于 NLP（自然语言处理）模块的重要变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 计划中
- 支持本地模型部署
- 增加多语言支持（英文、日文）
- 实现自适应学习功能
- 添加语音输入支持

## [1.0.0] - 2025-01-09

### 新增
- 🎉 首个稳定版本发布
- 核心 NLP 处理器 (`DeepSeekNLPProcessor`)
- 支持 DeepSeek API 集成
- 智能命令解析和意图识别
- 上下文感知功能
- LRU 缓存机制
- 异步处理支持
- 完整的错误处理和回退机制
- 工具路由系统
- 实时监控和统计
- 上下文压缩功能

### 改进
- 优化了 API 调用性能
- 改进了缓存键生成算法
- 增强了错误消息的可读性

### 文档
- 完整的 API 文档
- 架构设计文档
- 运维手册
- 开发指南
- 故障排查指南

## [0.9.0] - 2024-12-20 (Beta)

### 新增
- 初始 NLP 功能实现
- 基础命令解析
- 规则引擎回退
- 简单缓存实现

### 已知问题
- 缓存效率低
- 缺少异步支持
- 错误处理不完善

## [0.8.0] - 2024-12-01 (Alpha)

### 新增
- NLP 模块原型
- DeepSeek API 初步集成
- 基础测试框架

### 实验性
- 命令模式识别
- 简单上下文处理

## 版本对比

### v1.0.0 vs v0.9.0

| 功能 | v0.9.0 | v1.0.0 |
|------|--------|--------|
| API 支持 | 仅 DeepSeek | DeepSeek + OpenAI + Mock |
| 缓存机制 | 简单字典 | LRU + 内存缓存 |
| 异步支持 | ❌ | ✅ |
| 上下文压缩 | ❌ | ✅ |
| 监控功能 | 基础日志 | 完整监控系统 |
| 错误处理 | 基础 | 多级回退 |
| 测试覆盖率 | 60% | 95%+ |

## 迁移指南

### 从 v0.9.x 迁移到 v1.0.0

#### 1. API 变更

**旧版本 (v0.9.x):**
```python
# 返回字典
result = nlp.parse_command("攻击")
command = result["command"]
intent = result["intent"]
```

**新版本 (v1.0.0):**
```python
# 返回 ParsedCommand 对象
result = nlp.parse_command("攻击")
command = result.normalized_command
intent = result.intent
```

#### 2. 配置文件更新

**旧配置:**
```json
{
  "nlp_enabled": true,
  "api_key": "xxx"
}
```

**新配置:**
```json
{
  "nlp_config": {
    "enable_llm": true,
    "llm_provider": "deepseek",
    "cache_enabled": true,
    "cache_size": 100
  }
}
```

#### 3. 异步支持

**新增异步方法:**
```python
# 同步调用（保持兼容）
result = nlp.parse_command("攻击")

# 异步调用（新功能）
result = await nlp.parse_command_async("攻击")
```

#### 4. 工具注册

**旧方式:**
```python
# 直接在代码中硬编码
if command == "cultivate":
    do_cultivation()
```

**新方式:**
```python
# 使用工具路由系统
@register_tool("cultivate")
def cultivate_tool(payload):
    return do_cultivation(payload)
```

### 破坏性变更

1. **`parse_command` 返回类型变更**
   - 影响：所有调用此方法的代码
   - 解决：更新为使用对象属性访问

2. **移除 `parse_batch` 方法**
   - 影响：批量处理逻辑
   - 解决：使用异步方法或循环调用

3. **配置文件结构变更**
   - 影响：部署和配置管理
   - 解决：使用迁移脚本或手动更新

## 性能改进

### v1.0.0 性能提升

- **API 响应时间**: 降低 40%（通过缓存优化）
- **内存使用**: 减少 25%（通过上下文压缩）
- **并发处理**: 提升 3x（通过异步支持）
- **缓存命中率**: 从 45% 提升到 75%

### 基准测试结果

```
测试环境: Python 3.8, 4核 CPU, 8GB RAM

v0.9.0:
- 单次解析: 450ms
- 100次并发: 12.3s
- 内存峰值: 512MB

v1.0.0:
- 单次解析: 270ms
- 100次并发: 4.1s
- 内存峰值: 384MB
```

## 安全更新

### v1.0.0 安全增强

1. **API 密钥管理**
   - 支持环境变量
   - 不再在日志中显示密钥

2. **输入验证**
   - 添加长度限制（最大 1000 字符）
   - 防止注入攻击

3. **速率限制**
   - 默认限制：100 请求/分钟
   - 可配置限流策略

## 贡献者

### v1.0.0 主要贡献者

- 核心开发团队
- NLP 算法优化：AI 研究组
- 文档编写：技术文档组
- 测试：QA 团队

## 相关链接

- [NLP API 文档](docs/api/nlp_api.md)
- [架构设计](docs/architecture/nlp_architecture.md)
- [问题追踪](https://github.com/your-org/xianxia_world_engine/issues)
- [发布说明](https://github.com/your-org/xianxia_world_engine/releases)

## 即将到来

### v1.1.0 预览

- **新功能**
  - 本地模型支持（减少 API 依赖）
  - 批量命令优化
  - 自定义词典支持
  
- **改进**
  - 更智能的上下文理解
  - 降低 API 调用成本
  - 提升缓存效率

- **实验性**
  - 语音输入初步支持
  - 多轮对话理解