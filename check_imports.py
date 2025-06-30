#!/usr/bin/env python3
"""
快速检查所有模块导入是否正常
"""

import sys
import traceback

def test_imports():
    """测试所有关键模块的导入"""
    
    modules_to_test = [
        # 核心模块
        "xwe.core",
        "xwe.core.game_core",
        "xwe.core.character",
        "xwe.core.cultivation_system",
        "xwe.core.command_router",
        "xwe.core.optimizations.smart_cache",
        "xwe.core.state.game_state_manager",
        "xwe.core.output",
        
        # 事件模块
        "xwe.events",
        "xwe.events.initial_fate",
        
        # 服务模块
        "xwe.services.game_service",
        
        # 主程序
        "run",
    ]
    
    print("检查模块导入...")
    print("=" * 60)
    
    failed = []
    
    for module_name in modules_to_test:
        try:
            if module_name == "run":
                # 特殊处理 run.py
                import run
            else:
                __import__(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"✗ {module_name}: {e}")
            failed.append((module_name, str(e)))
        except Exception as e:
            print(f"✗ {module_name}: {type(e).__name__}: {e}")
            failed.append((module_name, f"{type(e).__name__}: {e}"))
    
    print("=" * 60)
    
    if failed:
        print(f"\n失败: {len(failed)} 个模块")
        for module, error in failed:
            print(f"\n{module}:")
            print(f"  {error}")
        return False
    else:
        print("\n✅ 所有模块导入成功！")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
