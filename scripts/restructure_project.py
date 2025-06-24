#!/usr/bin/env python3
"""
项目重构脚本 - 用于重组仙侠世界引擎项目的目录结构
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
import hashlib

class ProjectRestructurer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.new_structure = {
            "data/game_configs": {
                "description": "统一的游戏配置文件目录",
                "subdirs": {
                    "character": "角色相关配置",
                    "combat": "战斗系统配置",
                    "cultivation": "修炼系统配置", 
                    "items": "物品系统配置",
                    "skills": "技能系统配置",
                    "world": "世界设定配置",
                    "npc": "NPC相关配置",
                    "ui": "界面配置"
                }
            },
            "data/game_data": {
                "description": "游戏运行时数据",
                "subdirs": {
                    "templates": "各类模板文件",
                    "formulas": "计算公式配置",
                    "events": "事件配置"
                }
            },
            "data/deprecated": {
                "description": "废弃但暂时保留的文件",
                "subdirs": {}
            }
        }
        self.file_mapping = {}
        self.merge_candidates = []
        
    def analyze_current_structure(self):
        """分析当前的目录结构"""
        print("📊 分析当前项目结构...\n")
        
        # 统计各类JSON文件
        json_stats = {
            "total": 0,
            "by_directory": {},
            "by_category": {}
        }
        
        for root, dirs, files in os.walk(self.project_root):
            if '.git' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.json'):
                    json_stats["total"] += 1
                    rel_path = Path(root).relative_to(self.project_root)
                    
                    # 按目录统计
                    dir_key = str(rel_path)
                    if dir_key not in json_stats["by_directory"]:
                        json_stats["by_directory"][dir_key] = []
                    json_stats["by_directory"][dir_key].append(file)
                    
                    # 按类别统计
                    category = self._categorize_file(file)
                    if category not in json_stats["by_category"]:
                        json_stats["by_category"][category] = []
                    json_stats["by_category"][category].append(f"{rel_path}/{file}")
        
        # 打印统计信息
        print(f"📁 总JSON文件数: {json_stats['total']}\n")
        
        print("📂 按目录分布:")
        for dir_path, files in sorted(json_stats["by_directory"].items()):
            if files:  # 只显示包含JSON文件的目录
                print(f"  {dir_path}: {len(files)} 个文件")
        
        print("\n📋 按类别分布:")
        for category, files in sorted(json_stats["by_category"].items()):
            print(f"  {category}: {len(files)} 个文件")
        
        return json_stats
    
    def _categorize_file(self, filename: str) -> str:
        """根据文件名对文件进行分类"""
        filename_lower = filename.lower()
        
        # 定义分类规则
        categories = {
            "character": ["character", "npc", "player", "role", "destiny", "panel"],
            "combat": ["combat", "battle", "fight", "attack", "defense", "damage"],
            "cultivation": ["cultivation", "realm", "spiritual", "breakthrough", "level"],
            "items": ["item", "equipment", "weapon", "armor", "consumable", "treasure"],
            "skills": ["skill", "ability", "spell", "technique", "talent", "formation"],
            "world": ["world", "area", "location", "region", "timeline", "laws"],
            "system": ["system", "config", "setting", "integration"],
            "ui": ["ui", "interface", "display", "visual", "html"],
            "data": ["data", "template", "model", "schema"],
            "events": ["event", "interaction", "dialogue", "news"],
            "economy": ["auction", "market", "trade", "economy"],
            "ai": ["ai", "llm", "nlp", "intelligence"]
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    return category
        
        return "other"
    
    def create_file_mapping(self):
        """创建文件映射计划"""
        print("\n🗺️  创建文件映射计划...\n")
        
        # 收集所有JSON文件
        for root, dirs, files in os.walk(self.project_root):
            if '.git' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.json'):
                    source_path = Path(root) / file
                    rel_path = source_path.relative_to(self.project_root)
                    
                    # 确定目标位置
                    category = self._categorize_file(file)
                    
                    # 特殊处理某些文件
                    if self._should_deprecate(file, str(rel_path)):
                        target_dir = "data/deprecated"
                    elif category in ["character", "combat", "cultivation", "items", "skills", "world", "npc"]:
                        target_dir = f"data/game_configs/{category}"
                    elif category in ["events", "data"]:
                        target_dir = "data/game_data/templates"
                    else:
                        target_dir = "data/game_configs/system"
                    
                    target_path = self.project_root / target_dir / file
                    
                    self.file_mapping[str(source_path)] = {
                        "source": str(source_path),
                        "target": str(target_path),
                        "category": category,
                        "action": "move"
                    }
        
        # 识别需要合并的文件
        self._identify_merge_candidates()
        
        return self.file_mapping
    
    def _should_deprecate(self, filename: str, filepath: str) -> bool:
        """判断文件是否应该被标记为废弃"""
        # 空文件
        try:
            file_size = os.path.getsize(self.project_root / filepath)
            if file_size < 5:  # 小于5字节，基本是空文件
                return True
        except:
            pass
        
        # 测试文件
        if 'test' in filename.lower() or 'tmp' in filename.lower():
            return True
        
        # 旧版本文件
        if '_old' in filename or '_backup' in filename:
            return True

        return False
    
    def _identify_merge_candidates(self):
        """识别需要合并的文件"""
        print("🔍 识别需要合并的文件...\n")
        
        # 按基础文件名分组
        file_groups = {}
        for mapping in self.file_mapping.values():
            source_path = Path(mapping["source"])
            base_name = source_path.stem.replace('_v2', '').replace('_enhanced', '').replace('_optimized', '')
            
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(mapping["source"])
        
        # 找出有多个版本的文件
        for base_name, files in file_groups.items():
            if len(files) > 1:
                # 分析这些文件是否应该合并
                similar_files = []
                for file_path in files:
                    if not self._should_deprecate(Path(file_path).name, file_path):
                        similar_files.append(file_path)
                
                if len(similar_files) > 1:
                    self.merge_candidates.append({
                        "base_name": base_name,
                        "files": similar_files,
                        "suggested_name": f"{base_name}.json"
                    })
    
    def generate_restructure_plan(self) -> Dict:
        """生成重构计划"""
        print("\n📝 生成重构计划...\n")
        
        plan = {
            "create_directories": list(self.new_structure.keys()),
            "file_moves": [],
            "file_merges": [],
            "deprecated_files": [],
            "summary": {
                "total_files": len(self.file_mapping),
                "files_to_move": 0,
                "files_to_merge": 0,
                "files_to_deprecate": 0
            }
        }
        
        # 整理文件移动计划
        for source, mapping in self.file_mapping.items():
            if "deprecated" in mapping["target"]:
                plan["deprecated_files"].append(mapping)
                plan["summary"]["files_to_deprecate"] += 1
            else:
                plan["file_moves"].append(mapping)
                plan["summary"]["files_to_move"] += 1
        
        # 整理文件合并计划
        for merge_group in self.merge_candidates:
            plan["file_merges"].append({
                "files": merge_group["files"],
                "target": f"data/game_configs/{self._categorize_file(merge_group['suggested_name'])}/{merge_group['suggested_name']}",
                "strategy": "manual_review"  # 需要人工审查
            })
            plan["summary"]["files_to_merge"] += len(merge_group["files"])
        
        return plan
    
    def execute_restructure(self, plan: Dict, dry_run: bool = True):
        """执行重构计划"""
        if dry_run:
            print("\n🔍 试运行模式 - 不会实际移动文件\n")
        else:
            print("\n🚀 执行重构计划...\n")
            
            # 创建备份
            backup_dir = self.project_root / f"backup_restructure_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(exist_ok=True)
            print(f"💾 创建备份目录: {backup_dir}\n")
        
        # 1. 创建新目录结构
        print("📁 创建新目录结构...")
        for dir_path, info in self.new_structure.items():
            full_path = self.project_root / dir_path
            if dry_run:
                print(f"  [DRY RUN] 将创建: {dir_path}")
                for subdir, desc in info["subdirs"].items():
                    print(f"    └── {subdir} ({desc})")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                for subdir in info["subdirs"]:
                    (full_path / subdir).mkdir(exist_ok=True)
                print(f"  ✅ 已创建: {dir_path}")
        
        # 2. 移动文件
        print("\n📦 移动文件...")
        moved_count = 0
        for move_info in plan["file_moves"][:10]:  # 显示前10个
            source = Path(move_info["source"])
            target = Path(move_info["target"])
            
            if dry_run:
                print(f"  [DRY RUN] {source.relative_to(self.project_root)} → {target.relative_to(self.project_root)}")
            else:
                try:
                    # 备份原文件
                    backup_path = backup_dir / source.relative_to(self.project_root)
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, backup_path)
                    
                    # 移动文件
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(target))
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ 错误移动 {source}: {e}")
        
        if len(plan["file_moves"]) > 10:
            print(f"  ... 还有 {len(plan['file_moves']) - 10} 个文件")
        
        if not dry_run:
            print(f"\n✅ 成功移动 {moved_count} 个文件")
        
        # 3. 显示合并建议
        if plan["file_merges"]:
            print("\n🔀 文件合并建议:")
            for merge_info in plan["file_merges"]:
                print(f"\n  目标文件: {merge_info['target']}")
                print(f"  需要合并的文件:")
                for file in merge_info["files"]:
                    print(f"    - {Path(file).relative_to(self.project_root)}")
                print(f"  建议: {merge_info['strategy']}")
        
        # 4. 生成重构报告
        self._generate_restructure_report(plan, dry_run)
    
    def _generate_restructure_report(self, plan: Dict, dry_run: bool):
        """生成重构报告"""
        report_name = f"restructure_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        if dry_run:
            report_name = f"dry_run_{report_name}"
        
        report_path = self.project_root / report_name
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 项目重构报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"模式: {'试运行' if dry_run else '实际执行'}\n\n")
            
            f.write("## 重构摘要\n\n")
            f.write(f"- 总文件数: {plan['summary']['total_files']}\n")
            f.write(f"- 移动文件: {plan['summary']['files_to_move']}\n")
            f.write(f"- 需要合并: {plan['summary']['files_to_merge']}\n")
            f.write(f"- 标记废弃: {plan['summary']['files_to_deprecate']}\n\n")
            
            f.write("## 新目录结构\n\n")
            f.write("```\n")
            f.write("data/\n")
            f.write("├── game_configs/      # 游戏配置文件\n")
            f.write("│   ├── character/     # 角色相关\n")
            f.write("│   ├── combat/        # 战斗系统\n")
            f.write("│   ├── cultivation/   # 修炼系统\n")
            f.write("│   ├── items/         # 物品系统\n")
            f.write("│   ├── skills/        # 技能系统\n")
            f.write("│   ├── world/         # 世界设定\n")
            f.write("│   ├── npc/           # NPC配置\n")
            f.write("│   └── system/        # 系统配置\n")
            f.write("├── game_data/         # 游戏数据\n")
            f.write("│   ├── templates/     # 模板文件\n")
            f.write("│   ├── formulas/      # 公式配置\n")
            f.write("│   └── events/        # 事件配置\n")
            f.write("└── deprecated/        # 废弃文件\n")
            f.write("```\n\n")
            
            if plan["file_merges"]:
                f.write("## 需要手动处理的文件合并\n\n")
                for i, merge in enumerate(plan["file_merges"], 1):
                    f.write(f"### {i}. {Path(merge['target']).name}\n\n")
                    f.write("需要合并以下文件:\n")
                    for file in merge["files"]:
                        f.write(f"- `{Path(file).relative_to(self.project_root)}`\n")
                    f.write("\n建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。\n\n")
            
            f.write("## 后续步骤\n\n")
            f.write("1. **审查文件合并建议**：手动检查需要合并的文件，确保不丢失重要配置\n")
            f.write("2. **更新代码引用**：搜索并更新所有引用旧文件路径的代码\n")
            f.write("3. **清理空目录**：删除移动文件后留下的空目录\n")
            f.write("4. **建立规范**：制定文件命名和组织规范，避免未来出现类似问题\n")
            f.write("5. **版本控制**：将这次重构作为一个重要的提交节点\n\n")
            
            f.write("## 代码更新检查清单\n\n")
            f.write("需要检查和更新的可能位置:\n")
            f.write("- [ ] `core/data_loader.py` - 数据加载路径\n")
            f.write("- [ ] `xwe/core/data_loader.py` - XWE数据加载器\n")
            f.write("- [ ] 各个Service类中的配置文件路径\n")
            f.write("- [ ] 测试文件中的数据路径引用\n")
            f.write("- [ ] 启动脚本中的配置加载\n")
        
        print(f"\n📄 重构报告已保存至: {report_path}")
    
    def generate_path_update_script(self):
        """生成路径更新脚本"""
        print("\n🔧 生成路径更新脚本...")
        
        script_path = self.project_root / "update_paths.py"
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write('''#!/usr/bin/env python3
"""
自动更新代码中的文件路径引用
"""

import os
import re
from pathlib import Path

# 路径映射表
PATH_MAPPINGS = {
''')
            
            # 生成路径映射
            for source, mapping in self.file_mapping.items():
                old_path = Path(source).relative_to(self.project_root)
                new_path = Path(mapping["target"]).relative_to(self.project_root)
                f.write(f'    "{old_path}": "{new_path}",\n')
            
            f.write('''
}

def update_file_paths(file_path):
    """更新单个文件中的路径引用"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        for old_path, new_path in PATH_MAPPINGS.items():
            # 匹配各种可能的路径引用格式
            patterns = [
                rf'"{old_path}"',
                rf"'{old_path}'",
                rf'\\("{old_path}"\\)',
                rf"\\('{old_path}'\\)",
                rf'Path\\("{old_path}"\\)',
                rf"Path\\('{old_path}'\\)",
            ]
            
            for pattern in patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, pattern.replace(str(old_path), str(new_path)), content)
                    updated = True
        
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 更新: {file_path}")
            return True
    except Exception as e:
        print(f"❌ 错误处理 {file_path}: {e}")
    
    return False

