### Recommended Improvements

1. **Centralize logging with rotation**
   - Add `xwe/utils/log.py` for configuring `RotatingFileHandler` with gzip.
   - Update `run.py` to call `create_app()` from new `xwe/server/app_factory.py` which uses the logging utility.

2. **Configurable caching**
   - Extend `config/game_config.py` with `data_cache_ttl`, `smart_cache_ttl`, and `smart_cache_size`.
   - Update `DataLoader` and `SmartCache` to honor TTL and capacity from config.

3. **GameStateManager**
   - Implement `xwe/core/state/game_state_manager.py` to manage `GameState` and record transitions.

4. **Async exploration API**
   - Add `ExplorationSystem.explore_async` using `asyncio.to_thread` for non-blocking calls.

5. **Unit tests**
   - Cover new caching TTL logic, state manager logging, and async exploration.
- [x] Centralize logging with rotation
- [x] Configurable caching
- [x] GameStateManager
- [x] Async exploration API
- [x] Unit tests
