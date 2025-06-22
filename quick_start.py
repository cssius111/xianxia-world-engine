#!/usr/bin/env python3
"""
快速启动测试 - 检查项目是否可以运行
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_and_run():
    """测试并运行项目"""
    print("🚀 快速启动测试")
    print("=" * 60)
    
    # 测试关键导入
    print("1️⃣ 测试关键模块导入...")
    
    try:
        # 测试所有关键导入
        from xwe.engine.expression.exceptions import ValidationError
        print("   ✅ ValidationError")
        
        from xwe.features.narrative_system import Achievement, narrative_system
        print("   ✅ Achievement, narrative_system")
        
        from xwe.features.content_ecosystem import content_ecosystem
        print("   ✅ content_ecosystem")
        
        from xwe.metrics import metrics_registry
        print("   ✅ metrics_registry")
        
        print("\n2️⃣ 导入Web应用...")
        from entrypoints.run_web_ui_optimized import app
        print("   ✅ Flask应用导入成功")
        
        print("\n3️⃣ 检查路由...")
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(str(rule))
        print(f"   ✅ 发现 {len(routes)} 个路由")
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("\n启动 Web 服务器...")
        print("服务器地址: http://localhost:5000")
        print("按 Ctrl+C 停止服务器\n")
        
        # 启动应用
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        print("\n请运行以下命令修复:")
        print("1. python cleanup.py")
        print("2. python complete_fix.py")
        
    except Exception as e:
        print(f"\n❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_and_run()
