# Stage 3 Migration Guide

## Overview
This guide documents the changes made in Stage 3: HeavenLawEngine MVP.

## New Components

### 1. World Laws System
**Location:** `src/world/laws.py`

The system loads world laws from `data/world_laws.json`:
```python
@dataclass
class WorldLaw:
    code: str
    name: str = ""
    description: str = ""
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)
```

### 2. Heaven Law Engine
**Location:** `src/xwe/core/heaven_law_engine.py`

Core enforcement engine that:
- Checks actions against active world laws
- Triggers divine punishment for violations
- Manages thunder tribulation events

### 3. Event System
New events added:
- `ThunderTribulation` - Divine lightning punishment
- `ForbiddenArtBacklash` - Backlash from using forbidden techniques
- `BreakthroughTribulation` - Required tribulation for realm advancement

## World Laws Configuration

### Available Laws
1. **CROSS_REALM_KILL** - Prevents high-realm cultivators from killing low-realm ones
   - `max_gap`: Maximum allowed realm difference (default: 2)
   - `severity_threshold`: Gap for severe punishment (default: 3)

2. **FORBIDDEN_ARTS** - Punishes use of forbidden techniques
   - `backlash_multiplier`: Damage multiplier for backlash
   - `karma_penalty`: Karma points deducted

3. **REALM_BREAKTHROUGH** - Requires tribulation for major realm breakthroughs
   - `major_realms`: List of realms requiring tribulation
   - `tribulation_difficulty`: Difficulty map by realm

4. **KARMA_BALANCE** - Tracks good/evil actions (disabled by default)

## Integration Points

### Combat System
The `CombatSystem.attack()` method now:
1. Creates an `ActionContext`
2. Calls `HeavenLawEngine.enforce()` before damage calculation
3. Cancels the attack if laws are violated
4. Processes any triggered events (e.g., ThunderTribulation)

### Game Core
`GameCore` initialization:
```python
# Initialize heaven law engine
self.heaven_law_engine = HeavenLawEngine()

# Pass to combat system
self.combat_system = CombatSystem(
    self.skill_system, 
    self.parser, 
    self.heaven_law_engine
)
```

## Realm System

Realm hierarchy (index order):
1. 凡人 (0)
2. 炼气期 (1)
3. 筑基期 (2)
4. 金丹期 (3)
5. 元婴期 (4)
6. 化神期 (5)
7. 合体期 (6)
8. 大乘期 (7)
9. 渡劫期 (8)

## Thunder Tribulation Severity

- **minor**: 100 damage
- **moderate**: 500 damage
- **severe**: 9999 damage
- **fatal**: 99999 damage

All tribulations add "scorched" status effect and ensure minimum 1 HP remaining.

## Testing
Run the unit tests:
```bash
pytest tests/test_heaven_law_engine.py -v
```

## Migration Checklist
- [ ] Ensure `data/world_laws.json` exists with proper configuration
- [ ] Update any custom combat implementations to handle `ActionContext`
- [ ] Add realm_name attribute to all Character instances
- [ ] Test cross-realm combat scenarios
- [ ] Verify thunder tribulation damage and effects

## Known Limitations
- Laws only apply to the `attack()` method currently
- Skill-based attacks not yet integrated with law system
- No visual effects for thunder tribulation in UI
- Karma system not fully implemented

## Future Enhancements
- Extend to skill system
- Add visual/audio effects for tribulations
- Implement full karma tracking
- Add more configurable world laws
- Create law exemptions for special items/techniques
