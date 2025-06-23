import json


def test_get_settings(client):
    resp = client.get('/api/v1/system/settings')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'graphics' in data
    assert 'audio' in data


def test_update_settings(client, tmp_path):
    payload = {'graphics': {'text_speed': 'fast'}}
    resp = client.put('/api/v1/system/settings', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success']


def test_get_logs(client):
    resp = client.get('/api/v1/system/logs')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'logs' in data
    assert isinstance(data['logs'], list)


def test_game_time_no_session(client):
    resp = client.get('/api/v1/game/time')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['time_of_day'] == 'unknown'
