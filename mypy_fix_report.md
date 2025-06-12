# MyPy 错误修复报告

总错误数：396

## 错误分类统计
- unknown: 30 个

## 详细错误列表

### xwe/core/combat.py
- 行 497: "turn_order: list[<type>] = ...")  [var-annotated]
- 行 501: "combat_log: list[<type>] = ...")  [var-annotated]
- 行 862: "team_alive: dict[<type>, <type>] = ...")  [var-annotated]
- 行 932: "damage_dealt: dict[<type>, <type>] = ...")  [var-annotated]
- 行 933: "healing_done: dict[<type>, <type>] = ...")  [var-annotated]
- 行 934: "distances: dict[<type>, <type>] = ...")  [var-annotated]

### xwe/core/data_manager.py
- 行 204: "issues: dict[<type>, <type>] = ...")  [var-annotated]

### xwe/core/optimizations/async_event_system.py
- 行 16: "handlers: dict[<type>, <type>] = ...")  [var-annotated]
- 行 18: "workers: list[<type>] = ...")  [var-annotated]

### xwe/core/optimizations/expression_jit.py
- 行 223: "results: dict[<type>, <type>] = ...")  [var-annotated]

### xwe/engine/expression/parser.py
- 行 471: "args: list[<type>] = ...")  [var-annotated]

### xwe/features/ai_personalization.py
- 行 492: "int"; expected "str": "str"  [dict-item]
- 行 495: "int"; expected "str": "str"  [dict-item]

### xwe/features/auction_system.py
- 行 505: "output: list[<type>] = ...")  [var-annotated]

### xwe/features/community_system.py
- 行 487: "session_data: dict[<type>, <type>] = ...")  [var-annotated]

### xwe/features/html_output.py
- 行 7: "logs: list[<type>] = ...")  [var-annotated]
- 行 8: "status: dict[<type>, <type>] = ...")  [var-annotated]

### xwe/features/technical_ops.py
- 行 398: "error_counts: dict[<type>, <type>] = ...")  [var-annotated]
- 行 399: "last_errors: list[<type>] = ...")  [var-annotated]
- 行 403: "error_callbacks: list[<type>] = ...")  [var-annotated]

### xwe/services/combat_service.py
- 行 55: "_combat_log: list[<type>] = ...")  [var-annotated]

### xwe/services/game_service.py
- 行 100: "_logs: list[<type>] = ...")  [var-annotated]
- 行 101: "_events: list[<type>] = ...")  [var-annotated]

### xwe/services/world_service.py
- 行 57: "_locations: dict[<type>, <type>] = ...")  [var-annotated]
- 行 58: "_connections: dict[<type>, <type>] = ...")  [var-annotated]
- 行 59: "_discovered_locations: set[<type>] = ...")  [var-annotated]

### xwe/world/world_map.py
- 行 291: "list[str]"; expected "str": "int | str"  [dict-item]
- 行 292: "dict[str, str]"; expected "str": "int | str"  [dict-item]
- 行 293: "list[str]"; expected "str": "int | str"  [dict-item]
- 行 294: "list[dict[str, object]]"; expected "str": "int | str"  [dict-item]