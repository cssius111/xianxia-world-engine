"""POC: DeepSeek Client with Celery + Redis implementation."""

import json
import logging
import os
from typing import Dict, Optional, Any, List
import asyncio
from celery import Celery
from celery.result import AsyncResult
import requests
import uuid
import time

logger = logging.getLogger(__name__)

# Celery app configuration
celery_app = Celery('xianxia_deepseek')
celery_app.config_from_object({
    'broker_url': os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    'result_backend': os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'UTC',
    'enable_utc': True,
    'task_track_started': True,
    'task_time_limit': 60,  # 60 seconds hard limit
    'task_soft_time_limit': 50,  # 50 seconds soft limit
    'task_acks_late': True,
    'worker_prefetch_multiplier': 1,
})


# Celery tasks
@celery_app.task(bind=True, max_retries=3, default_retry_delay=2)
def deepseek_chat_task(self, prompt: str, api_key: str, model: str, base_url: str):
    """Celery task for DeepSeek API calls."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful game AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return {"text": result["choices"][0]["message"]["content"]}
        
    except requests.exceptions.Timeout as exc:
        logger.warning(f"Task timeout: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code >= 500:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)
        else:
            raise
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=2)
def deepseek_parse_task(self, prompt: str, api_key: str, model: str, base_url: str):
    """Celery task for DeepSeek parse operations."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful game AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)
        
    except Exception as exc:
        logger.error(f"Parse task failed: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


class DeepSeekClientCelery:
    """DeepSeek client using Celery for async task queue."""
    
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
        """Initialize DeepSeek client with Celery support."""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"
        
        # For sync fallback
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate client configuration."""
        if not self.api_key:
            logger.warning("DeepSeek API key not configured")
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Sync call to OpenAI-compatible API (fallback)."""
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
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise
    
    def chat(self, prompt: str) -> Dict[str, str]:
        """Sync chat method (original implementation)."""
        try:
            response = self._call_openai(prompt)
            return {"text": response["choices"][0]["message"]["content"]}
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"text": ""}
    
    async def chat_async(self, prompt: str, wait_for_result: bool = True) -> Dict[str, Any]:
        """Async chat using Celery task queue."""
        # Submit task to Celery
        task = deepseek_chat_task.delay(
            prompt=prompt,
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url
        )
        
        if not wait_for_result:
            # Return task ID immediately for polling
            return {
                "task_id": task.id,
                "status": "pending",
                "message": "Task submitted to queue"
            }
        
        # Wait for result with timeout
        max_wait = 30  # seconds
        poll_interval = 0.5
        elapsed = 0
        
        while elapsed < max_wait:
            if task.ready():
                if task.successful():
                    return task.result
                else:
                    logger.error(f"Task failed: {task.info}")
                    return {"text": ""}
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        # Timeout
        logger.warning(f"Task {task.id} timed out")
        return {"text": "", "error": "Task timeout"}
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a Celery task."""
        task = AsyncResult(task_id, app=celery_app)
        
        if task.pending:
            return {
                "task_id": task_id,
                "status": "pending",
                "progress": 0
            }
        elif task.failed():
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(task.info)
            }
        elif task.successful():
            return {
                "task_id": task_id,
                "status": "completed",
                "result": task.result
            }
        else:
            return {
                "task_id": task_id,
                "status": task.state,
                "info": task.info
            }
    
    async def parse_async(self, utterance: str, ctx: Any, wait_for_result: bool = True) -> Dict[str, Any]:
        """Async parse using Celery task queue."""
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
        
        # Submit task
        task = deepseek_parse_task.delay(
            prompt=prompt,
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url
        )
        
        if not wait_for_result:
            return {
                "task_id": task.id,
                "status": "pending",
                "message": "Parse task submitted"
            }
        
        # Wait for result
        max_wait = 30
        poll_interval = 0.5
        elapsed = 0
        
        while elapsed < max_wait:
            if task.ready():
                if task.successful():
                    return task.result
                else:
                    logger.error(f"Parse task failed: {task.info}")
                    return {
                        "intent": "unknown",
                        "slots": {},
                        "allowed": True,
                        "reason": ""
                    }
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        # Timeout
        return {
            "intent": "unknown",
            "slots": {},
            "allowed": True,
            "reason": "请求超时"
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
        
        try:
            response = self._call_openai(prompt)
            content = response["choices"][0]["message"]["content"]
            result = json.loads(content)
            return result
        except Exception as e:
            logger.error(f"Parse error: {e}")
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


# Worker startup command:
# celery -A src.ai.poc.deepseek_client_celery:celery_app worker --loglevel=info

# Alias for drop-in replacement
DeepSeekClient = DeepSeekClientCelery
