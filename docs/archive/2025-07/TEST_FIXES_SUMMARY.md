# 测试修复总结

## 修复的问题

### 1. test_mock_mode_end_to_end 失败

**问题原因**：在 mock 模式下，`ParsedCommand` 的 `raw` 字段应该保留用户的原始输入，但代码中使用了 API 返回的值。

**修复方案**：
- 文件：`src/xwe/core/nlp/nlp_processor.py`
- 修改：在 `parse` 方法中，将 `raw=result["raw"]` 改为 `raw=user_input`
- 这样确保了 `raw` 字段始终是用户的原始输入，而不是 mock API 返回的值

### 2. test_achievements_with_achievement_manager 失败

**问题原因**：测试代码错误地在返回的列表中查找 'achievements' 键，但实际上 API 返回的是一个包含 'success' 和 'achievements' 键的字典。

**修复方案**：
- 文件：`tests/test_sidebar_api_restoration.py`
- 修改：更新测试断言，先检查 'success' 键，然后检查 'achievements' 键及其类型

## 修改的文件

1. `/src/xwe/core/nlp/nlp_processor.py` - 第 537-538 行
2. `/tests/test_sidebar_api_restoration.py` - 第 136-138 行

## 运行测试

修复后，请运行以下命令重新测试：

```bash
pytest tests/e2e/optimizations/test_optimization_integration.py::TestOptimizationIntegration::test_mock_mode_end_to_end -v
pytest tests/test_sidebar_api_restoration.py::test_achievements_with_achievement_manager -v
```

或运行所有测试：

```bash
pytest tests/ -v
```

## 注意事项

这些修复是实际的代码修复，而不是形式主义的修复。它们解决了根本原因：
- 第一个问题是逻辑错误（使用了错误的数据源）
- 第二个问题是测试期望与实际 API 返回格式不匹配
