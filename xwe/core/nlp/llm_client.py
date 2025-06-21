"""LLMClient → DeepSeek API 封装（MVP 版）"""
import os
from deepseek import DeepSeek

_DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "demo-key")

class LLMClient:
    """最小可用封装：chat(prompt) → str"""
    def __init__(self, model_name: str = "deepseek-chat"):
        self.model_name = model_name
        self._ds = DeepSeek(api_key=_DEEPSEEK_KEY, model=model_name)

    def chat(self, prompt: str) -> str:
        resp = self._ds.chat(prompt)
        return resp.get("text", "(empty)")
