#!/usr/bin/env python3
"""
快速添加E2E测试路由到run.py的脚本
"""

import re
import sys
from pathlib import Path

def add_e2e_routes_to_run_py():
    """自动添加E2E测试路由到run.py"""
    run_py_path = Path('run.py')
    
    if not run_py_path.exists():
        print("❌ run.py 文件不存在！")
        return False
    
    # 读取文件内容
    content = run_py_path.read_text(encoding='utf-8')
    
    # 检查是否已经添加了E2E路由
    if 'register_e2e_routes' in content:
        print("✅ E2E测试路由已经存在于run.py中")
        return True
    
    # 查找app = create_app()的位置
    pattern = r'(app = create_app\(\))'
    match = re.search(pattern, content)
    
    if not match:
        print("❌ 未找到 'app = create_app()' 语句")
        return False
    
    # 要插入的代码
    e2e_code = '''

# Register E2E test routes in development/test mode
if os.getenv('FLASK_ENV') in ['development', 'testing'] or os.getenv('ENABLE_E2E_API') == 'true':
    try:
        from routes.api_e2e import register_e2e_routes
        register_e2e_routes(app)
        logger.info("E2E test API endpoints enabled")
    except ImportError as e:
        logger.debug(f"E2E test routes not loaded: {e}")
'''
    
    # 在app = create_app()后面插入代码
    insert_pos = match.end()
    new_content = content[:insert_pos] + e2e_code + content[insert_pos:]
    
    # 写回文件
    run_py_path.write_text(new_content, encoding='utf-8')
    print("✅ 成功添加E2E测试路由到run.py")
    return True

if __name__ == '__main__':
    if add_e2e_routes_to_run_py():
        print("\n现在可以运行E2E测试了：")
        print("npx playwright test tests/e2e_full.spec.ts --headed")
    else:
        print("\n请手动添加E2E路由到run.py")
