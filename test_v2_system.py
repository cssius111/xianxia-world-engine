#!/usr/bin/env python3
"""
修仙世界引擎 V2 - 完整测试脚本
测试新的引导系统和所有功能
"""

import os
import sys
import time
import webbrowser
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("修仙世界引擎 V2.0 - 完整引导系统")
    print("=" * 60)
    print()

def check_system():
    """系统检查"""
    print("正在进行系统检查...")
    
    # 检查Python版本
    print(f"✓ Python版本: {sys.version.split()[0]}")
    
    # 检查依赖
    required = ['flask', 'markdown']
    for module in required:
        try:
            __import__(module)
            print(f"✓ {module} 已安装")
        except ImportError:
            print(f"✗ {module} 未安装 - 请运行: pip install {module}")
            return False
    
    # 检查关键文件
    key_files = [
        'templates_enhanced/game_main_v2.html',
        'templates_enhanced/components/welcome_modal_v2.html',
        'templates_enhanced/components/sidebar_v2.html',
        'templates_enhanced/components/game_panels.html',
        'templates_enhanced/components/world_intro.html',
        'routes/character.py'
    ]
    
    missing = []
    for file in key_files:
        if not (project_root / file).exists():
            missing.append(file)
    
    if missing:
        print("\n✗ 缺少以下文件:")
        for f in missing:
            print(f"  - {f}")
        return False
    else:
        print("✓ 所有关键文件已就位")
    
    # 检查音频目录
    audio_dir = project_root / 'static' / 'audio'
    if audio_dir.exists():
        mp3_files = list(audio_dir.glob('*.mp3'))
        if mp3_files:
            print(f"✓ 找到 {len(mp3_files)} 个背景音乐文件")
        else:
            print("! 未找到背景音乐文件（可选）")
    
    return True

def show_test_guide():
    """显示测试指南"""
    print("\n" + "=" * 60)
    print("测试指南")
    print("=" * 60)
    
    print("\n1. 新玩家完整流程测试:")
    print("   a) 欢迎页面 → 选择'开始游戏'")
    print("   b) 创建角色（测试所有选项）")
    print("   c) 查看世界介绍")
    print("   d) 进入游戏主界面")
    
    print("\n2. 功能面板测试:")
    print("   - 点击每个功能链接")
    print("   - 测试面板内的交互")
    print("   - 点击外部关闭面板")
    
    print("\n3. 开发者模式测试:")
    print("   - 刷新页面")
    print("   - 选择'开发者模式'")
    print("   - 密码: dev123")
    print("   - 查看控制台输出")
    
    print("\n4. 老玩家流程测试:")
    print("   - 先创建角色并保存")
    print("   - 刷新页面")
    print("   - 选择'继续游戏'")
    
    print("\n5. 命令测试:")
    print("   - 探索")
    print("   - 修炼 1小时")
    print("   - 前往 青云峰")

def main():
    """主函数"""
    print_banner()
    
    # 系统检查
    if not check_system():
        print("\n系统检查失败，请解决上述问题后重试。")
        return
    
    print("\n✓ 系统检查通过！")
    
    # 显示测试指南
    show_test_guide()
    
    print("\n" + "=" * 60)
    print("准备启动游戏服务器...")
    print("=" * 60)
    
    # 提示
    print("\n提示:")
    print("- 服务器地址: http://localhost:5001")
    print("- 使用 Ctrl+C 停止服务器")
    print("- 建议使用Chrome或Firefox浏览器")
    print("- 首次测试建议使用隐私模式")
    
    input("\n按回车键启动服务器...")
    
    # 自动打开浏览器
    def open_browser():
        time.sleep(2)
        print("\n正在打开浏览器...")
        webbrowser.open('http://localhost:5001')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动服务器
    try:
        from run_web_ui_optimized import app
        
        # 设置一些测试配置
        app.config['TESTING'] = True
        app.config['SERVER_START_TIME'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        print("\n服务器启动中...\n")
        app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请检查:")
        print("1. 端口5001是否被占用")
        print("2. run_web_ui_optimized.py 是否正确")
        print("3. 所有依赖是否已安装")

if __name__ == '__main__':
    main()