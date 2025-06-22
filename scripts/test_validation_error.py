#!/usr/bin/env python3
"""
直接测试ValidationError导入问题
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("测试 ValidationError 导入...")
print("=" * 50)

try:
    # 尝试直接导入exceptions模块
    print("1. 导入 exceptions 模块...")
    import xwe.engine.expression.exceptions as exp_exceptions
    print(f"   ✅ 成功! 模块路径: {exp_exceptions.__file__}")
    
    # 检查模块内容
    print("\n2. 检查模块内容...")
    print(f"   模块属性: {dir(exp_exceptions)}")
    
    # 尝试导入ValidationError
    print("\n3. 导入 ValidationError...")
    from xwe.engine.expression.exceptions import ValidationError
    print(f"   ✅ 成功! ValidationError: {ValidationError}")
    
    # 尝试导入整个expression模块
    print("\n4. 导入 expression 模块...")
    import xwe.engine.expression
    print(f"   ✅ 成功!")
    
    print("\n✅ 所有测试通过!")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    
    # 额外的调试信息
    print("\n调试信息:")
    try:
        import xwe.engine.expression
        print(f"expression模块路径: {xwe.engine.expression.__file__}")
    except:
        pass
    
    try:
        import xwe.engine.expression.exceptions
        print(f"exceptions模块路径: {xwe.engine.expression.exceptions.__file__}")
    except:
        pass
