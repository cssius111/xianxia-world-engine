# 修仙世界引擎 - 精简版

## 核心结构
- /xwe/core - 游戏核心逻辑
- /xwe/models - 数据模型
- /xwe/world - 世界系统  
- /xwe/features - 功能模块
- /xwe_v2 - （已删除）早期 v2 重构目录，内容已合并到 /xwe
- /api - API接口
- /routes - 路由
- /templates - HTML模板
- /static - CSS/JS

## 启动方式
1. 控制台: python main_menu.py
2. Web: python entrypoints/run_web_ui_optimized.py

## 测试
使用 [pytest](https://docs.pytest.org/) 运行单元测试：

```bash
pytest
```
