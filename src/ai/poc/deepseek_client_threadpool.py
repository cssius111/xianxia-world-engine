"""POC: DeepSeek Client with ThreadPoolExecutor implementation."""

import json
import logging
import os
from typing import Dict, Optional, Any, List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests

logger = logging.getLogger(__name__)


class DeepSeekClientThreadPool:
    """DeepSeek client using ThreadPoolExecutor for async operations."""
    
    # Same prompt template as original
    PROMPT_TMPL = """\
你是修仙文字游戏的智能解析器。请根据当前游戏状态分析玩家的意图。

当前场景: {scene}
玩家境界: {player_realm}
目标境界: {target_realm}
激活的世界法则: {laws_summary}

玩家输入: "{utterance}"

请分析玩家意图并以JSON格式回答：
{{
  "intent": "意图类型(attack/move/talk/cultivate/inventory/unknown等)",
  "slots": {{"参数名": "参数值"}},
  "allowed": true/false,
  "reason": "如果不允许，说明原因"
}}

注意：
1. 如果玩家试图跨境界攻击（高境界攻击低境界超过2个大境界），设置allowed=false
2. 如果使用禁术，设置allowed=false
3. reason字段使用中文，符合修仙世界观
"""
    
    # Class-level thread pool (shared across instances)
    _executor: Optional[ThreadPoolExecutor] = None
    _executor_initialized = False
    
    def __init__(self, api_key: str = "", model: str = "deepseek-chat"):
        """Initialize DeepSeek client with thread pool support."""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        # Initialize thread pool if not already done
        self._ensure_executor()
        self._validate_config()
    
    @classmethod
    def _ensure_executor(cls):
        """Ensure thread pool executor is initialized (singleton pattern)."""
        if not cls._executor_initialized:
            max_workers = int(os.getenv("LLM_MAX_WORKERS", "5"))
            cls._executor = ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix="deepseek-"
            )
            cls._executor_initialized = True
            logger.info(f"Initialized ThreadPoolExecutor with {max_workers} workers")
    
    @classmethod
    def get_executor(cls) -> ThreadPoolExecutor:
        """Get the shared thread pool executor."""
        cls._ensure_executor()
        return cls._executor
    
    def _validate_config(self) -> None:
        """Validate client configuration."""
        if not self.api_key:
            logger.warning("DeepSeek API key not configured")
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Sync call to OpenAI-compatible API (used by thread pool)."""
        if not self.api_key:
            raise ValueError("API key not configured")
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful game AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        # Retry logic
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/completions",
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                if e.response.status_code >= 500 and attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
                    
            except Exception as e:
                logger.error(f"API call failed: {e}")
                raise
    
    async def _call_openai_async(self, prompt: str) -> Dict[str, Any]:
        """Async wrapper using thread pool executor."""
        loop = asyncio.get_event_loop()
        executor = self.get_executor()
        
        # Run sync method in thread pool
        result = await loop.run_in_executor(
            executor,
            self._call_openai,
            prompt
        )
        
        return result
    
    async def chat_async(self, prompt: str) -> Dict[str, str]:
        """Async chat request using thread pool."""
        try:
            response = await self._call_openai_async(prompt)
            return {"text": response["choices"][0]["message"]["content"]}
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"text": ""}
    
    def chat(self, prompt: str) -> Dict[str, str]:
        """Sync chat method (original implementation)."""
        try:
            response = self._call_openai(prompt)
            return {"text": response["choices"][0]["message"]["content"]}
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"text": ""}
    
    async def parse_async(self, utterance: str, ctx: Any) -> Dict[str, Any]:
        """Async parse using thread pool."""
        # Extract context information (same as original)
        scene = getattr(ctx, 'scene', '主城')
        player_realm = getattr(ctx.player, 'realm', '炼气期') if hasattr(ctx, 'player') else '炼气期'
        target_realm = getattr(ctx, 'target_realm', '未知')
        
        # Summarize active laws
        laws = getattr(ctx, 'laws', [])
        laws_summary = self._summarize_laws(laws)
        
        # Format prompt
        prompt = self.PROMPT_TMPL.format(
            scene=scene,
            player_realm=player_realm,
            target_realm=target_realm,
            laws_summary=laws_summary,
            utterance=utterance[:200]
        )
        
        if os.getenv("DEEPSEEK_VERBOSE") == "1":
            logger.debug(f"DeepSeek prompt:\n{prompt}")
        
        try:
            # Use thread pool for async execution
            response = await self._call_openai_async(prompt)
            content = response["choices"][0]["message"]["content"]
            result = json.loads(content)
            
            if os.getenv("DEEPSEEK_VERBOSE") == "1":
                logger.debug(f"DeepSeek response: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"DeepSeek parse error: {e}")
            return {
                "intent": "unknown",
                "slots": {},
                "allowed": True,
                "reason": ""
            }
    
    def parse(self, utterance: str, ctx: Any) -> Dict[str, Any]:
        """Sync parse method (original implementation)."""
        # Extract context information
        scene = getattr(ctx, 'scene', '主城')
        player_realm = getattr(ctx.player, 'realm', '炼气期') if hasattr(ctx, 'player') else '炼气期'
        target_realm = getattr(ctx, 'target_realm', '未知')
        
        # Summarize active laws
        laws = getattr(ctx, 'laws', [])
        laws_summary = self._summarize_laws(laws)
        
        # Format prompt
        prompt = self.PROMPT_TMPL.format(
            scene=scene,
            player_realm=player_realm,
            target_realm=target_realm,
            laws_summary=laws_summary,
            utterance=utterance[:200]
        )
        
        if os.getenv("DEEPSEEK_VERBOSE") == "1":
            logger.debug(f"DeepSeek prompt:\n{prompt}")
        
        try:
            response = self._call_openai(prompt)
            content = response["choices"][0]["message"]["content"]
            result = json.loads(content)
            
            if os.getenv("DEEPSEEK_VERBOSE") == "1":
                logger.debug(f"DeepSeek response: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"DeepSeek parse error: {e}")
            return {
                "intent": "unknown",
                "slots": {},
                "allowed": True,
                "reason": ""
            }
    
    def _summarize_laws(self, laws: List[Any]) -> str:
        """Summarize active world laws (same as original)."""
        if not laws:
            return "无特殊限制"
        
        active_laws = []
        for law in laws:
            if hasattr(law, 'enabled') and law.enabled:
                if hasattr(law, 'code'):
                    if law.code == "CROSS_REALM_KILL":
                        active_laws.append("禁止跨境界斩杀")
                    elif law.code == "FORBIDDEN_ARTS":
                        active_laws.append("禁止使用禁术")
                    elif law.code == "REALM_BREAKTHROUGH":
                        active_laws.append("突破需渡劫")
        
        return "；".join(active_laws) if active_laws else "无特殊限制"
    
    @classmethod
    def shutdown_executor(cls):
        """Shutdown the thread pool executor (call on app shutdown)."""
        if cls._executor:
            cls._executor.shutdown(wait=True)
            cls._executor = None
            cls._executor_initialized = False
            logger.info("ThreadPoolExecutor shutdown complete")
    
    def __del__(self):
        """Close session on deletion."""
        if hasattr(self, 'session'):
            self.session.close()


# Alias for drop-in replacement
DeepSeekClient = DeepSeekClientThreadPool
