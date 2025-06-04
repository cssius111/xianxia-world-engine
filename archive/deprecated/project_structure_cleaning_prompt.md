
# Claude 项目结构优化 Prompt

你是我的代码管家与架构审查助手，接下来请对本项目进行 **结构优化、内容合并、分类重构**。

🧠 项目核心信息：
- 项目名称：XianXia World Engine（修仙宇宙引擎）
- 结构由多个模块组成：表达式引擎、角色系统、地图系统、AI行为、物品系统、战斗系统等
- 文档存在于多个位置，包括但不限于 `开发总结.md`, `DEVELOPMENT_PROGRESS.md`, `enhanced_npc_*.json`, `*_template.json`, `project_brief/`, `tests/` 等
- 你可以读取项目当前目录下的所有 `.py`, `.json`, `.md` 文件，推断其用途与关联

📌 当前任务目标：

1. **目录结构优化**
   - 分析哪些模块或文件夹职责重叠（如 `npc/`, `enhanced_npc/`）
   - 合并冗余模块（如多个 npc dialogue 或 skills 文件）
   - 推荐合并后的文件夹结构与命名（如 `data/npc/`, `scripts/ai/`）

2. **内容归并**
   - 查找多个命名相似但内容部分重叠的文件（如 `skills.json`, `enhanced_skills.json`）
   - 合并为一个主文件，并标注合并策略（去重？版本保留？结构对齐？）
   - 如果同一系统存在旧/新两套，请统一标准格式，写出清理建议

3. **更新日志生成**
   - 自动记录你分析出的变更记录，格式如下：
     ## 更新日志（自动生成）

     - 🗂️ 合并文件：enhanced_npc_dialogues.json + npc_dialogues.json → xwe/data/npc/dialogues.json
     - 🧹 删除废弃数据：old_ai_behavior.json（已转移至 ai/behavior_tree.json）
     - 🔄 重命名模块：core/skills.py → gameplay/skills_core.py（符合模块语义）
     - 📁 新增分类目录：data/items/, data/skills/

4. **建议后续命名规范与文档布局**
   - 例如建议以 `/docs/` 专门放结构文档，`/data/` 内细分为 `npc/`, `world/`, `skills/` 等子目录
   - 提议将所有阶段任务更新统一放在 `DEVELOPMENT_PROGRESS.md` 中，并引用其他文档

📎 注意事项：
- 你应尽量复用已有内容，避免生成无关内容
- 不要随意删改内容，所有重构建议应带有“合并来源”、“变更说明”、“重命名原因”
- 所有文件变更要有更新日志记录（包括合并、移动、重命名）

🎯 当前阶段目标：
- 清理“开局roll系统”与人物面板相关内容
- 整合分散在多个位置的角色设定（灵根、命格、体质等）至一个清晰结构中
- 确保未来模块扩展容易维护（支持多人物、多开局场景、多样性配置）
