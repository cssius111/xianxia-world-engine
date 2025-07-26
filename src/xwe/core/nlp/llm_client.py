"""
DeepSeek API 客户端 - 优化版本
处理与 DeepSeek API 的通信，支持可配置重试和 Mock 模式
"""

import asyncio
import functools
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep, time
from typing import Any, Dict, Optional

try:
    import requests
except ImportError:  # pragma: no cover - 环境缺少 requests 时使用占位对象
    requests = None

# 导入 Prometheus 指标收集器
try:
    from ...metrics.prometheus_metrics import get_metrics_collector
    PROMETHEUS_ENABLED = True
except ImportError:
    PROMETHEUS_ENABLED = False

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
        # 读取 API Key
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
        
        # 初始化线程池执行器（用于异步包装）
        self._executor = ThreadPoolExecutor(
            max_workers=int(os.getenv("LLM_ASYNC_WORKERS", "5")),
            thread_name_prefix="llm_async_"
        )
        self._executor_initialized = True
        logger.info(f"LLMClient 线程池初始化完成，工作线程数: {self._executor._max_workers}")
        
        # Prometheus 指标收集器
        self.metrics_collector = None
        if PROMETHEUS_ENABLED:
            self.metrics_collector = get_metrics_collector()
            self.prometheus_enabled = os.getenv('ENABLE_PROMETHEUS', 'true').lower() == 'true'
            # 更新线程池大小指标
            if self.prometheus_enabled:
                self.metrics_collector.update_async_metrics(
                    thread_pool_size=self._executor._max_workers
                )
        else:
            self.prometheus_enabled = False
    
    def __del__(self):
        """清理资源"""
        self.cleanup()
    
    def cleanup(self):
        """清理线程池资源"""
        if hasattr(self, '_executor_initialized') and self._executor_initialized:
            try:
                self._executor.shutdown(wait=True, cancel_futures=True)
                self._executor_initialized = False
                logger.info("LLMClient 线程池已关闭")
            except Exception as e:
                logger.warning(f"关闭线程池时出错: {e}")

    def _make_request_with_retry(self, payload: Dict) -> Dict:
        """发送请求的包装方法"""
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


    def _make_request(self, payload: Dict) -> Dict:
        """
        发送请求到 DeepSeek API

        Args:
            payload: 请求载荷

        Returns:
            API响应
        """
        if requests is None:
            raise ImportError("The 'requests' package is required for network operations")

        start_time = time()
        try:
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            
            # 记录 API 调用延迟
            if self.prometheus_enabled and self.metrics_collector:
                duration = time() - start_time
                self.metrics_collector.record_api_call(
                    api_name="deepseek",
                    endpoint=self.api_url,
                    duration=duration
                )
            
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

        logger.debug(
            f"Sending request to DeepSeek API: {json.dumps(payload, ensure_ascii=False)[:200]}..."
        )

        try:
            # 发送请求（带重试）
            start_time = time()
            response = self._make_request_with_retry(payload)
            elapsed = time() - start_time

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
    
    async def chat_async(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 256,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        异步发送聊天请求（线程池包装）
        
        Args:
            prompt: 用户提示
            temperature: 温度参数（0-1），0表示更确定的输出
            max_tokens: 最大生成token数
            system_prompt: 系统提示（可选）
            
        Returns:
            模型响应文本
            
        Example:
            ```python
            import asyncio
            
            async def main():
                client = LLMClient()
                response = await client.chat_async("你好")
                print(response)
                
            asyncio.run(main())
            ```
        """
        if not self._executor_initialized:
            raise RuntimeError("LLMClient 线程池已关闭")
        
        loop = asyncio.get_event_loop()

        func = functools.partial(
            self.chat,
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )

        try:
            result = await loop.run_in_executor(self._executor, func)
            return result
        except Exception as e:
            logger.error(f"Async chat error: {e}")
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
    
    async def chat_with_context_async(
        self, messages: list, temperature: float = 0.7, max_tokens: int = 256
    ) -> str:
        """
        异步带上下文的聊天（线程池包装）
        
        Args:
            messages: 消息历史列表，格式为 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大生成token数
            
        Returns:
            模型响应文本
            
        Example:
            ```python
            messages = [
                {"role": "system", "content": "你是一个游戏助手"},
                {"role": "user", "content": "如何提升境界?"},
                {"role": "assistant", "content": "需要不断修炼..."},
                {"role": "user", "content": "具体怎么操作?"}
            ]
            response = await client.chat_with_context_async(messages)
            ```
        """
        if not self._executor_initialized:
            raise RuntimeError("LLMClient 线程池已关闭")
        
        loop = asyncio.get_event_loop()
        
        # 使用 functools.partial 创建带参数的函数
        func = functools.partial(
            self.chat_with_context,
            messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 在线程池中执行
        try:
            result = await loop.run_in_executor(self._executor, func)
            return result
        except Exception as e:
            logger.error(f"Async chat_with_context error: {e}")
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
    
    async def chat_async(self, prompt: str) -> Dict[str, Any]:
        """异步兼容旧接口"""
        try:
            text = await self.client.chat_async(prompt)
            return {"text": text}
        except Exception as e:
            logger.error(f"Error in legacy async chat method: {e}")
            return {"text": ""}
