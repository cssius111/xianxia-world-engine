"""POC: DeepSeek Client with httpx.AsyncClient implementation."""

import json
import logging
import os
from typing import Dict, Optional, Any, List
import httpx
import asyncio

logger = logging.getLogger(__name__)


class DeepSeekClientAsync:
    """DeepSeek client using httpx.AsyncClient for async operations."""
    
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
    
    def __init__(self, api_key: str = "", model: str = "deepseek-chat"):
        """Initialize DeepSeek client with async support."""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"
        
        # Async client configuration
        self.timeout = httpx.Timeout(30.0, connect=5.0)
        self._async_client: Optional[httpx.AsyncClient] = None
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate client configuration."""
        if not self.api_key:
            logger.warning("DeepSeek API key not configured")
    
    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client (singleton pattern)."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10
                ),
                http2=True  # Enable HTTP/2 for better performance
            )
        return self._async_client
    
    async def _call_openai_async(self, prompt: str) -> Dict[str, Any]:
        """Async call to OpenAI-compatible API."""
        if not self.api_key:
            raise ValueError("API key not configured")
        
        client = await self._get_async_client()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful game AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "stream": False  # Disable streaming for now
        }
        
        # Retry logic with exponential backoff
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.TimeoutException as e:
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                if e.response.status_code >= 500 and attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
                    
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Sync wrapper for backward compatibility."""
        # Create new event loop if none exists
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._call_openai_async(prompt))
            return result
        else:
            # If already in async context, create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self._call_openai_async(prompt))
                return future.result()
    
    async def chat_async(self, prompt: str) -> Dict[str, str]:
        """Async chat request to DeepSeek model."""
        try:
            response = await self._call_openai_async(prompt)
            return {"text": response["choices"][0]["message"]["content"]}
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"text": ""}
    
    def chat(self, prompt: str) -> Dict[str, str]:
        """Sync chat method for backward compatibility."""
        try:
            response = self._call_openai(prompt)
            return {"text": response["choices"][0]["message"]["content"]}
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"text": ""}
    
    async def parse_async(self, utterance: str, ctx: Any) -> Dict[str, Any]:
        """Async parse user utterance with game context."""
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
        """Sync parse method for backward compatibility."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.parse_async(utterance, ctx))
            return result
        else:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.parse_async(utterance, ctx))
                return future.result()
    
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
    
    async def close(self):
        """Close async client connections."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
    
    def __del__(self):
        """Cleanup on deletion."""
        if self._async_client:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.close())
            except RuntimeError:
                # No event loop, use sync close
                asyncio.run(self.close())


# Alias for drop-in replacement
DeepSeekClient = DeepSeekClientAsync
