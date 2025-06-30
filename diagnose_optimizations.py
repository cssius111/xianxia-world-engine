#!/usr/bin/env python3
"""
快速诊断优化模块的导入问题
"""

import sys
import traceback

def diagnose():
    print("🔍 诊断优化模块导入问题...")
    print("=" * 60)
    
    # 1. 检查 config
    print("\n1. 检查 config.game_config...")
    try:
        from config.game_config import config
        print("✓ config.game_config 导入成功")
        print(f"  - smart_cache_ttl: {getattr(config, 'smart_cache_ttl', 'NOT FOUND')}")
        print(f"  - smart_cache_size: {getattr(config, 'smart_cache_size', 'NOT FOUND')}")
    except Exception as e:
        print(f"✗ config.game_config 导入失败: {e}")
        traceback.print_exc()
    
    # 2. 尝试直接导入 smart_cache
    print("\n2. 检查 smart_cache 模块...")
    try:
        from xwe.core.optimizations.smart_cache import SmartCache, CacheableFunction
        print("✓ smart_cache 导入成功")
        # 测试创建实例
        cache = SmartCache()
        print("✓ SmartCache 实例创建成功")
    except Exception as e:
        print(f"✗ smart_cache 导入失败: {e}")
        traceback.print_exc()
    
    # 3. 尝试直接导入 expression_jit
    print("\n3. 检查 expression_jit 模块...")
    try:
        from xwe.core.optimizations.expression_jit import ExpressionJITCompiler, ExpressionBenchmark
        print("✓ expression_jit 导入成功")
        # 测试创建实例
        compiler = ExpressionJITCompiler()
        print("✓ ExpressionJITCompiler 实例创建成功")
    except Exception as e:
        print(f"✗ expression_jit 导入失败: {e}")
        traceback.print_exc()
    
    # 4. 检查 __init__.py
    print("\n4. 检查 optimizations.__init__.py...")
    try:
        import xwe.core.optimizations
        print("✓ xwe.core.optimizations 导入成功")
        print(f"  - SmartCache: {xwe.core.optimizations.SmartCache}")
        print(f"  - ExpressionJITCompiler: {xwe.core.optimizations.ExpressionJITCompiler}")
    except Exception as e:
        print(f"✗ xwe.core.optimizations 导入失败: {e}")
        traceback.print_exc()
    
    # 5. 测试测试代码的导入方式
    print("\n5. 测试 test_optimizations.py 的导入方式...")
    try:
        import importlib.util
        from pathlib import Path
        
        def _load_module(path, name):
            spec = importlib.util.spec_from_file_location(name, Path(path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        
        optimizations = _load_module('xwe/core/optimizations/__init__.py', 'optimizations')
        print("✓ 模块加载成功")
        print(f"  - SmartCache: {optimizations.SmartCache}")
        print(f"  - ExpressionJITCompiler: {optimizations.ExpressionJITCompiler}")
    except Exception as e:
        print(f"✗ 模块加载失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    diagnose()
