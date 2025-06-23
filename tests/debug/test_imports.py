#!/usr/bin/env python3
"""
测试脚本1：检查所有导入是否正常
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("🔍 修仙世界引擎 - 导入测试")
print("=" * 60)

# 测试结果记录
test_results = []

def test_import(module_name, import_statement):
    """测试单个导入"""
    print(f"\n测试导入: {module_name}")
    try:
        exec(import_statement)
        print(f"✅ 成功: {module_name}")
        test_results.append((module_name, True, None))
        return True
    except Exception as e:
        print(f"❌ 失败: {module_name}")
        print(f"   错误: {str(e)}")
        test_results.append((module_name, False, str(e)))
        return False

# 测试基础Python模块
print("\n1. 测试基础Python模块:")
test_import("json", "import json")
test_import("logging", "import logging")
test_import("flask", "from flask import Flask")

# 测试项目模块
print("\n2. 测试项目模块:")

# API模块
test_import("api", "from api import register_api")

# 路由模块
test_import("routes.character", "from routes import character")
test_import("routes.intel", "from routes import intel")
test_import("routes.lore", "from routes import lore")

# 核心模块
test_import("xwe.core.cultivation_system", "from xwe.core.cultivation_system import CultivationSystem")
test_import("xwe.core.game_core", "from xwe.core.game_core import create_enhanced_game")
test_import("xwe.core.attributes", "from xwe.core.attributes import CharacterAttributes")
test_import("xwe.core.character", "from xwe.core.character import Character, CharacterType")

# 功能模块
test_import("xwe.features.ai_personalization", "from xwe.features.ai_personalization import AIPersonalization")
test_import("xwe.features.community_system", "from xwe.features.community_system import CommunitySystem")
test_import("xwe.features.narrative_system", "from xwe.features.narrative_system import NarrativeSystem")
test_import("xwe.features.technical_ops", "from xwe.features.technical_ops import TechnicalOps")

# 配置模块
test_import("game_config", "from game_config import config")

# 总结
print("\n" + "=" * 60)
print("📊 测试总结:")
total = len(test_results)
passed = sum(1 for _, success, _ in test_results if success)
failed = total - passed

print(f"总测试数: {total}")
print(f"✅ 通过: {passed}")
print(f"❌ 失败: {failed}")

if failed > 0:
    print("\n失败的模块:")
    for module, success, error in test_results:
        if not success:
            print(f"  - {module}: {error}")

# 保存结果
import json
results_file = PROJECT_ROOT / "tests" / "debug" / "import_test_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump({
        "total": total,
        "passed": passed,
        "failed": failed,
        "details": [
            {"module": m, "success": s, "error": e}
            for m, s, e in test_results
        ]
    }, f, indent=2, ensure_ascii=False)

print(f"\n详细结果已保存到: {results_file}")
print("=" * 60)

# 返回状态码
sys.exit(0 if failed == 0 else 1)
