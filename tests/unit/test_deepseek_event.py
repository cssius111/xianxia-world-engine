import json
from unittest.mock import patch, MagicMock

from xwe.core.event_system import EventSystemV3


def _mock_event():
    return {
        "id": "evt_mock",
        "name": "测试事件",
        "description": "这是一条测试事件",
        "type": "random",
        "category": "system",
        "effect": {"type": "stat_delta", "payload": {"luck": 1}},
        "conditions": {},
        "weight": 1,
        "flags": []
    }


@patch("xwe.features.deepseek_client.requests.post")
def test_generate_event_api_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": json.dumps(_mock_event(), ensure_ascii=False)}}]
    }
    mock_post.return_value = mock_resp

    es = EventSystemV3()
    es.deepseek_client.api_key = "test"
    event = es.generate_event({"player": {"name": "tester"}})
    assert event["id"] == "evt_mock"
    mock_post.assert_called_once()


@patch("xwe.features.deepseek_client.requests.post", side_effect=Exception("net"))
def test_generate_event_fallback(mock_post):
    es = EventSystemV3()
    es.deepseek_client.api_key = "test"
    event = es.generate_event({})
    # 当API失败时应返回本地事件
    assert event in es.local_events
    mock_post.assert_called_once()
