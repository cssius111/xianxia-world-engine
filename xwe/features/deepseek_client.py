import json
import logging
import os
import re
from typing import Any, Dict, Optional

import requests  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """简单封装 DeepSeek 事件生成 API"""

    def __init__(
        self, api_key: Optional[str] = None, api_base: str = "https://api.deepseek.com/v1"
    ) -> None:
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.api_base = api_base.rstrip("/")

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        """尝试从文本中解析 JSON"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"{.*}", text, re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

    def _validate_event(self, event: Dict[str, Any]) -> bool:
        """简单校验事件结构是否符合规范"""
        required = {"id", "name", "description", "type", "category", "effect"}
        if not all(key in event for key in required):
            return False
        effect = event.get("effect")
        if not isinstance(effect, dict) or "type" not in effect:
            return False
        return True

    def generate_event(self, context: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """调用 DeepSeek API 生成事件"""
        if not self.api_key:
            raise RuntimeError("DeepSeek API key not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        prompt = (
            "你是修仙世界的事件生成器，请根据玩家上下文返回一个 JSON 事件，"
            "结构需包含 id、name、description、type、category、effect、conditions、weight、flags。"
        )
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
            ],
            "temperature": 0.7,
            "max_tokens": 400,
        }
        url = f"{self.api_base}/chat/completions"
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=timeout)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            event = self._parse_json(content)
            if not event or not self._validate_event(event):
                raise ValueError("Invalid event format")
            return event
        except Exception as exc:
            logger.error(f"DeepSeek API 调用失败: {exc}")
            raise
