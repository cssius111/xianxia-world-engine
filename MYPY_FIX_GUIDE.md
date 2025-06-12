# MyPy 类型错误修复指南

## 快速开始

1. **运行修复脚本**
   ```bash
   cd /Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine
   python3 fix_mypy_errors.py
   ```

2. **检查修复结果**
   ```bash
   # 查看修改日志
   cat mypy_fixes.log
   
   # 运行 mypy 检查剩余错误
   mypy xwe --config-file mypy.ini
   ```

3. **运行测试确保功能正常**
   ```bash
   pytest
   ```

4. **提交修改**
   ```bash
   git add -A
   git commit -m "[PHASE4-B2] fix: 批量修复 MyPy 类型错误

AI辅助: 90% | 模块: xwe/core, xwe/services, xwe/world

详细说明:
- 修复 Union 类型注解 (str | Path -> Union[str, Path])
- 添加缺失的返回类型注解
- 修复 Optional 类型参数
- 补充 typing 导入

AI协作详情:
- 使用场景: 分析项目类型错误并生成批量修复脚本
- 生成内容: fix_mypy_errors.py 自动修复脚本
- 人工修改: 需要手动处理复杂的泛型类型

测试状态:
- [ ] 单元测试通过
- [ ] mypy 检查通过
- [ ] 手动测试通过"
   ```

## 脚本功能说明

`fix_mypy_errors.py` 会自动修复以下类型错误：

1. **Union 类型语法**
   - `str | Path` → `Union[str, Path]`
   - `str | Path | None` → `Optional[Union[str, Path]]`

2. **缺失的类型参数**
   - `Dict` → `Dict[str, Any]`
   - `List` → `List[Any]`
   - `Set` → `Set[Any]`

3. **Optional 类型**
   - `param: str = None` → `param: Optional[str] = None`

4. **函数返回类型**
   - 自动为没有返回类型的函数添加 `-> None` 或 `-> Any`

5. **自动导入管理**
   - 确保使用的类型都有正确的 import

## 手动处理的情况

以下情况需要手动处理：

1. **复杂的泛型类型**
   ```python
   # 需要手动指定具体类型
   cache: Dict  # 修改为 Dict[str, CacheEntry]
   ```

2. **类型别名**
   ```python
   # 创建类型别名
   NodeDict = Dict[str, Union[ASTNode, List[ASTNode]]]
   ```

3. **回调函数类型**
   ```python
   # 使用 Callable
   from typing import Callable
   handler: Callable[[Event], None]
   ```

4. **协议类型**
   ```python
   # 使用 Protocol
   from typing import Protocol
   
   class Comparable(Protocol):
       def __lt__(self, other: Any) -> bool: ...
   ```

## 常见问题

**Q: 脚本修改后代码格式乱了怎么办？**
A: 运行 `black xwe` 重新格式化代码

**Q: 修复后还有类型错误怎么办？**
A: 查看 `mypy xwe` 的输出，手动修复剩余的复杂类型错误

**Q: 如何撤销修改？**
A: 使用 `git checkout -- .` 撤销所有未提交的修改

---

祝修复顺利！
