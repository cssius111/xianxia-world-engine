"""
DeepSeek API 客户端 - 优化版本
处理与 DeepSeek API 的通信，支持可配置重试和 Mock 模式
"""

import functools
import json
import logging
import os
import re
from time import sleep, time
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

# 尝试导入 backoff，如果不存在则使用简单的重试装饰器
try:
    import backoff
    HAS_BACKOFF = True
except ImportError:
    HAS_BACKOFF = False
    logger.warning("backoff 模块未安装，使用简单重试机制")


def simple_retry(max_tries=3, delay=1.0):
    """简单的重试装饰器（当 backoff 不可用时使用）"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_tries - 1:
                        sleep(delay * (attempt + 1))  # 递增延迟
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator


class LLMClient:
    """
    DeepSeek API 客户端 - 优化版本
    
    新增功能：
    - 可配置重试次数 (XWE_MAX_LLM_RETRIES)
    - Mock 模式支持 (USE_MOCK_LLM=true)
    - 改进的错误处理和日志记录
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://api.deepseek.com/v1/chat/completions",
        model_name: str = "deepseek-chat",
        timeout: int = 30,
        debug: bool = False,
    ):
        """
        初始化客户端

        Args:
            api_key: API密钥，如果不提供则从环境变量读取
            api_url: API端点URL
            model_name: 模型名称
            timeout: 请求超时时间（秒）
            debug: 是否启用调试模式
        """
        # 检查是否启用 Mock 模式
        self.use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        
        if self.use_mock:
            logger.info("🎭 LLM Mock 模式已启用，将跳过网络调用")
            self.api_key = "mock_key"
        else:
            self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
            if not self.api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

        self.api_url = api_url
        self.model_name = model_name
        self.timeout = timeout
        self.debug = debug
        
        # 可配置的重试次数
        self.max_retries = int(os.getenv("XWE_MAX_LLM_RETRIES", "3"))

        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _make_request_with_retry(self, payload: Dict) -> Dict:
        """发送请求的包装方法"""
        if self.use_mock:
            return self._mock_response(payload)
        
        if HAS_BACKOFF:
            # 使用 backoff 库的高级重试机制
            @backoff.on_exception(
                backoff.expo,
                (requests.exceptions.RequestException, requests.exceptions.Timeout),
                max_tries=self.max_retries,
                max_time=60,
            )
            def _request():
                return self._make_request(payload)
            return _request()
        else:
            # 使用简单重试机制
            @simple_retry(max_tries=self.max_retries, delay=1.0)
            def _request():
                return self._make_request(payload)
            return _request()

    def _mock_response(self, payload: Dict) -> Dict:
        """Mock 响应生成器"""
        # 从 payload 中提取用户消息
        messages = payload.get("messages", [])
        user_message = ""
        actual_user_input = ""
        
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                # 从 prompt 中提取实际的用户输入
                # 查找最后一个 "输入:" 标记
                last_input_idx = user_message.rfind('输入:')
                if last_input_idx != -1:
                    # 找到后面的引号内容
                    start_quote = user_message.find('"', last_input_idx)
                    if start_quote != -1:
                        end_quote = user_message.find('"', start_quote + 1)
                        if end_quote != -1:
                            actual_user_input = user_message[start_quote + 1:end_quote]
                break
        
        # 如果没有提取到，使用整个用户消息
        if not actual_user_input:
            actual_user_input = user_message
        
        # 简单的本地解析逻辑
        mock_responses = {
            "探索": {
                "normalized_command": "探索",
                "intent": "action",
                "args": {},
                "explanation": "Mock模式：探索命令"
            },
            "修炼": {
                "normalized_command": "修炼",
                "intent": "train",
                "args": {},
                "explanation": "Mock模式：修炼命令"
            },
            "背包": {
                "normalized_command": "打开背包",
                "intent": "check",
                "args": {},
                "explanation": "Mock模式：背包命令"
            },
            "状态": {
                "normalized_command": "查看状态",
                "intent": "check",
                "args": {},
                "explanation": "Mock模式：状态命令"
            }
        }
        
        # 尝试匹配用户输入
        # 先尝试完整匹配
        exact_matches = {
            "探索周围环境": {
                "normalized_command": "探索",
                "intent": "action",
                "args": {},
                "explanation": "Mock模式：探索命令"
            },
            "修炼提升实力": {
                "normalized_command": "修炼",
                "intent": "train",
                "args": {},
                "explanation": "Mock模式：修炼命令"
            },
            "查看当前状态": {
                "normalized_command": "查看状态",
                "intent": "check",
                "args": {},
                "explanation": "Mock模式：状态命令"
            },
            "打开背包看看": {
                "normalized_command": "打开背包",
                "intent": "check",
                "args": {},
                "explanation": "Mock模式：背包命令"
            }
        }
        
        # 先尝试完整匹配
        if actual_user_input in exact_matches:
            response_copy = exact_matches[actual_user_input].copy()
            response_copy["raw"] = actual_user_input
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(response_copy, ensure_ascii=False)
                        }
                    }
                ]
            }
        
        # 如果没有完整匹配，尝试关键词匹配
        for keyword, response in mock_responses.items():
            if keyword in actual_user_input.lower():
                response_copy = response.copy()
                response_copy["raw"] = actual_user_input
                return {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(response_copy, ensure_ascii=False)
                            }
                        }
                    ]
                }
        
        # 默认响应
        default_response = {
            "raw": actual_user_input,
            "normalized_command": "未知",
            "intent": "unknown",
            "args": {},
            "explanation": "Mock模式：未知命令"
        }
        
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(default_response, ensure_ascii=False)
                    }
                }
            ]
        }

    def _make_request(self, payload: Dict) -> Dict:
        """
        发送请求到 DeepSeek API

        Args:
            payload: 请求载荷

        Returns:
            API响应
        """
        try:
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.warning(f"Request to DeepSeek API timed out after {self.timeout}s")
            raise

        except requests.exceptions.RequestException as e:
            logger.warning(f"Request to DeepSeek API failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.warning(f"Response status: {e.response.status_code}")
                logger.warning(f"Response body: {e.response.text}")
            raise

    def chat(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 256,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        发送聊天请求

        Args:
            prompt: 用户提示
            temperature: 温度参数（0-1），0表示更确定的输出
            max_tokens: 最大生成token数
            system_prompt: 系统提示（可选）

        Returns:
            模型响应文本
        """
        messages = []

        # 添加系统提示（如果有）
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 添加用户消息
        messages.append({"role": "user", "content": prompt})

        # 构建请求载荷
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # 记录请求（仅在非 Mock 模式下）
        if not self.use_mock:
            logger.debug(
                f"Sending request to DeepSeek API: {json.dumps(payload, ensure_ascii=False)[:200]}..."
            )

        try:
            # 发送请求（带重试）
            start_time = time()
            response = self._make_request_with_retry(payload)
            elapsed = time() - start_time

            if self.use_mock:
                logger.debug(f"Mock response generated in {elapsed:.2f}s")
            else:
                logger.debug(f"DeepSeek API response received in {elapsed:.2f}s")
            
            if self.debug:
                logger.debug(
                    f"DeepSeek full response: {json.dumps(response, ensure_ascii=False)}"
                )

            # 提取响应文本
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0].get("message", {}).get("content", "")
                return content
            else:
                logger.error(f"Unexpected response format: {response}")
                return ""

        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {e}")
            raise

    def chat_with_context(
        self, messages: list, temperature: float = 0.7, max_tokens: int = 256
    ) -> str:
        """
        带上下文的聊天

        Args:
            messages: 消息历史列表，格式为 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            模型响应文本
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = self._make_request_with_retry(payload)
            if self.debug:
                logger.debug(
                    f"DeepSeek full response: {json.dumps(response, ensure_ascii=False)}"
                )

            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0].get("message", {}).get("content", "")
                return content
            else:
                return ""

        except Exception as e:
            logger.error(f"Error in chat_with_context: {e}")
            raise

    def get_embeddings(self, text: str) -> Optional[list]:
        """
        获取文本嵌入向量（如果API支持）

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        # 注意：DeepSeek API可能不支持嵌入功能
        # 这里只是预留接口
        logger.warning("Embeddings API not implemented for DeepSeek")
        return None


# 保持向后兼容
class DeepSeek:
    """向后兼容的DeepSeek类"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.client = LLMClient(api_key=api_key, model_name=model)

    def chat(self, prompt: str) -> Dict[str, Any]:
        """兼容旧接口"""
        try:
            text = self.client.chat(prompt)
            return {"text": text}
        except Exception as e:
            logger.error(f"Error in legacy chat method: {e}")
            return {"text": ""}
