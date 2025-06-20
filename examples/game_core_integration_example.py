"""
GameCore 集成示例

展示如何在现有的 GameCore 中集成新的模块
"""

from pathlib import Path

from xwe.core.output import (
    ConsoleChannel,
    FileChannel,
    HTMLChannel,
    MessageType,
    OutputManager,
)
from xwe.core.state import GameContext, GameStateManager


class GameCoreIntegrationExample:
    """
    展示如何集成新模块的示例类

    这不是完整的 GameCore 重写，而是展示集成方法
    """

    def __init__(self, game_mode: str = "player"):
        # === 新模块初始化 ===

        # 1. 初始化状态管理器
        self.state_manager = GameStateManager()
        self.state_manager.state.game_mode = game_mode

        # 2. 初始化输出管理器
        self.output_manager = OutputManager()
        self._setup_output_channels()

        # 3. 设置状态监听器
        self._setup_state_listeners()

        # === 向后兼容 ===

        # 保持旧的接口
        self._game_state = self.state_manager.state  # 内部使用
        self.output_buffer = []  # 兼容旧代码

        print("游戏核心初始化完成（使用新架构）")

    def _setup_output_channels(self):
        """设置输出通道"""
        # 控制台输出（彩色）
        self.output_manager.add_channel(ConsoleChannel(colored=True))

        # 文件日志
        log_path = Path("logs") / f"game_{self.state_manager.state.game_mode}.log"
        self.output_manager.add_channel(FileChannel(log_path))

        # HTML输出（可选）
        if self.state_manager.state.game_mode == "dev":
            html_path = Path("debug.html")
            self.output_manager.add_channel(
                HTMLChannel(html_path, title="游戏调试输出", auto_refresh=1)
            )

    def _setup_state_listeners(self):
        """设置状态变化监听器"""
        # 位置变化
        self.state_manager.add_listener("location_changed", self._on_location_changed)

        # 战斗状态
        self.state_manager.add_listener("combat_started", self._on_combat_started)
        self.state_manager.add_listener("combat_ended", self._on_combat_ended)

        # 成就
        self.state_manager.add_listener("achievement_unlocked", self._on_achievement)

        # 任务
        self.state_manager.add_listener("quest_completed", self._on_quest_completed)

    # === 向后兼容方法 ===

    @property
    def game_state(self):
        """兼容旧的 game_state 访问"""
        return self.state_manager.state

    def output(self, text: str) -> None:
        """兼容旧的 output 方法"""
        self.output_manager.system(text)
        self.output_buffer.append(text)  # 保持缓冲区兼容

    def get_output(self) -> list:
        """兼容旧的 get_output 方法"""
        output = self.output_buffer.copy()
        self.output_buffer.clear()
        return output

    # === 改进的方法（使用新模块）===

    def _show_status_new(self):
        """使用新的输出管理器显示状态"""
        player = self.state_manager.get_player()
        if not player:
            return

        # 构建状态数据
        status_data = {
            "姓名": player.name,
            "境界": player.get_realm_info(),
            "等级": player.attributes.cultivation_level,
            "生命": f"{int(player.attributes.current_health)}/{int(player.attributes.max_health)}",
            "灵力": f"{int(player.attributes.current_mana)}/{int(player.attributes.max_mana)}",
            "体力": f"{int(player.attributes.current_stamina)}/{int(player.attributes.max_stamina)}",
            "位置": self.state_manager.get_location(),
        }

        # 使用格式化输出
        self.output_manager.output_status(status_data, "角色状态")

        # 更新HTML显示
        self.output_manager.update_status(status_data)

    def _start_combat_new(self, target_name: str):
        """使用新架构的战斗开始"""
        # 使用状态管理器
        combat_id = f"combat_{self.state_manager.state.game_time}"
        self.state_manager.start_combat(combat_id)

        # 使用语义化输出
        self.output_manager.narrative(f"你遭遇了{target_name}！")
        self.output_manager.combat("⚔️ 战斗开始！")

        # 创建战斗上下文用于后续输出
        self.current_combat_context = combat_id

    def _process_combat_action_new(self, action: str, damage: int, target: str):
        """使用新架构处理战斗动作"""
        # 使用战斗序列输出
        combat_messages = []

        if action == "attack":
            combat_messages.extend(
                [
                    "你挥动武器发起攻击！",
                    f"剑光闪过，直取{target}要害！",
                    f"造成了 {damage} 点伤害！",
                ]
            )
        elif action == "skill":
            combat_messages.extend(
                [
                    "你运转灵力，施展技能！",
                    "强大的能量在空中凝聚...",
                    f"技能命中！造成 {damage} 点伤害！",
                ]
            )

        # 批量输出战斗信息
        self.output_manager.combat_sequence(combat_messages, context_id=self.current_combat_context)

    def _do_talk_new(self, npc_name: str):
        """使用新架构的对话系统"""
        # 进入对话上下文
        self.state_manager.push_context(GameContext.DIALOGUE, {"npc_name": npc_name})

        # 对话示例
        exchanges = [
            (npc_name, "你好，年轻的修士。"),
            (npc_name, "我看你骨骼清奇，是个修仙的好苗子。"),
            ("你", "多谢前辈夸奖，晚辈定当努力修炼。"),
            (npc_name, "很好，这是我的一点心意，拿去吧。"),
        ]

        # 使用对话交流输出
        self.output_manager.dialogue_exchange(exchanges)

        # 奖励
        self.output_manager.success("获得灵石 x10")
        self.output_manager.success("获得《基础吐纳法》x1")

        # 退出对话上下文
        self.state_manager.pop_context()

    def _do_explore_new(self):
        """使用新架构的探索系统"""
        location = self.state_manager.get_location()

        # 批处理模式用于多行输出
        self.output_manager.enable_batch_mode()

        self.output_manager.narrative("你仔细探索着周围的环境...")

        # 模拟探索结果
        discoveries = [
            {"发现": "灵草", "数量": 3, "品质": "普通"},
            {"发现": "铁矿石", "数量": 5, "品质": "普通"},
            {"发现": "神秘卷轴", "数量": 1, "品质": "稀有"},
        ]

        if discoveries:
            self.output_manager.success("你有所发现！")
            self.output_manager.output_table(discoveries)

        # 刷新批处理
        self.output_manager.disable_batch_mode()

        # 更新统计
        self.state_manager.update_statistics("areas_explored", 1)

    # === 状态监听器回调 ===

    def _on_location_changed(self, data):
        """位置变化回调"""
        old_loc = data["old"]
        new_loc = data["new"]

        # 使用叙述性输出
        self.output_manager.narrative(f"你离开了{old_loc}，来到了{new_loc}。")

        # 描述新位置
        location_descs = {
            "青云山": "青山绿水，仙气缭绕，正是修炼的好地方。",
            "主城": "人来人往，热闹非凡，各种商铺应有尽有。",
            "妖兽森林": "古木参天，不时传来兽吼声，危机四伏。",
        }

        if new_loc in location_descs:
            self.output_manager.narrative(location_descs[new_loc])

    def _on_combat_started(self, data):
        """战斗开始回调"""
        self.output_manager.system("进入战斗模式")
        # 可以播放战斗音乐等

    def _on_combat_ended(self, data):
        """战斗结束回调"""
        if data.get("winner") == "player":
            self.output_manager.success("战斗胜利！")
            self.output_manager.narrative("你深吸一口气，收起武器。")
        else:
            self.output_manager.error("战斗失败...")
            self.output_manager.narrative("你需要更多的修炼...")

    def _on_achievement(self, data):
        """成就解锁回调"""
        achievement_id = data["achievement"]

        # 成就描述
        achievements = {
            "first_kill": "初战告捷 - 击败第一个敌人",
            "first_cultivation": "踏入仙途 - 第一次修炼",
            "explorer_10": "探索者 - 探索10个区域",
        }

        desc = achievements.get(achievement_id, achievement_id)
        self.output_manager.achievement(f"🏆 成就解锁：{desc}")

    def _on_quest_completed(self, data):
        """任务完成回调"""
        quest_id = data["quest_id"]
        quest = self.state_manager.state.quests.get(quest_id, {})

        # 使用上下文输出任务完成信息
        ctx_id = f"quest_complete_{quest_id}"
        self.output_manager.create_context(ctx_id, "quest")

        self.output_manager.achievement(
            f"任务完成：{quest.get('name', quest_id)}", context_id=ctx_id
        )

        if "rewards" in quest:
            self.output_manager.success("获得奖励：", context_id=ctx_id)
            rewards_data = [{"奖励": k, "数量": v} for k, v in quest["rewards"].items()]
            self.output_manager.output_table(rewards_data, context_id=ctx_id)

        self.output_manager.end_context(ctx_id)

    # === 演示方法 ===

    def demo_new_features(self):
        """演示新功能"""
        print("\n=== 新架构功能演示 ===\n")

        # 创建测试玩家
        from xwe.core.character import Character, CharacterType

        player = Character(name="测试侠", character_type=CharacterType.PLAYER)
        self.state_manager.set_player(player)

        # 1. 状态显示
        print("--- 格式化状态显示 ---")
        self._show_status_new()

        # 2. 位置变化
        print("\n--- 位置变化和叙述 ---")
        self.state_manager.set_location("妖兽森林")

        # 3. 探索
        print("\n--- 探索系统 ---")
        self._do_explore_new()

        # 4. 战斗
        print("\n--- 战斗序列 ---")
        self._start_combat_new("赤炎虎")
        self._process_combat_action_new("attack", 50, "赤炎虎")
        self._process_combat_action_new("skill", 100, "赤炎虎")

        # 结束战斗
        self.state_manager.end_combat({"winner": "player"})

        # 5. 对话
        print("\n--- 对话系统 ---")
        self._do_talk_new("神秘长老")

        # 6. 成就
        print("\n--- 成就系统 ---")
        self.state_manager.add_achievement("first_kill")
        self.state_manager.add_achievement("explorer_10")

        # 7. 输出历史
        print("\n--- 搜索历史（包含'获得'的消息）---")
        results = self.output_manager.search_history("获得")
        for msg in results[-5:]:  # 显示最后5条
            print(f"  [{msg.type.value}] {msg.content}")


def main():
    """主函数"""
    # 创建集成示例
    game = GameCoreIntegrationExample(game_mode="dev")

    # 运行演示
    game.demo_new_features()

    print("\n" + "=" * 50)
    print("集成演示完成！")
    print("\n生成的文件：")
    print("- logs/game_dev.log (游戏日志)")
    print("- debug.html (实时HTML显示)")
    print("\n这个示例展示了如何在现有的GameCore中集成新模块，")
    print("同时保持向后兼容性。实际集成时可以逐步迁移。")


if __name__ == "__main__":
    main()
