#!/usr/bin/env python3
"""
完整项目修复脚本 - 解决所有已知问题
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set

# 项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_step(step_num: int, total: int, description: str):
    """打印步骤信息"""
    print(f"\n[{step_num}/{total}] {description}")
    print("=" * 60)


def clean_all_cache():
    """清理所有Python缓存"""
    print("🧹 清理Python缓存...")
    count = 0
    
    for root, dirs, files in os.walk(project_root):
        # 删除 __pycache__ 目录
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                count += 1
            except:
                pass
        
        # 删除 .pyc 文件
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                    count += 1
                except:
                    pass
    
    print(f"✅ 清理了 {count} 个缓存项")
    return True


def check_missing_modules():
    """检查缺失的模块"""
    print("🔍 检查缺失的模块...")
    
    missing_modules = []
    
    # 需要检查的模块路径
    modules_to_check = [
        ("xwe/features/world_building.py", """
\"\"\"
世界构建模块
管理游戏世界的生成和维护
\"\"\"

from typing import Dict, List, Optional, Any
import random


class Region:
    \"\"\"地域\"\"\"
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.locations: List[str] = []
        self.danger_level = 1
        self.resources: List[str] = []


class WorldBuilder:
    \"\"\"世界构建器\"\"\"
    
    def __init__(self):
        self.world_data: Dict[str, Any] = {}
        self.regions: Dict[str, Region] = {}
        self._init_default_world()
    
    def _init_default_world(self):
        \"\"\"初始化默认世界\"\"\"
        # 创建基础地域
        regions = [
            ("青云山脉", "云雾缭绕的山脉，适合修炼"),
            ("落日平原", "广阔的平原，资源丰富"),
            ("幽冥谷", "危险的山谷，妖兽众多"),
            ("东海之滨", "靠近大海，灵气充沛")
        ]
        
        for name, desc in regions:
            region = Region(name, desc)
            region.danger_level = random.randint(1, 5)
            self.regions[name] = region
    
    def generate_world(self):
        \"\"\"生成世界\"\"\"
        self.world_data = {
            "regions": {name: {
                "description": r.description,
                "danger_level": r.danger_level,
                "locations": r.locations
            } for name, r in self.regions.items()},
            "time": "dawn",
            "weather": "clear"
        }
        return self.world_data
    
    def load_world(self, data: Dict[str, Any]):
        \"\"\"加载世界数据\"\"\"
        self.world_data = data
    
    def save_world(self) -> Dict[str, Any]:
        \"\"\"保存世界数据\"\"\"
        return self.world_data
    
    def get_region(self, region_name: str) -> Optional[Region]:
        \"\"\"获取地域\"\"\"
        return self.regions.get(region_name)
    
    def add_location(self, region_name: str, location: str):
        \"\"\"添加地点\"\"\"
        region = self.regions.get(region_name)
        if region:
            region.locations.append(location)


# 全局实例
world_builder = WorldBuilder()
"""),
        ("xwe/systems/economy.py", """
\"\"\"
经济系统模块
管理游戏内的经济活动
\"\"\"

from typing import Dict, List, Optional
from dataclasses import dataclass
import math


@dataclass
class Currency:
    \"\"\"货币\"\"\"
    name: str
    symbol: str
    base_value: float  # 相对于基础货币的价值


class Market:
    \"\"\"市场\"\"\"
    
    def __init__(self, name: str):
        self.name = name
        self.items: Dict[str, float] = {}  # 物品ID -> 价格
        self.supply: Dict[str, int] = {}   # 物品ID -> 供应量
        self.demand: Dict[str, float] = {} # 物品ID -> 需求系数
    
    def update_price(self, item_id: str):
        \"\"\"根据供需更新价格\"\"\"
        if item_id not in self.items:
            return
            
        base_price = self.items[item_id]
        supply = self.supply.get(item_id, 1)
        demand = self.demand.get(item_id, 1.0)
        
        # 简单的供需公式
        price_modifier = demand / max(1, math.sqrt(supply))
        new_price = base_price * price_modifier
        
        self.items[item_id] = max(1, int(new_price))


