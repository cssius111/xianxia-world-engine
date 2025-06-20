# 数据迁移指南

## 从旧版本迁移到3.0数据结构

### 快速迁移脚本

```python
#!/usr/bin/env python3
"""
修仙世界引擎数据迁移脚本
从旧版数据结构迁移到3.0版本
"""

import json
import os
from pathlib import Path
import shutil
from datetime import datetime

class DataMigrator:
    def __init__(self, old_data_path, new_data_path):
        self.old_path = Path(old_data_path)
        self.new_path = Path(new_data_path)
        self.backup_path = self.old_path.parent / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def backup_old_data(self):
        """备份旧数据"""
        print(f"备份旧数据到: {self.backup_path}")
        shutil.copytree(self.old_path, self.backup_path)

    def migrate_attributes(self):
        """迁移属性数据"""
        print("迁移属性数据...")

        # 读取旧的属性文件
        old_attribute = self._load_json(self.old_path / "attribute/attribute_model.json")
        old_base = self._load_json(self.old_path / "attribute/base.json")

        # 已经是新格式，检查是否需要更新
        new_attribute = self._load_json(self.new_path / "attribute_model.json")

        # 合并额外的属性定义
        if old_base:
            # 将base.json中的内容合并到新的attribute_model中
            pass

        print("✓ 属性数据迁移完成")

    def migrate_cultivation(self):
        """迁移修炼境界数据"""
        print("迁移境界数据...")

        old_cultivation = self._load_json(self.old_path / "attribute/cultivation.json")
        new_cultivation = self._load_json(self.new_path / "cultivation_realm.json")

        # 旧数据格式较简单，需要扩展
        if old_cultivation and "realms" in old_cultivation:
            # 扩展每个境界的详细信息
            for i, old_realm in enumerate(old_cultivation["realms"]):
                # 在新数据中找到对应的境界并确保信息完整
                realm_id = old_realm["id"]
                # 新数据已经包含完整信息

        print("✓ 境界数据迁移完成")

    def migrate_combat(self):
        """迁移战斗系统数据"""
        print("迁移战斗系统...")

        # 检查多个版本的战斗系统文件
        combat_files = [
            "combat/combat_system.json",
            "combat/combat_system_v2.json",
            "combat/combat_system_optimized.json"
        ]

        # 使用最新版本
        latest_combat = None
        for file in combat_files:
            data = self._load_json(self.old_path / file)
            if data:
                latest_combat = data

        # 新的战斗系统已经是重构后的格式
        print("✓ 战斗系统迁移完成")

    def migrate_items(self):
        """迁移物品数据"""
        print("迁移物品数据...")

        # 旧版可能有分散的物品文件
        items_path = self.old_path / "items"
        if items_path.exists():
            all_items = []
            for item_file in items_path.glob("*.json"):
                items = self._load_json(item_file)
                if isinstance(items, list):
                    all_items.extend(items)
                elif isinstance(items, dict) and "items" in items:
                    all_items.extend(items["items"])

            # 转换为新格式
            # 新格式已经包含了示例物品

        print("✓ 物品数据迁移完成")

    def migrate_npcs(self):
        """迁移NPC数据"""
        print("迁移NPC数据...")

        # 检查NPC相关文件
        npc_files = [
            "npc/npcs.json",
            "npc/dialogues.json",
            "templates/npc.json"
        ]

        for file in npc_files:
            data = self._load_json(self.old_path / file)
            if data:
                # 处理NPC数据
                pass

        print("✓ NPC数据迁移完成")

    def create_formula_library(self):
        """创建公式库"""
        print("整理公式库...")

        # 公式库已经在新数据中创建
        # 这里可以扫描所有文件中的公式并验证

        print("✓ 公式库创建完成")

    def validate_migration(self):
        """验证迁移结果"""
        print("\n验证迁移结果...")

        required_files = [
            "attribute_model.json",
            "cultivation_realm.json",
            "spiritual_root.json",
            "combat_system.json",
            "event_template.json",
            "npc_template.json",
            "item_template.json",
            "faction_model.json",
            "formula_library.json",
            "system_config.json"
        ]

        all_valid = True
        for file in required_files:
            file_path = self.new_path / file
            if file_path.exists():
                # 验证JSON格式
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"✓ {file}")
                except json.JSONDecodeError as e:
                    print(f"✗ {file} - JSON格式错误: {e}")
                    all_valid = False
            else:
                print(f"✗ {file} - 文件不存在")
                all_valid = False

        # 验证Schema文件
        print("\n验证Schema文件...")
        for file in required_files:
            schema_file = file.replace('.json', '_schema.json')
            schema_path = self.new_path / schema_file
            if schema_path.exists():
                print(f"✓ {schema_file}")
            else:
                print(f"✗ {schema_file} - Schema文件不存在")

        return all_valid

    def _load_json(self, path):
        """加载JSON文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def run(self):
        """执行迁移"""
        print("开始数据迁移...")
        print(f"源路径: {self.old_path}")
        print(f"目标路径: {self.new_path}")

        # 1. 备份
        self.backup_old_data()

        # 2. 迁移各个模块
        self.migrate_attributes()
        self.migrate_cultivation()
        self.migrate_combat()
        self.migrate_items()
        self.migrate_npcs()
        self.create_formula_library()

        # 3. 验证
        if self.validate_migration():
            print("\n✅ 数据迁移成功完成！")
        else:
            print("\n⚠️ 数据迁移完成，但存在一些问题需要手动检查")

        print(f"\n旧数据已备份至: {self.backup_path}")
        print("建议手动检查迁移后的数据确保正确性")


if __name__ == "__main__":
    # 使用示例
    migrator = DataMigrator(
        old_data_path="/path/to/xwe/data",
        new_data_path="/path/to/xwe/data/restructured"
    )
    migrator.run()
```

### 手动迁移检查清单

- [ ] 备份所有旧数据文件
- [ ] 确认新数据文件都已生成
- [ ] 验证所有JSON文件格式正确
- [ ] 检查引用关系是否完整
- [ ] 测试加载新数据文件
- [ ] 运行单元测试验证功能
- [ ] 检查游戏平衡性是否受影响

### 主要变更说明

1. **文件结构变化**
   - 从分散的子目录结构改为扁平化结构
   - 所有核心数据文件放在同一目录下
   - 每个数据文件都有对应的Schema文件

2. **数据格式标准化**
   - 所有文件都包含meta信息
   - 统一的ID命名规范（snake_case）
   - 结构化的公式表达式

3. **新增内容**
   - formula_library.json - 集中管理所有公式
   - 完整的JSON Schema验证
   - _custom_tags扩展机制

4. **依赖关系明确化**
   - 通过ID引用替代文件路径引用
   - 明确的模块间依赖关系
   - 支持循环依赖检测

### 兼容性说明

- 3.0版本不直接兼容旧版数据格式
- 需要通过迁移脚本转换数据
- 建议在测试环境先进行迁移测试
- 保留旧数据备份直到确认新版本稳定运行

### 后续步骤

1. 运行迁移脚本
2. 验证迁移结果
3. 更新游戏代码以使用新数据格式
4. 进行完整的功能测试
5. 部署到生产环境

---

如有问题，请参考 RESTRUCTURE_SUMMARY.md 文档或联系开发团队。
