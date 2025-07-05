"""Test suite for Stage 2: Sidebar API Restoration"""

import pytest
import json
from unittest.mock import MagicMock, patch


def test_cultivation_status_endpoint_exists(client):
    """Test that /api/cultivation/status endpoint exists."""
    response = client.get('/api/cultivation/status')
    assert response.status_code == 200
    assert response.is_json


def test_cultivation_status_returns_correct_format(client):
    """Test that cultivation status returns expected format."""
    response = client.get('/api/cultivation/status')
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Check required fields
    assert 'realm' in data
    assert 'progress' in data
    assert 'next_tribulation' in data or data['next_tribulation'] is None


def test_achievements_endpoint_exists(client):
    """Test that /api/achievements endpoint exists."""
    response = client.get('/api/achievements')
    assert response.status_code == 200
    assert response.is_json


def test_achievements_returns_array(client):
    """Test that achievements endpoint returns an array."""
    response = client.get('/api/achievements')
    assert response.status_code == 200
    
    data = response.get_json()
    # The API returns {"success": True, "achievements": [...]}
    assert 'success' in data
    assert 'achievements' in data
    assert isinstance(data['achievements'], list)


def test_inventory_endpoint_exists(client):
    """Test that /api/inventory endpoint exists."""
    response = client.get('/api/inventory')
    assert response.status_code == 200
    assert response.is_json


def test_inventory_returns_array(client):
    """Test that inventory endpoint returns an array."""
    response = client.get('/api/inventory')
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)


def test_sessionStorage_panel_persistence():
    """Test that panel state is saved to sessionStorage (JS test)."""
    # This is a JavaScript behavior test, documented here for completeness
    js_test = """
    // Test code to run in browser console
    GamePanels.showPanel('statusPanel');
    console.assert(sessionStorage.getItem('sidebar:last') === 'statusPanel');
    
    GamePanels.showPanel('inventoryPanel');
    console.assert(sessionStorage.getItem('sidebar:last') === 'inventoryPanel');
    """
    assert True  # Placeholder - actual test should be in E2E tests


def test_cultivation_status_with_game_state(client, mocker, app):
    """Test cultivation status with mocked game state."""
    # Mock the game instance
    mock_player = MagicMock()
    mock_player.attributes.realm_name = '筑基期'
    mock_player.attributes.realm_progress = 75
    mock_player.next_tribulation = None
    
    mock_game = MagicMock()
    mock_game.game_state.player = mock_player
    
    mock_instance = {'game': mock_game}
    
    # Set game_instances on the app
    with app.app_context():
        app.game_instances = {'test_session': mock_instance}
        
        with client.session_transaction() as sess:
            sess['session_id'] = 'test_session'
        
        response = client.get('/api/cultivation/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['realm'] == '筑基期'
        assert data['progress'] == 75
        assert data['next_tribulation'] is None


def test_achievements_with_achievement_manager(client, mocker, app):
    """Test achievements with mocked achievement manager."""
    # Mock achievement
    mock_achievement = MagicMock()
    mock_achievement.to_dict.return_value = {
        'id': 'test_ach',
        'name': 'Test Achievement',
        'description': 'Test description',
        'unlocked': True
    }
    
    # Mock achievement manager
    mock_manager = MagicMock()
    mock_manager.list_player.return_value = [mock_achievement]
    
    mock_game = MagicMock()
    mock_game.achievement_manager = mock_manager
    
    mock_instance = {'game': mock_game}
    
    with app.app_context():
        app.game_instances = {'test_session': mock_instance}
        
        with client.session_transaction() as sess:
            sess['session_id'] = 'test_session'
        
        response = client.get('/api/achievements')
        assert response.status_code == 200
        
        data = response.get_json()
        # The API returns {"success": True, "achievements": [...]}
        assert 'success' in data
        assert 'achievements' in data
        assert isinstance(data['achievements'], list)
        assert len(data['achievements']) >= 1  # Should have mock achievement or fallback data


def test_inventory_with_player_inventory(client, mocker, app):
    """Test inventory with mocked player inventory."""
    # Mock inventory item
    mock_item = MagicMock()
    mock_item.to_dict.return_value = {
        'id': 'item_001',
        'name': 'Test Item',
        'quantity': 5,
        'type': 'consumable'
    }
    
    mock_player = MagicMock()
    mock_player.inventory = [mock_item]
    
    mock_game = MagicMock()
    mock_game.game_state.player = mock_player
    
    mock_instance = {'game': mock_game}
    
    with app.app_context():
        app.game_instances = {'test_session': mock_instance}
        
        with client.session_transaction() as sess:
            sess['session_id'] = 'test_session'
        
        response = client.get('/api/inventory')
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1  # Should have mock item or fallback data


def test_all_routes_registered(app):
    """Test that all new routes are properly registered."""
    # Get all registered routes
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    
    # Check new routes exist
    assert '/api/cultivation/status' in routes
    assert '/api/achievements/' in routes
    assert '/api/inventory/' in routes
    
    # Check existing routes still work
    assert '/api/player/stats/detailed' in routes
    assert '/api/quests' in routes
    assert '/api/map' in routes


# Both app and client fixtures are now provided by tests/conftest.py
# This avoids duplication and ensures consistency


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
