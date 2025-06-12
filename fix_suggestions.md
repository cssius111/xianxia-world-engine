# MyPy 错误修复建议

## 剩余错误类型和修复方法

### 1. Optional 类型处理 (union-attr)
```python
# 错误示例
player: Optional[Player] = get_player()
player.name  # 错误!

# 修复方法 1: 添加 None 检查
if player is not None:
    player.name

# 修复方法 2: 使用断言（确定不为 None）
assert player is not None
player.name

# 修复方法 3: 使用默认值
name = player.name if player else "Unknown"
```

### 2. 抽象类实例化 (abstract)
```python
# 错误示例
service = IGameService()  # 错误!

# 修复方法
service = GameServiceImpl()  # 使用具体实现类
```

### 3. 类型不匹配 (arg-type, assignment)
```python
# 错误示例
def process(value: int) -> None:
    pass

process("string")  # 错误!

# 修复方法
process(int("string"))  # 类型转换
# 或修改函数签名
def process(value: Union[int, str]) -> None:
    pass
```

### 4. 属性未定义 (attr-defined)
```python
# 检查拼写错误
# 检查属性是否真的存在
# 考虑使用 hasattr() 检查
```

## 下一步操作

1. 手动检查 `fix_suggestions.md` 中的建议
2. 逐个文件修复剩余错误
3. 使用 `mypy xwe --config-file mypy.ini` 验证修复
4. 提交代码前运行完整测试

## 有用的命令

```bash
# 只检查特定文件
mypy xwe/core/game_core.py

# 显示错误代码
mypy xwe --show-error-codes

# 生成类型存根
stubgen -p xwe

# 忽略特定错误（临时）
# type: ignore[error-code]
```
