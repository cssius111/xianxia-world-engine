# DeepSeek API 集成文档

## 配置

1. 在 `.env` 文件中设置 API Key：
   ```
   DEEPSEEK_API_KEY=your-api-key-here
   ```

2. API 已配置为使用 OpenAI SDK（DeepSeek 使用兼容格式）

## 使用示例

```python
from deepseek import DeepSeek

# 创建客户端
client = DeepSeek()

# 基本对话
response = client.chat("你好，介绍一下修仙世界")
print(response["text"])

# 使用不同模型
client_v3 = DeepSeek(model="deepseek-chat")     # DeepSeek-V3
client_r1 = DeepSeek(model="deepseek-reasoner")  # DeepSeek-R1
```

## 模型说明

- `deepseek-chat`: 通用对话模型（DeepSeek-V3）
- `deepseek-reasoner`: 推理模型（DeepSeek-R1），适合复杂任务

## 费用提醒

DeepSeek API 是收费服务，请注意控制使用量。