class EconomySystem:
    \"\"\"经济系统\"\"\"
    
    def __init__(self):
        self.currencies: Dict[str, Currency] = {}
        self.markets: Dict[str, Market] = {}
        self.exchange_rates: Dict[str, Dict[str, float]] = {}
        self._init_currencies()
        self._init_markets()
    
    def _init_currencies(self):
        \"\"\"初始化货币\"\"\"
        self.currencies = {
            "gold": Currency("金币", "G", 1.0),
            "spirit_stone": Currency("灵石", "SS", 100.0),
            "contribution": Currency("贡献点", "CP", 10.0)
        }
        
        # 设置汇率
        self.exchange_rates = {
            "gold": {"spirit_stone": 0.01, "contribution": 0.1},
            "spirit_stone": {"gold": 100.0, "contribution": 10.0},
            "contribution": {"gold": 10.0, "spirit_stone": 0.1}
        }
    
    def _init_markets(self):
        \"\"\"初始化市场\"\"\"
        # 创建主城市场
        main_market = Market("主城市场")
        main_market.items = {
            "healing_potion": 50,
            "mana_potion": 80,
            "iron_sword": 200,
            "wooden_staff": 150
        }
        self.markets["main_city"] = main_market
    
    def convert_currency(self, amount: float, from_type: str, to_type: str) -> float:
        \"\"\"货币转换\"\"\"
        if from_type == to_type:
            return amount
            
        if from_type in self.exchange_rates and to_type in self.exchange_rates[from_type]:
            rate = self.exchange_rates[from_type][to_type]
            return amount * rate
            
        return 0.0
    
    def get_item_price(self, item_id: str, market_name: str = "main_city") -> Optional[float]:
        \"\"\"获取物品价格\"\"\"
        market = self.markets.get(market_name)
        if market and item_id in market.items:
            return market.items[item_id]
        return None
    
    def buy_item(self, item_id: str, quantity: int, market_name: str = "main_city") -> Optional[float]:
        \"\"\"购买物品\"\"\"
        market = self.markets.get(market_name)
        if not market or item_id not in market.items:
            return None
            
        price = market.items[item_id]
        total_cost = price * quantity
        
        # 更新供应量
        market.supply[item_id] = market.supply.get(item_id, 100) - quantity
        
        # 更新价格
        market.update_price(item_id)
        
        return total_cost
    
    def sell_item(self, item_id: str, quantity: int, market_name: str = "main_city") -> Optional[float]:
        \"\"\"出售物品\"\"\"
        market = self.markets.get(market_name)
        if not market:
            return None
            
        # 如果市场没有这个物品，创建一个基础价格
        if item_id not in market.items:
            market.items[item_id] = 10  # 基础价格
            
        price = market.items[item_id] * 0.7  # 出售价格是购买价格的70%
        total_value = price * quantity
        
        # 更新供应量
        market.supply[item_id] = market.supply.get(item_id, 0) + quantity
        
        # 更新价格
        market.update_price(item_id)
        
        return total_value


