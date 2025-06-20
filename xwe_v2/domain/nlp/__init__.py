from xwe_v2.utils.dotenv_helper import load_dotenv

load_dotenv()
# nlp/__init__.py
"""
自然语言处理模块

提供自然语言理解和命令转换功能。
"""

from xwe_v2.core.nlp.llm_client import LLMClient
from xwe_v2.core.nlp.nlp_processor import NLPConfig, NLPProcessor

__all__ = ["NLPProcessor", "NLPConfig", "LLMClient"]
