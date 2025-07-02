import pytest


@pytest.mark.parametrize(
    "endpoint,key",
    [
        ("/api/cultivation/status", "data"),
        ("/api/achievements", "achievements"),
        ("/api/map", "data"),
        ("/api/quests", "quests"),
        ("/api/intel", "data"),
        ("/api/player/stats/detailed", "data"),
    ],
)
def test_get_endpoints(client, endpoint, key):
    resp = client.get(endpoint)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("success") is True
    assert key in data


def test_cultivation_start(client):
    resp = client.post("/api/cultivation/start", json={"hours": 2})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("success") is True
    assert "result" in data
