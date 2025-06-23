#!/usr/bin/env python3
"""
测试脚本4：数据文件验证
"""

import json
import os
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

print("=" * 60)
print("📊 修仙世界引擎 - 数据文件验证")
print("=" * 60)

test_results = {
    "files": {},
    "validation_errors": defaultdict(list),
    "data_stats": {}
}

# 数据文件列表
data_files = {
    "attribute_model.json": {
        "required_keys": ["basic_attributes", "derived_attributes", "special_attributes"],
        "description": "角色属性模型"
    },
    "cultivation_realm.json": {
        "required_keys": ["realms"],
        "description": "修炼境界系统"
    },
    "skill_library.json": {
        "required_keys": ["skills", "skill_categories"],
        "description": "技能功法库"
    },
    "spiritual_root.json": {
        "required_keys": ["root_types", "root_qualities"],
        "description": "灵根系统"
    },
    "faction_data.json": {
        "required_keys": ["factions"],
        "description": "门派阵营数据"
    },
    "achievement.json": {
        "required_keys": ["achievements", "categories"],
        "description": "成就系统"
    }
}

# 验证每个数据文件
for filename, config in data_files.items():
    print(f"\n检查 {filename} ({config['description']}):")
    file_path = PROJECT_ROOT / "data" / "restructured" / filename
    
    if not file_path.exists():
        print(f"  ❌ 文件不存在")
        test_results["files"][filename] = False
        test_results["validation_errors"][filename].append("文件不存在")
        continue
    
    try:
        # 加载JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  ✅ JSON格式正确")
        test_results["files"][filename] = True
        
        # 检查必需的键
        missing_keys = []
        for key in config["required_keys"]:
            if key not in data:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"  ❌ 缺少必需的键: {', '.join(missing_keys)}")
            test_results["validation_errors"][filename].extend(
                [f"缺少键: {key}" for key in missing_keys]
            )
        else:
            print(f"  ✅ 所有必需的键都存在")
        
        # 收集统计信息
        stats = {}
        
        # 特定文件的验证
        if filename == "attribute_model.json" and "basic_attributes" in data:
            stats["基础属性数"] = len(data.get("basic_attributes", {}))
            stats["衍生属性数"] = len(data.get("derived_attributes", {}))
            
        elif filename == "cultivation_realm.json" and "realms" in data:
            stats["境界数"] = len(data.get("realms", []))
            # 检查每个境界是否有必要字段
            for i, realm in enumerate(data.get("realms", [])):
                if not isinstance(realm, dict):
                    test_results["validation_errors"][filename].append(
                        f"境界 {i} 不是字典类型"
                    )
                elif "name" not in realm:
                    test_results["validation_errors"][filename].append(
                        f"境界 {i} 缺少名称"
                    )
        
        elif filename == "skill_library.json" and "skills" in data:
            skills = data.get("skills", {})
            stats["技能总数"] = len(skills)
            stats["技能类别数"] = len(data.get("skill_categories", {}))
            
            # 验证技能结构
            for skill_id, skill in skills.items():
                if not isinstance(skill, dict):
                    test_results["validation_errors"][filename].append(
                        f"技能 {skill_id} 格式错误"
                    )
                elif "name" not in skill:
                    test_results["validation_errors"][filename].append(
                        f"技能 {skill_id} 缺少名称"
                    )
        
        elif filename == "spiritual_root.json":
            stats["灵根类型数"] = len(data.get("root_types", {}))
            stats["灵根品质数"] = len(data.get("root_qualities", {}))
        
        elif filename == "faction_data.json" and "factions" in data:
            stats["门派数"] = len(data.get("factions", {}))
        
        elif filename == "achievement.json":
            achievements = data.get("achievements", {})
            stats["成就总数"] = len(achievements)
            stats["成就类别数"] = len(data.get("categories", {}))
        
        test_results["data_stats"][filename] = stats
        
        # 显示统计信息
        if stats:
            print("  📈 数据统计:")
            for key, value in stats.items():
                print(f"     - {key}: {value}")
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON解析错误: {e}")
        test_results["files"][filename] = False
        test_results["validation_errors"][filename].append(f"JSON解析错误: {str(e)}")
    except Exception as e:
        print(f"  ❌ 其他错误: {e}")
        test_results["files"][filename] = False
        test_results["validation_errors"][filename].append(f"其他错误: {str(e)}")

# 检查数据文件之间的引用完整性
print("\n" + "=" * 60)
print("🔗 检查数据引用完整性:")

# 这里可以添加交叉引用检查，比如：
# - 技能引用的境界是否存在
# - 成就引用的技能是否存在
# 等等

# 总结
print("\n" + "=" * 60)
print("📊 验证总结:")

total_files = len(data_files)
valid_files = sum(1 for v in test_results["files"].values() if v)
total_errors = sum(len(errors) for errors in test_results["validation_errors"].values())

print(f"数据文件: {valid_files}/{total_files} 有效")
print(f"验证错误: {total_errors} 个")

if total_errors > 0:
    print("\n错误详情:")
    for filename, errors in test_results["validation_errors"].items():
        if errors:
            print(f"\n  {filename}:")
            for error in errors:
                print(f"    - {error}")

# 保存结果
results_file = PROJECT_ROOT / "tests" / "debug" / "data_validation_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(test_results, f, indent=2, ensure_ascii=False)

print(f"\n详细结果已保存到: {results_file}")

# 如果有错误，生成修复建议
if total_errors > 0:
    suggestions_file = PROJECT_ROOT / "tests" / "debug" / "data_fix_suggestions.txt"
    with open(suggestions_file, 'w', encoding='utf-8') as f:
        f.write("数据文件修复建议\n")
        f.write("=" * 60 + "\n\n")
        
        for filename, errors in test_results["validation_errors"].items():
            if errors:
                f.write(f"{filename}:\n")
                for error in errors:
                    f.write(f"  - {error}\n")
                    
                    # 根据错误类型给出建议
                    if "文件不存在" in error:
                        f.write(f"    建议: 创建文件 data/restructured/{filename}\n")
                    elif "缺少键" in error:
                        key = error.split(": ")[1]
                        f.write(f"    建议: 在文件中添加 '{key}' 字段\n")
                    elif "JSON解析错误" in error:
                        f.write(f"    建议: 检查JSON语法，确保格式正确\n")
                f.write("\n")
    
    print(f"\n💡 修复建议已保存到: {suggestions_file}")

print("=" * 60)
