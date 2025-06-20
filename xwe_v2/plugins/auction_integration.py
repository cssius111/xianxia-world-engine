"""
拍卖行系统集成示例

展示如何将拍卖行系统集成到主游戏中
"""

from xwe_v2.core.command_parser import CommandParser
from xwe_v2.plugins.auction_commands import auction_command_handler


def integrate_auction_system(command_parser: CommandParser) -> None:
    """
    将拍卖行系统集成到游戏命令解析器中

    Args:
        command_parser: 游戏的命令解析器实例
    """

    # 注册拍卖行相关命令
    auction_commands = {
        "拍卖行": "进入拍卖行查看信息",
        "参加拍卖": "参加当前的拍卖会",
        "出价": "在拍卖中出价（需要指定金额）",
        "放弃": "放弃当前拍品的竞拍",
        "离开拍卖行": "离开拍卖行",
        "拍卖帮助": "查看拍卖行使用指南",
    }

    # 将命令添加到命令解析器
    for cmd, desc in auction_commands.items():
        # 这里假设command_parser有register_command方法
        # 实际集成时需要根据具体的命令系统进行调整
        pass

    print("拍卖行系统已集成到游戏中！")


def handle_auction_in_game_loop(game, player, command, params=None) -> None:
    """
    在游戏主循环中处理拍卖行命令

    Args:
        game: 游戏实例
        player: 玩家角色
        command: 输入的命令
        params: 命令参数

    Returns:
        处理结果文本
    """

    # 检查是否是拍卖行相关命令
    auction_commands = ["拍卖行", "参加拍卖", "出价", "放弃", "离开拍卖行", "拍卖帮助"]

    if command in auction_commands:
        # 处理拍卖行命令
        result = auction_command_handler.handle_auction_command(player, command, params)

        # 如果在拍卖中，可能需要特殊的提示
        if auction_command_handler.is_in_auction():
            prompt = auction_command_handler.get_auction_prompt()
            if prompt:
                result += f"\n\n{prompt}"

        return result

    return None


# 示例：如何在game_core.py中集成
"""
# 在 GameCore 类的 run 方法中添加拍卖行命令处理

def run(self) -> None:
    while self.running:
        # ... 现有代码 ...

        # 获取玩家输入
        user_input = input("> ").strip()

        # 解析命令
        parsed = self.command_parser.parse(user_input)

        # 首先检查是否是拍卖行命令
        if parsed.command in ["拍卖行", "参加拍卖", "出价", "放弃", "离开拍卖行", "拍卖帮助"]:
            result = auction_command_handler.handle_auction_command(
                self.player,
                parsed.command,
                parsed.params
            )
            print(result)
            continue

        # ... 处理其他命令 ...
"""


# 示例：添加到地点系统
def add_auction_house_location() -> None:
    """
    将拍卖行添加为一个可访问的地点

    返回地点配置
    """
    auction_house_location = {
        "id": "tiannan_auction_house",
        "name": "天宝拍卖行",
        "type": "special",
        "description": "玄苍界最大的拍卖行，每日都有珍稀宝物拍卖。金碧辉煌的大厅中，来自各方的修士正在激烈竞价。",
        "connections": ["tiannan_fangshi"],  # 连接到天南坊市
        "features": ["拍卖行"],
        "npcs": ["柳掌柜"],
        "events": [
            {
                "type": "enter",
                "probability": 1.0,
                "description": "你走进拍卖行，立刻被热闹的气氛所感染。",
            }
        ],
        "commands": {
            "参加拍卖": "参加正在进行的拍卖会",
            "查看公告": "查看今日拍卖物品公告",
            "申请包厢": "申请VIP包厢（需要资格）",
        },
    }

    return auction_house_location


# 示例：拍卖行相关的成就
def get_auction_achievements() -> None:
    """
    获取拍卖行相关的成就配置
    """
    achievements = [
        {
            "id": "first_auction_win",
            "name": "初入拍场",
            "description": "第一次在拍卖会上成功拍得物品",
            "points": 10,
            "category": "special",
        },
        {
            "id": "auction_millionaire",
            "name": "豪掷千金",
            "description": "在一次拍卖会上花费超过10万灵石",
            "points": 50,
            "category": "special",
        },
        {
            "id": "auction_survivor",
            "name": "全身而退",
            "description": "拍得珍贵物品后成功躲过劫杀",
            "points": 30,
            "category": "combat",
        },
        {
            "id": "grudge_bidding",
            "name": "意气之争",
            "description": "在仇敌的恶意抬价下依然拍得物品",
            "points": 20,
            "category": "social",
        },
        {
            "id": "vip_member",
            "name": "贵宾待遇",
            "description": "成为拍卖行的VIP会员",
            "points": 25,
            "category": "special",
        },
    ]

    return achievements


if __name__ == "__main__":
    # 打印集成指南
    print("=== 拍卖行系统集成指南 ===\n")

    print("1. 命令集成：")
    print("   在 command_parser.py 中注册拍卖行命令")
    print("   在 game_core.py 的主循环中处理拍卖命令\n")

    print("2. 地点集成：")
    print("   在地图数据中添加拍卖行地点")
    print("   设置从坊市到拍卖行的通路\n")

    print("3. 成就集成：")
    print("   在成就系统中添加拍卖相关成就")
    print("   在拍卖事件中触发成就检查\n")

    print("4. 数据集成：")
    print("   确保物品系统与拍卖品兼容")
    print("   在玩家数据中记录拍卖历史\n")

    print("5. UI集成：")
    print("   如果有Web UI，添加拍卖行界面")
    print("   显示实时竞价信息和倒计时\n")
