# 项目结构概览

本节描述代码迁移至 `src/` 目录后的整体结构。

```
xianxia-world-engine/
├── run.py              # 入口脚本
├── src/                # 所有源代码
│   └── xwe/            # 游戏引擎核心模块
├── tests/              # 单元测试
└── docs/               # 文档
```

源代码均位于 `src` 下，引用时需使用 `src.xwe` 前缀。
