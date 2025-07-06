import json


def test_events_stream(client):
    response = client.get('/events', buffered=False)
    # Read first chunk from the event stream
    first_chunk = next(response.response)
    assert b'data:' in first_chunk
    data_json = first_chunk.decode().split('data:')[1].strip()
    data = json.loads(data_json)
    assert 'player' in data
    assert 'inventory' in data
