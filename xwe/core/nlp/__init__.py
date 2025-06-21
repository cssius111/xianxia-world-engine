from xwe.utils.dotenv_helper import load_dotenv
load_dotenv()

from .llm_client import LLMClient


class NLPConfig:
    def __init__(self, model_name: str = "deepseek-chat"):
        self.model_name = model_name

from .nlp_processor import NLPProcessor

__all__ = ["LLMClient", "NLPProcessor", "NLPConfig"]
