#!/usr/bin/env python3
"""Quick test for v2 imports."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Testing v2 imports...")
    from xwe_v2.domain.character.models import Attribute, Character

    print("✅ Import successful!")

    # Create a test character
    char = Character(
        name="测试角色",
        level=1,
        attributes=[Attribute(name="strength", value=10), Attribute(name="agility", value=8)],
    )

    print(f"✅ 角色创建成功: {char.name}")
    print(f"   等级: {char.level}")
    print(f"   属性数量: {len(char.attributes)}")
    print(f"   力量: {char.get_attribute('strength')}")
    print(f"   敏捷: {char.get_attribute('agility')}")
    print(f"   是否存活: {char.is_alive()}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback

    traceback.print_exc()
