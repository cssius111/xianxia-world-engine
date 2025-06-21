"""
DeepSeek API 客户端
使用 OpenAI SDK 访问 DeepSeek API
"""

import os
from typing import Dict, Any, Optional, List
from openai import OpenAI

class DeepSeek:
    """
    DeepSeek API 客户端
    兼容 OpenAI API 格式，使用 OpenAI SDK 访问
    """
    
    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        """
        初始化 DeepSeek 客户端
        
        Args:
            api_key: API 密钥，如果不提供则从环境变量读取
            model: 模型名称，可选 "deepseek-chat" (V3) 或 "deepseek-reasoner" (R1)
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables or parameters")
        
        self.model = model
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
    
    def chat(self, prompt: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """
        发送聊天请求
        
        Args:
            prompt: 用户消息
            system_prompt: 系统提示（可选）
            **kwargs: 其他参数（temperature, max_tokens 等）
        
        Returns:
            包含响应文本的字典
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # 设置默认参数
        params = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 500)
        }
        
        # 更新其他参数
        for key in ["top_p", "frequency_penalty", "presence_penalty"]:
            if key in kwargs:
                params[key] = kwargs[key]
        
        try:
            response = self.client.chat.completions.create(**params)
            
            return {
                "text": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            print(f"❌ DeepSeek API 错误: {str(e)}")
            # 返回模拟响应以保持兼容性
            return {
                "text": f"[API错误] {str(e)}",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "model": self.model,
                "finish_reason": "error"
            }
    
    def complete(self, prompt: str, **kwargs) -> str:
        """
        简化的补全方法，直接返回文本
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数
        
        Returns:
            生成的文本
        """
        response = self.chat(prompt, **kwargs)
        return response["text"]
    
    def stream_chat(self, prompt: str, system_prompt: str = None, **kwargs):
        """
        流式聊天响应
        
        Args:
            prompt: 用户消息
            system_prompt: 系统提示（可选）
            **kwargs: 其他参数
        
        Yields:
            响应文本片段
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        params = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 500)
        }
        
        try:
            stream = self.client.chat.completions.create(**params)
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"[API错误] {str(e)}"

# 兼容性别名
DeepSeekChat = DeepSeek

# 工具函数
def test_connection():
    """测试 DeepSeek API 连接"""
    try:
        client = DeepSeek()
        response = client.chat("Hello, can you hear me?")
        print("✅ DeepSeek API 连接成功!")
        print(f"响应: {response['text'][:100]}...")
        return True
    except Exception as e:
        print(f"❌ DeepSeek API 连接失败: {str(e)}")
        return False

__all__ = ["DeepSeek", "DeepSeekChat", "test_connection"]
