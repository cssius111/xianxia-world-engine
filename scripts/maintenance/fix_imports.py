#!/usr/bin/env python3
"""
修复修仙世界引擎的导入错误
"""

import os
import sys
import subprocess
from pathlib import Path

class ImportFixer:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.fixes_applied = []
        
    def fix_all(self):
        """执行所有修复"""
        print("🔧 开始修复导入错误...")
        print("=" * 60)
        
        # 1. 创建缺失的 __init__.py 文件
        self.ensure_init_files()
        
        # 2. 修复已知的导入问题
        self.fix_known_issues()
        
        # 3. 创建 pytest 配置
        self.create_pytest_config()
        
        # 4. 测试导入
        self.test_imports()
        
        print("\n" + "=" * 60)
        print(f"✅ 修复完成！应用了 {len(self.fixes_applied)} 个修复")
        
        if self.fixes_applied:
            print("\n应用的修复：")
            for fix in self.fixes_applied:
                print(f"  - {fix}")
    
    def ensure_init_files(self):
        """确保所有包目录都有 __init__.py"""
        print("\n📁 检查 __init__.py 文件...")
        
        # 需要检查的目录
        dirs_to_check = [
            "xwe",
            "xwe/core",
            "xwe/core/state",
            "xwe/core/optimizations",
            "xwe/events",
            "xwe/world",
            "xwe/services",
            "xwe/npc",
            "xwe/data",
            "xwe/utils",
            "xwe/systems",
            "xwe/features",
            "xwe/metrics",
            "xwe/engine",
            "xwe/server",
            "api",
            "api/middleware",
            "api/specs",
            "api/utils",
            "api/v1",
            "routes",
            "config",
            "tests",
        ]
        
        for dir_path in dirs_to_check:
            full_path = self.root / dir_path
            if full_path.exists() and full_path.is_dir():
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("# Auto-generated __init__.py\n")
                    self.fixes_applied.append(f"创建 {dir_path}/__init__.py")
                    print(f"  ✓ 创建 {dir_path}/__init__.py")
    
    def fix_known_issues(self):
        """修复已知的导入问题"""
        print("\n🔨 修复已知问题...")
        
        # 1. 确保 initial_fate.py 存在
        initial_fate_path = self.root / "xwe/events/initial_fate.py"
        if not initial_fate_path.exists():
            initial_fate_path.write_text('''def select_initial_fate(player, events=None):
    """选择初始命运节点
    
    Args:
        player: 玩家角色对象
        events: 可选的事件列表
        
    Returns:
        命运节点ID或None
    """
    return None
''')
            self.fixes_applied.append("创建 xwe/events/initial_fate.py")
            print("  ✓ 创建 xwe/events/initial_fate.py")
        
        # 2. 修复循环导入 - 修改 xwe/core/__init__.py
        core_init = self.root / "xwe/core/__init__.py"
        if core_init.exists():
            content = core_init.read_text()
            if "from xwe.core.game_core import GameCore" in content:
                # 使用延迟导入
                new_content = '''# xwe/core/__init__.py
"""核心模块"""

# 延迟导入以避免循环依赖
_game_core = None
_character = None
_cultivation_system = None

def __getattr__(name):
    global _game_core, _character, _cultivation_system
    
    if name == "GameCore":
        if _game_core is None:
            from xwe.core.game_core import GameCore as _GameCore
            _game_core = _GameCore
        return _game_core
    
    elif name == "Character":
        if _character is None:
            from xwe.core.character import Character as _Character
            _character = _Character
        return _character
    
    elif name == "CultivationSystem":
        if _cultivation_system is None:
            from xwe.core.cultivation_system import CultivationSystem as _CultivationSystem
            _cultivation_system = _CultivationSystem
        return _cultivation_system
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["GameCore", "Character", "CultivationSystem"]
'''
                core_init.write_text(new_content)
                self.fixes_applied.append("修复 xwe/core/__init__.py 循环导入")
                print("  ✓ 修复 xwe/core/__init__.py 循环导入")
    
    def create_pytest_config(self):
        """创建 pytest 配置文件"""
        print("\n📝 创建 pytest 配置...")
        
        pytest_ini = self.root / "pytest.ini"
        if not pytest_ini.exists():
            pytest_ini.write_text('''[pytest]
# 测试路径
testpaths = tests

# 排除的目录
norecursedirs = 
    .git 
    __pycache__ 
    *.egg 
    dist 
    build 
    node_modules
    backup_*
    .pytest_cache
    playwright-report
    test-results
    logs
    saves
    venv
    .venv

# Python 文件匹配模式
python_files = test_*.py

# Python 类匹配模式
python_classes = Test*

# Python 函数匹配模式  
python_functions = test_*

# 添加标记
markers =
    slow: 标记为慢速测试
    integration: 集成测试
    unit: 单元测试
    e2e: 端到端测试

# 输出选项
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    
# 忽略的警告
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
''')
            self.fixes_applied.append("创建 pytest.ini")
            print("  ✓ 创建 pytest.ini")
    
    def test_imports(self):
        """测试导入是否成功"""
        print("\n🧪 测试导入...")
        
        # 尝试导入关键模块
        test_modules = [
            "xwe.core.game_core",
            "xwe.core.character", 
            "xwe.events.initial_fate",
            "xwe.services.game_service",
        ]
        
        failed = []
        for module in test_modules:
            try:
                __import__(module)
                print(f"  ✓ {module}")
            except Exception as e:
                print(f"  ✗ {module}: {e}")
                failed.append(module)
        
        if failed:
            print(f"\n⚠️  仍有 {len(failed)} 个模块导入失败")
        else:
            print("\n✅ 所有关键模块导入成功！")
        
        return len(failed) == 0

def main():
    """主函数"""
    # 获取项目根目录
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    # 确认是修仙世界引擎项目
    if not os.path.exists(os.path.join(project_root, "run.py")):
        print("❌ 错误：当前目录不是修仙世界引擎项目")
        print("请在项目根目录运行此脚本")
        return 1
    
    # 执行修复
    fixer = ImportFixer(project_root)
    fixer.fix_all()
    
    # 提示下一步
    print("\n" + "=" * 60)
    print("下一步：")
    print("1. 运行测试验证修复：")
    print("   pytest tests/")
    print("\n2. 启动游戏检查：")
    print("   python run.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
