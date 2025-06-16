#!/usr/bin/env python3
# @dev_only
"""
展示如何在主游戏中使用修复后的系统和增强的UI
"""
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from xwe.features.html_output import HtmlGameLogger
from xwe.features.enhanced_output import EnhancedGameOutput


class XianXiaGameDemo:
    """修仙游戏演示"""
    
    def __init__(self):
        # 初始化HTML输出
        self.html_logger = HtmlGameLogger("xianxia_game.html", refresh_interval=1)
        self.output = EnhancedGameOutput(self.html_logger)
        
        # 模拟玩家数据
        self.player = {
            "name": "凌天",
            "realm": "筑基期",
            "level": 3,
            "health": 150,
            "max_health": 200,
            "mana": 80,
            "max_mana": 100,
            "attack": 45,
            "defense": 30
        }
        
        # 更新状态显示
        self.update_status()
        
    def update_status(self):
        """更新状态显示"""
        self.html_logger.update_status(self.player)
        
    def start_game(self):
        """游戏开始"""
        self.output.output("=== 修仙世界引擎 v2.0 ===", "system")
        self.output.output("所有系统已优化，战斗更加平衡", "system")
        self.output.output("UI显示已改进，多行内容统一显示", "system")
        
        self.output.output("\n欢迎来到修仙世界！", "success")
        self.output.output(f"你是{self.player['name']}，一名{self.player['realm']}的修士。", "system")
        
        # 显示玩家状态
        self.show_player_status()
        
        # 模拟一些游戏内容
        self.explore_area()
        self.encounter_enemy()
        self.find_spiritual_vein()
        
    def show_player_status(self):
        """显示玩家状态"""
        self.output.status_report({
            "姓名": self.player["name"],
            "境界": f"{self.player['realm']}第{self.player['level']}层",
            "生命": f"{self.player['health']}/{self.player['max_health']}",
            "法力": f"{self.player['mana']}/{self.player['max_mana']}",
            "攻击": self.player["attack"],
            "防御": self.player["defense"]
        })
        
    def explore_area(self):
        """探索区域"""
        self.output.output("\n你开始探索周围的区域...", "system")
        self.output.output("发现了一片密林", "system")
        self.output.output("林中灵气充沛，适合修炼", "system")
        self.output.output("但也可能隐藏着危险", "system")
        
    def encounter_enemy(self):
        """遭遇敌人"""
        self.output.output("\n突然，一只妖兽从林中跃出！", "combat")
        
        # 模拟战斗
        combat_log = [
            "【战斗开始】",
            "妖兽发起了攻击！",
            "你灵活地闪避开来",
            "你使用「剑气斩」反击",
            "命中！造成 52 点伤害（元素相克加成：1.2x）",
            "妖兽愤怒地咆哮",
            "妖兽使用「野性冲撞」",
            "你受到 25 点伤害",
            "你使用「金刚护体」增强防御",
            "再次使用「剑气斩」",
            "暴击！造成 78 点伤害（暴击倍率：1.5x）",
            "妖兽倒下了！",
            "【战斗胜利】",
            "获得经验值：150",
            "获得物品：妖兽内丹 x1"
        ]
        
        self.output.combat_sequence(combat_log)
        
        # 更新玩家状态
        self.player["health"] = 125
        self.update_status()
        
    def find_spiritual_vein(self):
        """发现灵脉"""
        self.output.output("\n继续深入密林，你感到灵气越来越浓郁...", "system")
        
        discovery_text = """
你发现了一处隐藏的灵脉！

【福地灵脉】
- 品质：福地级
- 修炼加成：1.5倍
- 特殊效果：小概率触发顿悟（5%）
- 当前状态：无主

这是一处天然形成的灵脉，灵气充沛，非常适合修炼。
如果能在此地修炼，必定事半功倍。
"""
        self.output.output(discovery_text.strip(), "success")
        
        # 提供选择
        self.output.dialogue_exchange(
            "系统提示",
            "你要如何处理这处灵脉？",
            [
                "立即占据并开始修炼",
                "先布置防护阵法",
                "标记位置，以后再来",
                "寻找灵脉的源头"
            ]
        )
        
    def demonstrate_ui_improvements(self):
        """演示UI改进"""
        self.output.output("\n=== UI改进演示 ===", "system")
        
        # 演示多行列表在一个框内
        list_text = """
当前可用命令：
- 移动：前往不同区域
- 修炼：提升境界和属性
- 战斗：与敌人战斗
- 探索：发现新地点
- 背包：查看物品
- 技能：查看和使用技能
- 任务：查看当前任务
- 社交：与NPC互动
"""
        self.output.output(list_text.strip(), "system")
        
        # 演示复杂信息展示
        info_text = """
【灵脉系统说明】

灵脉是天地间灵气汇聚之处，分为多个等级：
• 贫瘠之地（0.5x）：灵气稀薄
• 普通灵脉（1.0x）：标准修炼环境
• 福地灵脉（1.5x）：灵气充沛，有概率顿悟
• 洞天灵脉（2.0x）：元素亲和度提升20%
• 仙灵宝地（3.0x）：突破瓶颈成功率+50%

占据灵脉后可以获得修炼加成，但也需要防御其他修士的争夺。
高品质的灵脉往往会引起激烈的争夺，请做好准备。
"""
        self.output.output(info_text.strip(), "system")


def main():
    """主函数"""
    print("启动修仙世界引擎演示...")
    print("HTML输出文件将生成在: xianxia_game.html")
    print("-" * 50)
    
    # 创建游戏实例
    game = XianXiaGameDemo()
    
    # 开始游戏
    game.start_game()
    
    # 演示UI改进
    game.demonstrate_ui_improvements()
    
    print("\n" + "-" * 50)
    print("✅ 演示完成！")
    print("📄 请在浏览器中打开 xianxia_game.html 查看效果")
    print("🔄 页面会每秒自动刷新")


if __name__ == "__main__":
    main()
