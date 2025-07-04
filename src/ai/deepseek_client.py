"""DeepSeek AI client integration for Xianxia World Engine."""

import json
import logging
import os
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """Client for interacting with DeepSeek AI models."""
    
    # Context-rich prompt template for game understanding
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
        """Initialize DeepSeek client.
        
        Args:
            api_key: API key for DeepSeek service
            model: Model name to use (default: deepseek-chat)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate client configuration."""
        if not self.api_key:
            logger.warning("DeepSeek API key not configured")
    
    def parse(self, utterance: str, ctx: Any) -> Dict[str, Any]:
        """Parse user utterance with game context.
        
        Args:
            utterance: User input text
            ctx: Game context object containing player, scene, laws, etc.
            
        Returns:
            Dict with intent, slots, allowed, and reason
        """
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
            utterance=utterance[:200]  # Limit length
        )
        
        if os.getenv("DEEPSEEK_VERBOSE") == "1":
            logger.debug(f"DeepSeek prompt:\n{prompt}")
        
        try:
            # Call DeepSeek API
            response = self._call_openai(prompt)
            
            # Parse response
            content = response["choices"][0]["message"]["content"]
            result = json.loads(content)
            
            if os.getenv("DEEPSEEK_VERBOSE") == "1":
                logger.debug(f"DeepSeek response: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"DeepSeek parse error: {e}")
            # Return a safe default
            return {
                "intent": "unknown",
                "slots": {},
                "allowed": True,
                "reason": ""
            }
    
    def _summarize_laws(self, laws: List[Any]) -> str:
        """Summarize active world laws."""
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
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI-compatible API.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            API response dict
        """
        if not self.api_key:
            raise ValueError("API key not configured")
        
        # In production, this would make an actual API call
        # For now, return a mock response
        import requests
        
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
            "max_tokens": 200
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API call failed: {e}")
            # Return mock response for testing
            return {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "intent": "unknown",
                            "slots": {},
                            "allowed": True,
                            "reason": ""
                        })
                    }
                }]
            }
    
    def chat(self, prompt: str) -> Dict[str, str]:
        """Send chat request to DeepSeek model.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Dict containing the response text
        """
        try:
            response = self._call_openai(prompt)
            return {"text": response["choices"][0]["message"]["content"]}
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"text": ""}
    
    async def chat_async(self, prompt: str) -> Dict[str, str]:
        """Async version of chat method.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Dict containing the response text
        """
        # TODO: Implement async API call
        return self.chat(prompt)