def main():
    """遍历所有Python文件并更新路径"""
    project_root = Path(__file__).parent
    updated_files = 0
    
    print("🔍 搜索需要更新的文件...")
    
    for root, dirs, files in os.walk(project_root):
        # 跳过某些目录
        if '.git' in root or '__pycache__' in root or 'backup' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if update_file_paths(file_path):
                    updated_files += 1
    
    print(f"\\n✅ 更新完成！共更新 {updated_files} 个文件")

if __name__ == "__main__":
    main()
''')
        
        # 设置脚本为可执行
        os.chmod(script_path, 0o755)
        print(f"✅ 路径更新脚本已生成: {script_path}")


def main():
    """主函数"""
    project_root = "/Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine"
    
    print("=" * 60)
    print("🏗️  仙侠世界引擎项目重构工具")
    print("=" * 60)
    
    restructurer = ProjectRestructurer(project_root)
    
    # 1. 分析当前结构
    stats = restructurer.analyze_current_structure()
    
    # 2. 创建文件映射
    restructurer.create_file_mapping()
    
    # 3. 生成重构计划
    plan = restructurer.generate_restructure_plan()
    
    print("\n" + "=" * 60)
    print("📋 重构计划已生成")
    print("=" * 60)
    
    # 4. 询问执行模式
    print("\n请选择执行模式:")
    print("1. 试运行 (仅显示将要执行的操作，不实际移动文件)")
    print("2. 实际执行 (移动文件并创建备份)")
    print("3. 仅生成路径更新脚本")
    print("4. 退出")
    
    choice = input("\n请输入选择 (1-4): ")
    
    if choice == "1":
        restructurer.execute_restructure(plan, dry_run=True)
    elif choice == "2":
        confirm = input("\n⚠️  确定要执行重构吗？所有文件都会被移动！(yes/no): ")
        if confirm.lower() == "yes":
            restructurer.execute_restructure(plan, dry_run=False)
            restructurer.generate_path_update_script()
        else:
            print("❌ 操作已取消")
    elif choice == "3":
        restructurer.generate_path_update_script()
    else:
        print("👋 退出程序")


if __name__ == "__main__":
    main()
