"""
集成增强输出系统到主游戏
"""
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from xwe.features.html_output import HtmlGameLogger
from xwe.features.enhanced_output import EnhancedGameOutput


def integrate_enhanced_output(game_instance):
    """
    将增强输出系统集成到游戏实例
    
    Args:
        game_instance: 游戏实例对象
    """
    # 创建HTML日志器
    html_logger = HtmlGameLogger("game_log.html", refresh_interval=1)
    
    # 创建增强输出处理器
    output_handler = EnhancedGameOutput(html_logger)
    
    # 替换游戏的输出方法
    original_print = game_instance.print if hasattr(game_instance, 'print') else print
    
    def enhanced_print(text, category="system", **kwargs):
        """增强的打印函数"""
        # 使用增强输出处理器
        output_handler.output(str(text), category)
        
    # 绑定到游戏实例
    game_instance.print = enhanced_print
    game_instance.output = output_handler
    game_instance.html_logger = html_logger
    
    # 添加便捷方法
    game_instance.combat_log = lambda actions: output_handler.combat_sequence(actions)
    game_instance.show_status = lambda status: output_handler.status_report(status)
    game_instance.show_dialogue = lambda speaker, text, options=None: output_handler.dialogue_exchange(speaker, text, options)
    
    return output_handler


# 测试代码
if __name__ == "__main__":
    # 模拟游戏实例
    class MockGame:
        def __init__(self):
            self.name = "修仙世界引擎"
            
    game = MockGame()
    output = integrate_enhanced_output(game)
    
    # 测试输出
    game.print("欢迎来到修仙世界！", "system")
    game.print("这是一个充满机遇与挑战的世界。", "system")
    
    # 测试战斗日志
    game.combat_log([
        "战斗开始！",
        "你使用了「剑气斩」",
        "暴击！造成了 150 点伤害",
        "妖兽反击，你受到 30 点伤害",
        "你使用了「金刚护体」",
        "成功格挡了妖兽的攻击",
        "战斗胜利！"
    ])
    
    # 测试状态显示
    game.show_status({
        "姓名": "张三",
        "境界": "筑基期三层",
        "生命": "150/200",
        "法力": "80/100",
        "经验": "2500/5000"
    })
    
    # 测试对话
    game.show_dialogue(
        "掌门",
        "你已经在筑基期停留了很久，是时候尝试突破了。这是一颗金丹期突破丹，祝你好运！",
        ["多谢掌门！", "弟子还需要再准备准备", "请问突破的要点是什么？"]
    )
    
    print("\n✅ 增强输出系统集成成功！")
    print(f"📄 HTML日志文件: {os.path.abspath('game_log.html')}")