# 全局实例
economy_system = EconomySystem()
""")
    ]
    
    for module_path, content in modules_to_check:
        full_path = project_root / module_path
        if not full_path.exists():
            # 确保目录存在
            full_path.parent.mkdir(parents=True, exist_ok=True)
            # 创建文件
            full_path.write_text(content.strip())
            print(f"✅ 创建模块: {module_path}")
            missing_modules.append(module_path)
    
    if not missing_modules:
        print("✅ 所有模块都存在")
    
    return len(missing_modules)


def fix_imports():
    """修复导入问题"""
    print("🔧 修复导入问题...")
    
    # 特别检查 narrative_system.py 文件
    narrative_path = project_root / "xwe" / "features" / "narrative_system.py"
    if narrative_path.exists():
        content = narrative_path.read_text()
        # 确保所有必需的类都存在
        required_items = [
            "Achievement", "AchievementSystem", "NarrativeEventSystem",
            "OpeningEventGenerator", "StoryBranchManager", "StoryEvent",
            "check_and_display_achievements", "create_immersive_opening",
            "narrative_system"
        ]
        
        missing = []
        for item in required_items:
            if f"class {item}" not in content and f"def {item}" not in content and f"{item} =" not in content:
                missing.append(item)
        
        if missing:
            print(f"⚠️ narrative_system.py 缺少: {', '.join(missing)}")
        else:
            print("✅ narrative_system.py 包含所有必需的定义")
    
    return True


def run_quick_test():
    """运行快速测试"""
    print("🧪 运行快速测试...")
    
    test_results = []
    
    # 测试导入
    tests = [
        ("ValidationError", "from xwe.engine.expression.exceptions import ValidationError"),
        ("Achievement", "from xwe.features.narrative_system import Achievement"),
        ("content_ecosystem", "from xwe.features.content_ecosystem import content_ecosystem"),
        ("metrics_registry", "from xwe.metrics import metrics_registry"),
    ]
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            test_results.append((name, True, None))
            print(f"✅ {name}")
        except Exception as e:
            test_results.append((name, False, str(e)))
            print(f"❌ {name}: {str(e)[:50]}...")
    
    # 计算成功率
    success_count = sum(1 for _, success, _ in test_results if success)
    total_count = len(test_results)
    
    return success_count, total_count


def create_project_snapshot():
    """创建项目快照"""
    print("📸 创建项目快照...")
    
    # 运行 quick_snapshot.py
    snapshot_script = project_root / "scripts" / "quick_snapshot.py"
    if snapshot_script.exists():
        result = subprocess.run(
            [sys.executable, str(snapshot_script)],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        if result.returncode == 0:
            print("✅ 快照创建成功")
            
            # 读取并分析快照
            snapshot_file = project_root / "project_snapshot.json"
            if snapshot_file.exists():
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    errors = json.load(f)
                print(f"📊 发现 {len(errors)} 个导入错误")
                return len(errors)
        else:
            print("❌ 快照创建失败")
    else:
        print("⚠️ 快照脚本不存在")
    
    return -1


def fix_all_issues():
    """修复所有问题的主函数"""
    print("🚀 完整项目修复")
    print("=" * 60)
    
    total_steps = 6
    current_step = 0
    
    # 步骤1：清理缓存
    current_step += 1
    print_step(current_step, total_steps, "清理Python缓存")
    clean_all_cache()
    
    # 步骤2：检查并创建缺失模块
    current_step += 1
    print_step(current_step, total_steps, "检查并创建缺失模块")
    missing_count = check_missing_modules()
    
    # 步骤3：修复导入问题
    current_step += 1
    print_step(current_step, total_steps, "修复导入问题")
    fix_imports()
    
    # 步骤4：快速测试
    current_step += 1
    print_step(current_step, total_steps, "快速测试")
    success, total = run_quick_test()
    
    # 步骤5：创建项目快照
    current_step += 1
    print_step(current_step, total_steps, "创建项目快照")
    error_count = create_project_snapshot()
    
    # 步骤6：最终测试
    current_step += 1
    print_step(current_step, total_steps, "最终测试")
    try:
        # 尝试导入主应用
        from entrypoints.run_web_ui_optimized import app
        print("✅ Web UI 可以导入")
        final_status = True
    except Exception as e:
        print(f"❌ Web UI 导入失败: {e}")
        final_status = False
    
    # 生成报告
    print("\n" + "=" * 60)
    print("📊 修复报告")
    print("=" * 60)
    print(f"• 创建的缺失模块: {missing_count}")
    print(f"• 导入测试: {success}/{total} 成功")
    print(f"• 剩余错误: {error_count if error_count >= 0 else '未知'}")
    print(f"• Web UI 状态: {'✅ 可用' if final_status else '❌ 不可用'}")
    
    if final_status and error_count == 0:
        print("\n🎉 恭喜！所有问题已修复！")
        print("\n你现在可以运行:")
        print("  python entrypoints/run_web_ui_optimized.py")
    else:
        print("\n⚠️ 仍有一些问题需要解决")
        print("\n建议:")
        print("1. 查看 project_snapshot.json 了解具体错误")
        print("2. 确保所有依赖已安装: pip install -r requirements.txt")
        print("3. 手动检查报错的模块")


if __name__ == "__main__":
    fix_all_issues()
