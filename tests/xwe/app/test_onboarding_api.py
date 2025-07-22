import json


def test_onboarding_flow(client):
    # Initialize session
    with client.session_transaction() as sess:
        sess["player_id"] = "test_player"

    # Query initial progress
    resp = client.get("/api/onboarding")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["completed_count"] == 0
    assert data["total"] == 5

    # Complete first step
    resp = client.post(
        "/api/onboarding/complete",
        data=json.dumps({"step": "status"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    result = resp.get_json()
    assert result["success"] is True
    assert result["progress"]["completed_count"] == 1
