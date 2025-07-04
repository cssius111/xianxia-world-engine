# Stage 1 Migration Guide

## Overview
This guide documents the changes made in Stage 1: Clean Up & Refactor.

## Files Removed
1. **api_fixes.py** - API routes have been migrated to proper route modules
2. **deepseek/__init__.py** - DeepSeek integration moved to `src/ai/deepseek_client.py`

## New File Structure

### API Routes (`src/api/routes/`)
- `cultivation.py` - Cultivation system endpoints
- `achievements.py` - Achievement system endpoints  
- `map.py` - Map and location data endpoints
- `quests.py` - Quest management endpoints
- `player.py` - Player statistics endpoints
- `intel_api.py` - Intelligence/news system endpoints

### AI Integration (`src/ai/`)
- `deepseek_client.py` - DeepSeek AI client implementation
- `__init__.py` - Module initialization

## Code Migration

### Importing DeepSeek
**Before:**
```python
from deepseek import DeepSeek
```

**After:**
```python
from src.ai.deepseek_client import DeepSeekClient
```

### Registering Routes
**Before:**
```python
from api_fixes import register_sidebar_apis
register_sidebar_apis(app)
```

**After:**
```python
from src.api.routes import register_all_routes
register_all_routes(app)
```

## Testing
Run the unit tests to verify the migration:
```bash
pytest tests/test_cleanup_migration.py -v
```

## Rollback
If needed, backup files are available:
- `api_fixes.py.backup`
- `deepseek/__init__.py.backup`

To rollback:
```bash
mv api_fixes.py.backup api_fixes.py
mv deepseek/__init__.py.backup deepseek/__init__.py
# Then revert changes in run.py
```
