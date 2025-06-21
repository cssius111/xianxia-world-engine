def test_system_info(client):
    resp = client.get('/api/v1/system/info')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('version') == '1.0.0'
    assert 'features' in data


def test_game_status_without_session(client):
    resp = client.get('/api/v1/game/status')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('status') == 'idle'
