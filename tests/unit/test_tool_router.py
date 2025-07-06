import types
import pytest

from src.xwe.core.nlp import tool_router
from src.xwe.core.nlp.nlp_processor import NLPProcessor, ParsedCommand


def test_dispatch_valid_tool():
    result = tool_router.dispatch("start_cultivation", {"hours": 1})
    assert result["action"] == "start_cultivation"
    assert result["payload"] == {"hours": 1}


def test_dispatch_invalid_tool():
    with pytest.raises(ValueError):
        tool_router.dispatch("invalid_tool", {})


def test_parse_command_triggers_dispatch(monkeypatch):
    processor = NLPProcessor()
    processor.enabled = True
    parsed = ParsedCommand(
        raw="修炼",
        normalized_command="start_cultivation",
        intent="action",
        args={"hours": 2},
        explanation="test",
    )
    monkeypatch.setattr(processor, "processor", types.SimpleNamespace(parse=lambda text: parsed))

    called = {}

    def fake_tool(payload):
        called["payload"] = payload
        return "ok"

    monkeypatch.setitem(tool_router._TOOL_REGISTRY, "start_cultivation", fake_tool)

    processor.parse_command("dummy")
    assert called["payload"] == {"hours": 2}


def test_parse_command_invalid_tool(monkeypatch):
    processor = NLPProcessor()
    processor.enabled = True
    parsed = ParsedCommand(
        raw="无效",
        normalized_command="non_exist",
        intent="action",
        args={},
        explanation="bad",
    )
    monkeypatch.setattr(processor, "processor", types.SimpleNamespace(parse=lambda text: parsed))

    with pytest.raises(ValueError):
        processor.parse_command("dummy")
