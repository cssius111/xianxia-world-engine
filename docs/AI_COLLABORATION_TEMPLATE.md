# AI 协作 PR/Commit 模板

## Commit Message 模板

```
[PHASE4-B2] <type>: <description>

AI辅助: <percentage>% | 模块: <modules>

详细说明:
- 主要变更内容
- 影响范围说明
- 相关issue: #xxx

AI协作详情:
- 使用场景: <场景描述>
- 生成内容: <代码/文档/测试>
- 人工修改: <修改说明>

测试状态:
- [ ] 单元测试通过
- [ ] mypy 检查通过
- [ ] 手动测试通过
```

### Type 类型说明
- `feat`: 新功能
- `fix`: 修复bug
- `refactor`: 重构
- `test`: 测试相关
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `perf`: 性能优化
- `chore`: 构建过程或辅助工具的变动

### 示例

```
[PHASE4-B2] fix: 批量修复 MyPy 类型错误

AI辅助: 80% | 模块: xwe/core, xwe/services

详细说明:
- 修复 Union 类型注解 (str | Path -> Union[str, Path])
- 添加缺失的返回类型注解
- 修复 Optional 类型参数
- 补充 typing 导入

AI协作详情:
- 使用场景: 分析项目中的类型错误模式并生成修复脚本
- 生成内容: scripts/fix_mypy_errors.py 自动修复脚本
- 人工修改: 调整了部分复杂类型的推断逻辑

测试状态:
- [x] 单元测试通过
- [x] mypy 检查通过（错误数从120减少到15）
- [x] 手动测试通过

相关issue: #42
```

## PR Description 模板

```markdown
## 🎯 PR 概述
简述本次 PR 的主要目的和变更

## 📝 变更类型
- [ ] ✨ 新功能 (feat)
- [ ] 🐛 Bug修复 (fix)
- [ ] ♻️ 重构 (refactor)
- [ ] ✅ 测试 (test)
- [ ] 📚 文档 (docs)
- [ ] 🎨 代码格式 (style)
- [ ] ⚡ 性能优化 (perf)

## 🤖 AI 协作说明

### 使用的 AI 工具
- [ ] GitHub Copilot
- [ ] Claude
- [ ] ChatGPT
- [ ] 其他: _____

### AI 辅助内容
| 内容类型 | AI生成比例 | 说明 |
|---------|-----------|------|
| 代码实现 | __% | |
| 测试用例 | __% | |
| 文档注释 | __% | |

### AI 协作细节
```
任务描述: [给AI的具体任务]
上下文: [提供的相关代码/需求]
生成结果: [AI生成的主要内容]
人工调整: [对AI结果的修改]
```

## 📋 测试清单
- [ ] 所有测试通过 (`pytest`)
- [ ] 类型检查通过 (`mypy xwe`)
- [ ] 代码格式检查 (`black --check xwe`)
- [ ] 无新增警告
- [ ] 文档已更新

## 🔍 影响分析
**影响模块**: 
- `xwe/core/*`
- `xwe/services/*`

**破坏性变更**: 
- [ ] 是
- [ ] 否

**需要迁移**: 
- [ ] 是
- [ ] 否

## 📸 截图/演示
（如适用）

## 🔗 相关链接
- Issue: #___
- 设计文档: [链接]
- 相关PR: #___

## 📌 部署注意事项
- [ ] 需要环境变量更新
- [ ] 需要数据库迁移
- [ ] 需要配置文件更新

## ✏️ 备注
其他需要说明的内容
```

## AI 协作最佳实践

### 1. 明确任务描述
```
❌ 不好的请求: "帮我写个函数"
✅ 好的请求: "基于现有的 Character 类，创建一个计算角色战斗力的方法，需要考虑等级、装备和技能加成"
```

### 2. 提供充分上下文
```python
# 给 AI 的上下文示例
"""
当前类结构:
class Character:
    attributes: CharacterAttributes
    skills: List[Skill]
    equipment: Dict[str, Item]
    
需求: 添加一个方法计算综合战斗力
公式: 基础属性 * 1.5 + 技能加成 + 装备加成
"""
```

### 3. 验证和调整
- 始终验证 AI 生成的代码
- 检查边界条件
- 确保符合项目规范
- 补充测试用例

### 4. 记录协作过程
在 commit 或 PR 中记录:
- AI 的贡献比例
- 人工修改的部分
- 为什么选择 AI 辅助

## 常用 AI 协作场景模板

### 场景1: 类型注解修复
```
任务: 修复文件 [filename] 的 mypy 类型错误
上下文: [粘贴 mypy 错误输出]
约束: 
- 保持向后兼容
- 使用 Union 而不是 |
- 确保所有函数有返回类型
期望输出: 修复后的代码片段
```

### 场景2: 单元测试生成
```
任务: 为 [class/function] 生成完整的单元测试
上下文: [粘贴类或函数代码]
要求:
- 使用 pytest
- 覆盖正常和异常情况
- 包含参数化测试
- 添加适当的 mock
期望输出: 完整的测试文件
```

### 场景3: 文档生成
```
任务: 为 [module] 生成 API 文档
上下文: [模块的主要功能和接口]
格式要求:
- Google docstring 风格
- 包含示例代码
- 说明参数和返回值
- 列出可能的异常
期望输出: 完整的文档字符串
```

### 场景4: 重构建议
```
任务: 重构 [code section] 以提高可维护性
当前问题: [描述代码味道或问题]
约束:
- 保持接口不变
- 提高可测试性
- 遵循 SOLID 原则
期望输出: 重构方案和代码
```

## Git Hooks 集成

### pre-commit hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# 检查是否有 AI 协作标记
if git diff --cached --name-only | xargs grep -l "AI辅助" > /dev/null 2>&1; then
    echo "检测到 AI 协作内容，请确保："
    echo "1. 已经人工审核所有 AI 生成的代码"
    echo "2. 在 commit message 中说明 AI 协作情况"
    echo "3. 运行了相关测试"
    read -p "是否继续提交？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

### commit-msg hook
```bash
#!/bin/bash
# .git/hooks/commit-msg

# 检查 PHASE4 提交是否包含 AI 协作信息
if grep -q "^\[PHASE4" "$1" && ! grep -q "AI辅助:" "$1"; then
    echo "错误: PHASE4 的提交必须包含 AI 协作信息"
    echo "请在 commit message 中添加: AI辅助: <percentage>%"
    exit 1
fi
```

---

**最后更新**: 2025-06-12
**用途**: 规范 AI 协作开发流程，确保透明度和可追溯性
