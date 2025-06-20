# 修仙世界引擎 - 实现指南

本指南补充说明重构数据的使用细节。

## 模板文件规范

位于 `xwe/data/restructured/` 的统一模板文件需在 `meta` 区块包含 `schema_version` 字段，当前为 `2020-12`，用于表明所遵循的 JSON Schema 版本。
