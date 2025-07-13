# Changelog

## [0.3.4] - 2025-01-13

### Added
- 完整的API文档
- 架构设计文档
- 开发者指南
- CI/CD配置 (GitHub Actions, GitLab CI)
- Docker支持
- 健康检查端点
- 性能监控仪表板
- 缓存机制优化性能

### Fixed
- 修复所有测试失败 (12个)
- 修复性能退化问题
- 修复RateLimiter测试时间期望
- 修复Prometheus指标内部属性访问
- 修复多模块协调测试

### Changed
- 优化测试配置
- 改进错误处理
- 增强日志记录

### Security
- 添加输入验证
- 增强XSS防护



All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2025-01-04
### Changed
- Consolidated DeepSeek API blueprints. `src/api/v1/deepseek.py` was removed and
  all endpoints are now served from `src/api/routes/deepseek_async.py` under
  `/api/llm`.

## [0.3.2] - 2025-01-03

### Added
- **HeavenLawEngine MVP**: Implemented world-level law enforcement system
  - `src/world/laws.py` - WorldLaw dataclass and JSON loader for `world_laws.json`
  - `src/xwe/core/heaven_law_engine.py` - Core engine that enforces divine laws
  - Cross-realm kill prevention (CROSS_REALM_KILL law)
  - ThunderTribulation event system for divine punishment
  - Support for forbidden arts detection and realm breakthrough tribulations
- **Combat System Integration**: CombatSystem now checks laws before damage calculation
  - Pre-action hook in `attack()` method calls `HeavenLawEngine.enforce()`
  - Cancelled actions trigger appropriate divine punishment events

### Changed
- `CombatSystem.__init__` now accepts optional `heaven_law_engine` parameter
- `GameCore` initializes HeavenLawEngine and passes it to CombatSystem
- Combat flow now includes divine law checks before damage application

### Fixed
- High-realm cultivators can no longer freely slaughter low-realm opponents
- Added realm index mapping for proper cultivation level comparisons

## [0.3.1] - 2025-01-03

### Added
- **Sidebar API Restoration**: Implemented missing sidebar panel endpoints
  - `GET /api/cultivation/status` - Returns realm, progress, and tribulation info
  - `GET /api/achievements/` - Lists all player achievements
  - `GET /api/inventory/` - Returns player inventory items
- **Panel State Persistence**: Sidebar panels now remember last opened state using sessionStorage
- **Game State Integration**: API routes can now access game instances via `current_app.game_instances`

### Changed
- Updated `game_panels_enhanced.js` to support both new and legacy API formats
- Achievement blueprint URL prefix changed from `/api` to `/api/achievements/`
- Cultivation status endpoint now returns simplified realm data with backward compatibility

### Fixed
- Sidebar panels not retaining state after page refresh (KNOWN_BUGS #12)
- API endpoints not accessing actual game state data
- Missing inventory API endpoint for sidebar panel

## [0.3.0] - 2025-01-03

### Changed
- **Major Refactoring**: Consolidated API structure
  - Removed `api_fixes.py` - functionality merged into:
    - `/src/api/routes/cultivation.py` (cultivation status endpoints)
    - `/src/api/routes/player.py` (player state endpoints)
    - `/src/api/routes/achievements.py` (achievement system)
    - `/src/api/routes/map.py` (map and location data)
    - `/src/api/routes/quests.py` (quest management)
    - `/src/api/routes/intel_api.py` (intelligence/news system)
  - Deleted empty `deepseek/__init__.py` module
  - Moved DeepSeek integration to `src/ai/deepseek_client.py`

### Added
- Comprehensive route structure under `src/api/routes/`
- Centralized route registration via `register_all_routes()` function
- Improved DeepSeekClient with async support preparation

### Fixed
- Duplicate route definitions causing Flask warnings
- Import cycles between api_fixes and main route modules
- Inconsistent API endpoint naming conventions

### Deprecated
- Direct imports from `api_fixes` module (use `src.api.routes.*` instead)
- `deepseek` package namespace (use `src.ai.deepseek_client` instead)

## [0.2.5] - 2024-12-28

### Added
- Initial game engine implementation
- Basic cultivation system
- Character creation flow
- Web-based UI with sidebar panels

### Fixed
- Various UI responsiveness issues
- Game state persistence problems

## [0.2.0] - 2024-12-15

### Added
- Core game loop
- Basic combat system
- NPC interaction framework

## [0.1.0] - 2024-12-01

### Added
- Initial project structure
- Basic Flask application setup
- Prototype UI design
