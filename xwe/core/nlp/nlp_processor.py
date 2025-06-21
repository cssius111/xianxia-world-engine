from .llm_client import LLMClient


class NLPProcessor:
    def __init__(self):
        self.llm = LLMClient()

    def chat(self, prompt: str) -> str:
        return self.llm.chat(prompt)

    def analyze(self, text: str) -> dict:
        return {
            "summary": self.llm.chat("请帮我总结以下内容:" + text),
            "keywords": [],
            "sentiment": "neutral",
        }
