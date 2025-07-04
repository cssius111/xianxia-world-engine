# Stage 2 Migration Guide

## Overview
This guide documents the changes made in Stage 2: Sidebar API Restoration.

## New API Endpoints

### 1. Cultivation Status
**Endpoint:** `GET /api/cultivation/status`

**Response Format:**
```json
{
    "realm": "炼气期",
    "progress": 25,
    "next_tribulation": null
}
```

**Backward Compatibility:**
The endpoint also returns additional fields for compatibility:
- `current_technique`: Current cultivation technique name
- `techniques`: List of available techniques
- `max_hours`: Maximum cultivation hours
- `warning`: Any warnings or tips

### 2. Achievements
**Endpoint:** `GET /api/achievements/`

**Response Format:**
```json
[
    {
        "id": "ach_001",
        "name": "初入仙门",
        "description": "踏上修仙之路",
        "unlocked": true,
        "unlock_time": "2025-06-30 10:00"
    }
]
```

### 3. Inventory
**Endpoint:** `GET /api/inventory/`

**Response Format:**
```json
[
    {
        "id": "item_001",
        "name": "回血丹",
        "quantity": 3,
        "type": "consumable",
        "description": "恢复50点生命值"
    }
]
```

## Frontend Updates

### Session Storage
The sidebar panel system now remembers the last opened panel across page refreshes:
- Panel state is saved to `sessionStorage` with key `sidebar:last`
- On page load, the last opened panel is automatically restored

### Updated JavaScript Functions
1. `GamePanels.showPanel()` - Now saves panel ID to sessionStorage
2. `GamePanels.loadCultivationData()` - Updated to use new API format
3. Added `DOMContentLoaded` event listener to restore panel state

## Code Changes

### Files Modified
1. `src/api/routes/cultivation.py` - Updated to return realm/progress data
2. `src/api/routes/achievements.py` - URL prefix changed to `/api/achievements/`
3. `src/api/routes/inventory.py` - New file for inventory endpoints
4. `src/api/routes/__init__.py` - Added inventory blueprint registration
5. `run.py` - Exposed game_instances to app context
6. `src/web/static/js/game_panels_enhanced.js` - Added sessionStorage support

### API Integration
Routes now access game state through `current_app.game_instances`:
```python
if hasattr(current_app, 'game_instances') and 'session_id' in session:
    session_id = session.get('session_id')
    if session_id in current_app.game_instances:
        game = current_app.game_instances[session_id]['game']
        # Access game state here
```

## Testing
Run the unit tests to verify the new endpoints:
```bash
pytest tests/test_sidebar_api_restoration.py -v
```

## Migration Checklist
- [ ] Update any direct API calls to use new endpoints
- [ ] Test sidebar panel persistence across page reloads
- [ ] Verify all three new endpoints return data
- [ ] Check backward compatibility for existing integrations
- [ ] Update API documentation

## Known Issues
- Achievement manager integration requires game instance to be properly initialized
- Inventory fallback uses InventorySystem when player.inventory is not available
- Session storage may not work in private browsing mode
