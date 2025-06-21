import os
from deepseek import DeepSeek


class LLMClient:
    def __init__(self, model_name: str = "deepseek-chat"):
        self._ds = DeepSeek(api_key=os.environ["DEEPSEEK_API_KEY"], model=model_name)

    def chat(self, prompt: str) -> str:
        return self._ds.chat(prompt).get("text", "")
