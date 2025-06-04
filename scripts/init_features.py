#!/usr/bin/env python3
"""
初始化所有新功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xwe.features import (
    enhance_player_experience,
    enhance_with_ai_features,
    integrate_community_features,
    integrate_technical_features,
    narrative_system,
    content_ecosystem,
    visual_effects
)

def initialize_all_features(game_core):
    """初始化所有功能增强"""
    print("正在初始化游戏功能增强...")
    
    # 1. 基础玩家体验
    print("  - 初始化智能命令系统...")
    enhance_player_experience(game_core)
    
    # 2. AI个性化
    print("  - 初始化AI个性化系统...")
    enhance_with_ai_features(game_core)
    
    # 3. 社区功能
    print("  - 初始化社区系统...")
    integrate_community_features(game_core)
    
    # 4. 技术运营
    print("  - 初始化技术支持系统...")
    integrate_technical_features(game_core)
    
    # 5. 叙事系统
    print("  - 初始化叙事系统...")
    # 叙事系统通过game_core内部调用
    
    # 6. 内容生态
    print("  - 初始化MOD系统...")
    # MOD系统独立运行
    
    # 7. 视觉增强
    print("  - 初始化视觉效果...")
    # 视觉系统通过输出增强
    
    print("✅ 所有功能初始化完成！")
    
    # 显示功能状态
    print("\n功能状态：")
    print(f"  - MOD加载: {len(content_ecosystem.mod_loader.loaded_mods)} 个MOD")
    print(f"  - 成就系统: {len(narrative_system.achievement_system.achievements)} 个成就")
    print("  - AI个性化: 已启用")
    print("  - 社区功能: 已启用")
    print("  - 自动备份: 已启用")
    print("  - 性能监控: 已启用")

def create_required_directories():
    """创建必要的目录"""
    directories = [
        "saves",
        "saves/backups",
        "logs",
        "logs/crashes",
        "feedback",
        "analytics",
        "mods"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 必要目录已创建")

def check_dependencies():
    """检查依赖"""
    try:
        import psutil
        print("✅ psutil 已安装")
    except ImportError:
        print("❌ 缺少 psutil，请运行: pip install psutil")
        return False
    
    return True

def main():
    """主函数"""
    print("=== 修仙世界引擎 2.0 功能初始化 ===\n")
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装缺失的依赖！")
        return
    
    # 创建目录
    create_required_directories()
    
    # 初始化功能（需要游戏核心实例）
    print("\n功能已准备就绪，在游戏启动时会自动加载。")
    
    # 创建示例MOD
    print("\n创建示例MOD...")
    from xwe.features.content_ecosystem import content_ecosystem
    
    success = content_ecosystem.create_new_mod(
        mod_id="example_mod",
        mod_name="示例MOD",
        author="开发者",
        description="这是一个示例MOD，展示MOD系统的使用方法"
    )
    
    if success:
        print("✅ 示例MOD已创建在 mods/example_mod 目录")
    
    print("\n初始化完成！你可以运行增强版游戏了。")

if __name__ == "__main__":
    main()
