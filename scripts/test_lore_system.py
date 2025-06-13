#!/usr/bin/env python
"""
仙侠世界引导系统 - 快速测试脚本
用于测试新手引导流程
"""

import os
import sys
import time
import webbrowser
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查必要的依赖"""
    required_modules = ['flask', 'markdown']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"缺少依赖: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False
    
    return True

def check_files():
    """检查必要的文件是否存在"""
    required_files = [
        'lore/intro.md',
        'routes/lore.py',
        'routes/character.py',
        'templates_enhanced/components/welcome_modal.html',
        'templates_enhanced/components/lore_modal.html',
        'templates_enhanced/components/roll_modal.html',
        'static/js/lore.js'
    ]
    
    missing = []
    for file in required_files:
        if not (project_root / file).exists():
            missing.append(file)
    
    if missing:
        print("缺少以下文件:")
        for file in missing:
            print(f"  - {file}")
        return False
    
    return True

def clear_browser_data():
    """提示用户清除浏览器数据"""
    print("\n=== 测试新玩家流程 ===")
    print("为了完整测试新手引导流程，请按以下步骤操作：")
    print("1. 打开浏览器的开发者工具 (F12)")
    print("2. 进入 Application/存储 标签")
    print("3. 清除 Local Storage 中的 'xianxia_seen_intro' 项")
    print("4. 或使用隐私/无痕模式打开浏览器")
    print("\n按回车键继续...")
    input()

def main():
    """主函数"""
    print("=== 仙侠世界引导系统测试 ===\n")
    
    # 检查依赖
    print("检查依赖...")
    if not check_dependencies():
        return
    
    # 检查文件
    print("检查文件...")
    if not check_files():
        return
    
    print("✓ 所有检查通过\n")
    
    # 提示清除浏览器数据
    clear_browser_data()
    
    # 启动服务器
    print("启动游戏服务器...")
    print("服务器地址: http://localhost:5001")
    print("\n完整的新手引导流程：")
    print("1. 欢迎页面 → 选择'开始新游戏'")
    print("2. 世界观介绍 → 分页阅读或跳过")
    print("3. 角色创建 → 设置姓名、属性、背景")
    print("4. 进入游戏主界面")
    print("\n使用 Ctrl+C 停止服务器")
    
    # 延迟打开浏览器
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5001')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 导入并运行主应用
    try:
        from run_web_ui_optimized import app
        app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
    except Exception as e:
        print(f"\n错误: {e}")
        print("请确保 run_web_ui_optimized.py 文件正确配置")

if __name__ == '__main__':
    main()