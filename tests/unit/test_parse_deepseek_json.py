import pytest
from xwe.core.nlp.nlp_processor import NLPProcessor, NLPConfig


@pytest.fixture
def nlp():
    return NLPProcessor(config=NLPConfig(enable_llm=False))


def test_parse_plain_json(nlp):
    raw = '{"command": "ATTACK", "confidence": 0.8}'
    parsed = nlp._parse_deepseek_json(raw)
    assert parsed == {"command": "ATTACK", "confidence": 0.8}


def test_parse_markdown_json(nlp):
    raw = "```json\n{\"command\": \"STATUS\"}\n```"
    parsed = nlp._parse_deepseek_json(raw)
    assert parsed == {"command": "STATUS"}


def test_parse_json_in_text(nlp):
    raw = "response: {\"command\": \"FLEE\"}" \
          " some trailing text"
    parsed = nlp._parse_deepseek_json(raw)
    assert parsed == {"command": "FLEE"}
