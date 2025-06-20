# XWE V2 - Clean Architecture Implementation

## 🏗️ Architecture Overview

XWE V2 follows Clean Architecture principles with clear separation of concerns:

```
xwe_v2/
├── domain/           # Core business logic (no external dependencies)
│   ├── entities/     # Core business objects
│   ├── values/       # Immutable value objects
│   ├── events/       # Domain events
│   └── world/        # World-specific domain logic
│
├── application/      # Use cases and orchestration
│   ├── commands/     # Command handlers (CQRS)
│   ├── queries/      # Query handlers (CQRS)
│   ├── services/     # Application services
│   └── dtos/         # Data transfer objects
│
├── infrastructure/   # External concerns
│   ├── persistence/  # Data access implementations
│   ├── ai/          # AI/LLM integrations
│   ├── cache/       # Caching layer
│   └── events/      # Event bus implementation
│
├── presentation/     # User interfaces
│   ├── cli/         # Command line interface
│   ├── api/         # REST/GraphQL APIs
│   └── web/         # Web frontend
│
└── plugins/         # Optional feature modules
```

## 🎯 Key Principles

1. **Dependency Rule**: Dependencies only point inward. Domain has no dependencies.
2. **Interface Segregation**: Use small, focused interfaces
3. **Dependency Inversion**: Depend on abstractions, not concretions
4. **Single Responsibility**: Each module has one reason to change

## 🔄 Migration Strategy

We're using the Strangler Fig pattern for gradual migration:

### Phase 1: Foundation (Current)
- [x] Create parallel v2 structure
- [x] Set up strict type checking
- [x] Create import adapters
- [x] Archive legacy files
- [ ] Extract first domain model

### Phase 2: Service Layer
- [ ] Port services with clean interfaces
- [ ] Implement repository pattern
- [ ] Create CQRS command bus
- [ ] Build event system

### Phase 3: Data Migration
- [ ] Version all schemas
- [ ] Create migration tools
- [ ] Unify data access
- [ ] Build compatibility layer

### Phase 4: Deprecation
- [ ] Switch all imports to v2
- [ ] Remove legacy code
- [ ] Update documentation
- [ ] Release v2.0

## 🚀 Getting Started

### Enable V2 Mode

```bash
# Enable v2 imports globally
export XWE_USE_V2=true

# Or enable specific features
export XWE_V2_IMPORTS=true
export XWE_V2_DOMAIN_MODELS=true
```

### Run Tests

```bash
# Run v2 tests with strict typing
pytest tests/v2/ --mypy

# Run with coverage
pytest tests/v2/ --cov=xwe_v2 --cov-report=html
```

### Archive Legacy Files

```bash
# Preview what will be archived
python scripts/archive_legacy.py --dry-run

# Actually archive files
python scripts/archive_legacy.py
```

## 📦 Module Structure

### Domain Layer
Pure Python objects with business logic:
```python
# xwe_v2/domain/character.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Character:
    id: str
    name: str
    cultivation_level: int

    def can_breakthrough(self) -> bool:
        """Domain logic for breakthrough eligibility."""
        return self.cultivation_level % 10 == 9
```

### Application Layer
Use cases that orchestrate domain objects:
```python
# xwe_v2/application/commands/breakthrough.py
from xwe_v2.domain.character import Character
from xwe_v2.application.interfaces import ICharacterRepository

class BreakthroughCommand:
    def __init__(self, repo: ICharacterRepository):
        self.repo = repo

    async def execute(self, character_id: str) -> Character:
        character = await self.repo.get(character_id)
        if character.can_breakthrough():
            character.cultivation_level += 1
            await self.repo.save(character)
        return character
```

### Infrastructure Layer
External integrations:
```python
# xwe_v2/infrastructure/persistence/json_character_repo.py
from xwe_v2.application.interfaces import ICharacterRepository
from xwe_v2.domain.character import Character

class JsonCharacterRepository(ICharacterRepository):
    async def get(self, id: str) -> Character:
        # Load from JSON file
        pass

    async def save(self, character: Character) -> None:
        # Save to JSON file
        pass
```

## 🛡️ Type Safety

All v2 code must pass strict mypy checks:

```ini
[mypy]
strict = true
warn_return_any = true
disallow_untyped_defs = true
```

## 📊 Monitoring Migration

Track v1 vs v2 usage:
```python
# Automatic logging when XWE_LOG_V1_USAGE=true
2024-01-15 10:23:45 INFO Redirected import: xwe.core.character -> xwe_v2.domain.character
```

## 🤝 Contributing

1. All new features go in v2
2. Fix bugs in v1 only if critical
3. Write tests for all v2 code
4. Maintain backward compatibility until Phase 4

## 📚 Documentation

- [Architecture Decision Records](docs/architecture/)
- [Migration Guide](docs/MIGRATION_GUIDE_v2.md)
- [API Documentation](docs/api/)
