#!/usr/bin/env python3
"""
直接测试Web UI启动
"""

import sys
import traceback
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("🚀 尝试启动 Web UI...")
print("=" * 60)

try:
    # 尝试导入并运行
    print("1. 导入Flask应用...")
    from entrypoints.run_web_ui_optimized import app
    print("   ✅ 导入成功!")
    
    print("\n2. 检查路由...")
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append(str(rule))
    print(f"   ✅ 发现 {len(routes)} 个路由")
    
    print("\n3. 启动服务器...")
    print("   服务器将在 http://localhost:5000 启动")
    print("   按 Ctrl+C 停止服务器")
    print("\n" + "=" * 60)
    
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
    
    print("\n💡 调试建议:")
    print("1. 检查所有依赖是否安装: pip install -r requirements.txt")
    print("2. 清理缓存: python scripts/clean_cache.py")
    print("3. 运行诊断: python scripts/full_diagnosis.py")
