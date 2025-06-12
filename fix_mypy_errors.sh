#!/bin/bash
# 快速开始修复 MyPy 错误的脚本

echo "=== xianxia_world_engine MyPy 错误修复工具 ==="
echo

# 检查环境
echo "1. 检查环境..."
if ! command -v mypy &> /dev/null; then
    echo "错误: 未安装 mypy"
    echo "请运行: pip install mypy"
    exit 1
fi

# 创建备份
echo "2. 创建代码备份..."
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
cp -r xwe "$backup_dir"
echo "备份已创建: $backup_dir"

# 第一阶段：添加基础类型注解
echo
echo "3. 第一阶段：修复简单的类型错误"
echo "   - 添加函数返回值 -> None"
echo "   - 修复字典类型注解"

# 修复 return None 类型
find xwe -name "*.py" -type f | while read file; do
    # 查找没有返回值注解的函数
    if grep -E "^[[:space:]]*def .+\(.*\):[[:space:]]*$" "$file" > /dev/null; then
        echo "处理: $file"
        # 添加 -> None 到没有返回值的函数
        sed -i.bak -E 's/^([[:space:]]*)def ([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\):[[:space:]]*$/\1def \2(\3) -> None:/' "$file"
    fi
done

# 修复空字典初始化
echo
echo "4. 修复字典类型注解..."
find xwe -name "*.py" -type f | while read file; do
    if grep -E "^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*=[[:space:]]*\{\}" "$file" > /dev/null; then
        echo "处理字典注解: $file"
        # 首先确保有必要的导入
        if ! grep -q "from typing import" "$file"; then
            sed -i.bak '1i\from typing import Dict, Any' "$file"
        fi
        # 添加字典类型注解
        sed -i.bak -E 's/^([[:space:]]*)([a-zA-Z_][a-zA-Z0-9_]*)[[:space:]]*=[[:space:]]*\{\}/\1\2: Dict[str, Any] = {}/' "$file"
    fi
done

# 运行 mypy 查看进度
echo
echo "5. 运行 mypy 检查当前状态..."
mypy xwe --config-file mypy.ini 2>&1 | tee mypy_errors_phase1.log
error_count=$(grep -c "error:" mypy_errors_phase1.log || echo "0")
echo "当前错误数: $error_count"

# 第二阶段：处理 Optional 类型
echo
echo "6. 第二阶段：处理 Optional 类型错误"
echo "   提示：需要手动检查以下文件中的 Optional 访问："

# 列出有 union-attr 错误的文件
grep "union-attr" mypy_errors_phase1.log | cut -d: -f1 | sort | uniq | while read file; do
    echo "   - $file"
done

# 生成修复建议
echo
echo "7. 生成详细的修复建议..."
cat > fix_suggestions.md << 'EOF'
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
EOF

echo "修复建议已保存到: fix_suggestions.md"

# 统计信息
echo
echo "=== 修复统计 ==="
echo "原始错误数: 416"
echo "当前错误数: $error_count"
echo "修复进度: $((100 - error_count * 100 / 416))%"

echo
echo "=== 下一步 ==="
echo "1. 查看 fix_suggestions.md 了解如何修复剩余错误"
echo "2. 使用 'mypy xwe/path/to/file.py' 检查单个文件"
echo "3. 修复后运行 'mypy xwe --config-file mypy.ini' 验证"
echo "4. 如需恢复，使用备份: $backup_dir"
