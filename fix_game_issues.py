#!/usr/bin/env python3
"""
修复游戏核心问题并准备新功能
"""

import os
import sys
import shutil
from datetime import datetime

def fix_game_core():
    """修复GameCore主循环问题"""
    print("修复GameCore主循环问题...")
    
    game_core_path = "xwe/core/game_core.py"
    
    # 读取文件
    with open(game_core_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    backup_path = f"{game_core_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(game_core_path, backup_path)
    
    # 修复1: 确保start_new_game设置running状态
    # 在_character_creation_flow前设置running = True
    old_pattern = """        # 设置游戏运行状态（重要！必须在Roll流程前设置）
        logger.info("[GameCore] 游戏已启动，进入运行状态")
        
        # 显示开场"""
    
    new_pattern = """        # 设置游戏运行状态（重要！必须在Roll流程前设置）
        self.running = True
        logger.info("[GameCore] 游戏已启动，进入运行状态")
        
        # 显示开场"""
    
    content = content.replace(old_pattern, new_pattern)
    
    # 修复2: 删除重复的running设置代码（在Roll流程后的）
    duplicate_pattern = """
        # 设置游戏运行状态（修复主循环退出问题）
        self.running = True
        import logging
        logging.info('[GameCore] 游戏已启动，进入运行状态')"""
    
    content = content.replace(duplicate_pattern, "")
    
    # 写回文件
    with open(game_core_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ GameCore修复完成，备份保存到: {backup_path}")

def fix_command_parser():
    """确保CommandType包含所有需要的命令类型"""
    print("修复命令解析器...")
    
    parser_path = "xwe/core/command_parser.py"
    
    # 读取文件
    with open(parser_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有BREAKTHROUGH和CULTIVATE
    if 'BREAKTHROUGH' not in content:
        # 在CommandType枚举中添加缺失的命令
        old_enum = """class CommandType(Enum):
    \"\"\"命令类型枚举\"\"\"
    ATTACK = "attack"
    DEFEND = "defend"
    USE_SKILL = "use_skill"
    FLEE = "flee"
    STATUS = "status"
    INVENTORY = "inventory"
    SKILLS = "skills"
    MAP = "map"
    HELP = "help"
    SAVE = "save"
    QUIT = "quit"
    UNKNOWN = "unknown\""""
        
        new_enum = """class CommandType(Enum):
    \"\"\"命令类型枚举\"\"\"
    ATTACK = "attack"
    DEFEND = "defend"
    USE_SKILL = "use_skill"
    FLEE = "flee"
    STATUS = "status"
    INVENTORY = "inventory"
    SKILLS = "skills"
    MAP = "map"
    HELP = "help"
    SAVE = "save"
    QUIT = "quit"
    CULTIVATE = "cultivate"
    EXPLORE = "explore"
    MOVE = "move"
    TALK = "talk"
    BREAKTHROUGH = "breakthrough"
    UNKNOWN = "unknown\""""
        
        content = content.replace(old_enum, new_enum)
        
        # 写回文件
        with open(parser_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 命令类型添加完成")
    else:
        print("✅ 命令类型已存在，无需修复")

def ensure_data_files():
    """确保所有必要的数据文件存在"""
    print("检查并创建必要的数据文件...")
    
    required_files = {
        "xwe/data/templates/mod_template.json": {
            "mod_info": {
                "name": "示例MOD",
                "version": "1.0.0",
                "author": "作者名",
                "description": "MOD描述"
            },
            "content": {
                "events": [],
                "npcs": [],
                "items": [],
                "skills": []
            }
        }
    }
    
    for filepath, content in required_files.items():
        if not os.path.exists(filepath):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                import json
                json.dump(content, f, ensure_ascii=False, indent=2)
            print(f"✅ 创建文件: {filepath}")

def create_features_directory():
    """创建新功能目录结构"""
    print("创建新功能目录...")
    
    features_dir = "xwe/features"
    if not os.path.exists(features_dir):
        os.makedirs(features_dir)
        
        # 创建__init__.py
        with open(f"{features_dir}/__init__.py", 'w', encoding='utf-8') as f:
            f.write('"""游戏新功能模块"""\n')
        
        print(f"✅ 创建目录: {features_dir}")

def main():
    """主函数"""
    print("=== 修仙世界引擎修复工具 ===\n")
    
    # 检查是否在正确的目录
    if not os.path.exists("xwe"):
        print("错误：请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 执行修复
    try:
        fix_game_core()
        fix_command_parser()
        ensure_data_files()
        create_features_directory()
        
        print("\n✅ 所有修复完成！")
        print("\n下一步：")
        print("1. 运行 python main.py 测试游戏")
        print("2. 运行 python implement_features.py 实现新功能")
        
    except Exception as e:
        print(f"\n❌ 修复过程中出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
