import logging
import json
import os
import logging

from src.xwe.core.command_router import CommandRouter
from src.xwe.core.nlp.nlp_processor import DeepSeekNLPProcessor


def test_route_command_logs(caplog):
    router = CommandRouter(use_nlp=False)
    with caplog.at_level(logging.DEBUG, logger="xwe.command_router"):
        cmd, params = router.route_command("移动 北")
    assert cmd == "move"
    messages = [r.getMessage() for r in caplog.records]
    assert any("收到命令文本" in m for m in messages)
    assert any("传统路由选择处理器" in m and "move" in m for m in messages)


def test_nlp_parse_logs(monkeypatch, caplog):
    os.environ["DEEPSEEK_API_KEY"] = "dummy"
    sample_result = {
        "raw": "探索",
        "normalized_command": "explore",
        "intent": "action",
        "args": {},
        "explanation": "test",
        "confidence": 1.0,
    }

    def fake_call(self, prompt):
        return json.dumps(sample_result)

    monkeypatch.setattr(DeepSeekNLPProcessor, "_call_deepseek_api", fake_call)
    monkeypatch.setattr(DeepSeekNLPProcessor, "build_prompt", lambda self, text, context=None: text)

    processor = DeepSeekNLPProcessor(api_key="dummy")
    with caplog.at_level(logging.DEBUG, logger="xwe.nlp"):
        result = processor.parse("探索", use_cache=False)
    assert result.normalized_command == "explore"
    messages = [r.getMessage() for r in caplog.records]
    assert any("Raw user input: 探索" in m for m in messages)
    assert any("Parsed command:" in m for m in messages)
