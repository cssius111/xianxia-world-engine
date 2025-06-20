# XWE V1 to V2 Migration Guide

## 📋 Overview

This guide helps you migrate your Xianxia World Engine project from the traditional `xwe/` structure to the new clean architecture `xwe_v2/` structure.

## 🏗️ Architecture Differences

### V1 Structure (Traditional)
```
xwe/
├── core/              # Core game logic
├── data/              # JSON data files
├── features/          # Feature modules
├── npc/               # NPC system
├── services/          # Service layer
└── world/             # World system
```

### V2 Structure (Clean Architecture)
```
xwe_v2/
├── domain/            # Business logic (no dependencies)
├── application/       # Use cases and orchestration
├── infrastructure/    # External concerns
├── presentation/      # User interfaces
└── plugins/           # Optional features
```

## 🔄 Migration Steps

### Step 1: Preparation

1. **Backup your project**
   ```bash
   cp -r xianxia_world_engine xianxia_world_engine_backup
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Archive old files** (optional)
   ```bash
   python scripts/archive_legacy.py --dry-run
   python scripts/archive_legacy.py
   ```

### Step 2: Run Migration Analysis

First, preview what will be migrated:

```bash
python scripts/migrate_to_v2.py --dry-run
```

This will:
- Analyze all Python files in `xwe/`
- Show import mappings
- Generate a preview report
- NOT modify any files

### Step 3: Selective Migration

You can migrate specific modules:

```bash
# Migrate only character-related code
python scripts/migrate_to_v2.py --include core.character --dry-run

# Migrate everything except features
python scripts/migrate_to_v2.py --exclude features --dry-run

# Migrate only data files
python scripts/migrate_to_v2.py --data-only

# Migrate only code files
python scripts/migrate_to_v2.py --code-only
```

### Step 4: Perform Migration

Once satisfied with the preview:

```bash
python scripts/migrate_to_v2.py
```

### Step 5: Enable V2 Features

Update your `.env` file:

```env
# Enable v2 globally
XWE_USE_V2=true

# Or enable specific features
XWE_V2_IMPORTS=true
XWE_V2_DOMAIN_MODELS=true
XWE_V2_SERVICES=false  # Enable gradually
```

### Step 6: Update Imports

The migration script automatically updates most imports, but you may need to manually update some:

#### Before (V1):
```python
from xwe.core.character import Character
from xwe.core.attributes import CharacterAttributes
from xwe.services.game_service import GameService
```

#### After (V2):
```python
from xwe_v2.domain.character.models import Character
from xwe_v2.domain.character.attributes import CharacterAttributes
from xwe_v2.application.services.game_service import GameService
```

## 📦 Module Mapping Reference

| V1 Module | V2 Module | Notes |
|-----------|-----------|-------|
| `xwe.core.character` | `xwe_v2.domain.character.models` | Domain model |
| `xwe.core.combat` | `xwe_v2.domain.combat.models` | Combat entities |
| `xwe.core.game_core` | `xwe_v2.application.services.game_service` | Application service |
| `xwe.core.command_processor` | `xwe_v2.application.commands` | CQRS pattern |
| `xwe.services.*` | `xwe_v2.infrastructure.services.*` | Infrastructure layer |
| `xwe.features.*` | `xwe_v2.plugins.*` | Plugin system |

## 🔧 Manual Migration Tasks

Some aspects require manual intervention:

### 1. Update Data Models

V2 uses different data structures. Update your character models:

```python
# V1 Style
character = Character(
    name="张三",
    attributes={"strength": 10, "agility": 8}
)

# V2 Style
character = Character(
    name="张三",
    level=1,
    attributes=[
        Attribute(name="strength", value=10),
        Attribute(name="agility", value=8)
    ]
)
```

### 2. Update Service Interfaces

V2 uses dependency injection and interfaces:

```python
# V1 Style
from xwe.services.game_service import GameService
game = GameService()

# V2 Style
from xwe_v2.application.interfaces import IGameService
from xwe_v2.infrastructure.services.game_service import GameService

game: IGameService = GameService()
```

### 3. Update Event Handling

V2 uses a more structured event system:

```python
# V1 Style
event_system.trigger("player_level_up", player)

# V2 Style
from xwe_v2.domain.events import PlayerLevelUpEvent
event_bus.publish(PlayerLevelUpEvent(player_id=player.id, new_level=2))
```

## 🧪 Testing After Migration

1. **Run V2 tests**
   ```bash
   pytest tests/v2/ -v
   ```

2. **Check type safety**
   ```bash
   mypy xwe_v2/ --strict
   ```

3. **Test imports**
   ```python
   # test_imports.py
   from xwe_v2.domain.character.models import Character
   from xwe_v2.application.services.game_service import GameService

   print("✅ Imports working!")
   ```

## ⚠️ Common Issues and Solutions

### Issue 1: Import Errors
```
ImportError: cannot import name 'Character' from 'xwe.core.character'
```
**Solution**: Update import to use v2 path or enable compatibility mode.

### Issue 2: Attribute Errors
```
AttributeError: 'Character' object has no attribute 'attributes'
```
**Solution**: V2 uses a list of Attribute objects instead of a dict.

### Issue 3: Missing Modules
```
ModuleNotFoundError: No module named 'xwe_v2.domain.special_feature'
```
**Solution**: Some features may not have direct v2 equivalents. Check the plugin system.

## 📊 Migration Checklist

- [ ] Backup project
- [ ] Run migration preview
- [ ] Review migration report
- [ ] Perform actual migration
- [ ] Update .env configuration
- [ ] Fix manual migration tasks
- [ ] Run tests
- [ ] Update documentation
- [ ] Test game functionality

## 🔄 Rollback Plan

If you need to rollback:

1. Disable v2 in `.env`:
   ```env
   XWE_USE_V2=false
   ```

2. Restore from backup:
   ```bash
   rm -rf xwe_v2/
   cp -r xianxia_world_engine_backup/* .
   ```

## 📚 Additional Resources

- [Clean Architecture Principles](docs/architecture/clean_architecture.md)
- [V2 API Documentation](docs/api/v2/)
- [Plugin Development Guide](docs/plugins/guide.md)

## 🤝 Getting Help

If you encounter issues:

1. Check the migration report in `migration_reports/`
2. Review error logs in `logs/migration/`
3. Open an issue with:
   - Error message
   - Migration report
   - Steps to reproduce

---

Remember: Migration is a gradual process. You can run both v1 and v2 side-by-side during the transition!
