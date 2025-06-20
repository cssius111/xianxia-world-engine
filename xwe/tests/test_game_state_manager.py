"""
游戏状态管理器测试

测试 GameStateManager 的所有功能
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from xwe.core.attributes import AttributeSystem
from xwe.core.character import Character, CharacterType
from xwe.core.state import ContextInfo, GameContext, GameState, GameStateManager
from xwe.engine.expression import ExpressionParser


class TestGameStateManager:
    """GameStateManager 测试类"""

    @pytest.fixture
    def state_manager(self):
        """创建测试用的状态管理器"""
        return GameStateManager()

    @pytest.fixture
    def test_player(self):
        """创建测试用的玩家角色"""
        player = Character(name="测试玩家", character_type=CharacterType.PLAYER)
        player.id = "player_001"
        return player

    # === 上下文管理测试 ===

    def test_push_pop_context(self, state_manager):
        """测试上下文栈的推入和弹出"""
        # 初始状态应该没有上下文
        assert state_manager.get_current_context() is None

        # 推入探索上下文
        state_manager.push_context(GameContext.EXPLORATION)
        assert state_manager.get_current_context() == GameContext.EXPLORATION

        # 推入战斗上下文
        state_manager.push_context(GameContext.COMBAT, {"combat_id": "battle_001"})
        assert state_manager.get_current_context() == GameContext.COMBAT
        assert state_manager.get_context_data()["combat_id"] == "battle_001"

        # 弹出战斗上下文
        context = state_manager.pop_context()
        assert context.context_type == GameContext.COMBAT
        assert state_manager.get_current_context() == GameContext.EXPLORATION

        # 弹出探索上下文
        state_manager.pop_context()
        assert state_manager.get_current_context() is None

    def test_update_context_data(self, state_manager):
        """测试更新上下文数据"""
        state_manager.push_context(GameContext.DIALOGUE, {"npc_id": "npc_001"})

        # 更新数据
        state_manager.update_context_data({"dialogue_node": "greeting"})

        data = state_manager.get_context_data()
        assert data["npc_id"] == "npc_001"
        assert data["dialogue_node"] == "greeting"

    def test_is_in_context(self, state_manager):
        """测试上下文检查"""
        state_manager.push_context(GameContext.EXPLORATION)
        state_manager.push_context(GameContext.DIALOGUE)

        assert state_manager.is_in_context(GameContext.EXPLORATION)
        assert state_manager.is_in_context(GameContext.DIALOGUE)
        assert not state_manager.is_in_context(GameContext.COMBAT)

    def test_clear_context_stack(self, state_manager):
        """测试清空上下文栈"""
        state_manager.push_context(GameContext.EXPLORATION)
        state_manager.push_context(GameContext.COMBAT)

        state_manager.clear_context_stack()
        assert state_manager.get_current_context() is None
        assert len(state_manager.context_stack) == 0

    # === 状态访问和修改测试 ===

    def test_player_management(self, state_manager, test_player):
        """测试玩家管理"""
        # 初始没有玩家
        assert state_manager.get_player() is None

        # 设置玩家
        state_manager.set_player(test_player)
        assert state_manager.get_player() == test_player
        assert state_manager.state.player_id == test_player.id

    def test_location_management(self, state_manager):
        """测试位置管理"""
        # 检查默认位置
        assert state_manager.get_location() == "qingyun_city"

        # 更改位置
        state_manager.set_location("mystic_forest")
        assert state_manager.get_location() == "mystic_forest"

    def test_flag_management(self, state_manager):
        """测试标记管理"""
        # 获取不存在的标记
        assert state_manager.get_flag("test_flag") is None
        assert state_manager.get_flag("test_flag", "default") == "default"

        # 设置标记
        state_manager.set_flag("test_flag", True)
        assert state_manager.get_flag("test_flag") is True

        # 更新标记
        state_manager.set_flag("test_flag", "new_value")
        assert state_manager.get_flag("test_flag") == "new_value"

    def test_statistics_update(self, state_manager):
        """测试统计数据更新"""
        # 更新数值统计
        state_manager.update_statistics("enemies_defeated", 1)
        state_manager.update_statistics("enemies_defeated", 2)
        assert state_manager.state.statistics["enemies_defeated"] == 3

        # 更新非数值统计
        state_manager.update_statistics("last_save", "2024-01-01")
        assert state_manager.state.statistics["last_save"] == "2024-01-01"

    def test_achievement_management(self, state_manager):
        """测试成就管理"""
        # 初始没有成就
        assert len(state_manager.state.achievements) == 0

        # 添加成就
        state_manager.add_achievement("first_kill")
        assert "first_kill" in state_manager.state.achievements

        # 重复添加成就（不应重复）
        state_manager.add_achievement("first_kill")
        assert len(state_manager.state.achievements) == 1

    # === 战斗状态管理测试 ===

    def test_combat_management(self, state_manager):
        """测试战斗管理"""
        # 初始不在战斗中
        assert not state_manager.is_in_combat()

        # 开始战斗
        state_manager.start_combat("combat_001")
        assert state_manager.is_in_combat()
        assert state_manager.state.current_combat == "combat_001"
        assert state_manager.get_current_context() == GameContext.COMBAT

        # 结束战斗
        result = {"winner": "player", "exp_gained": 100}
        state_manager.end_combat(result)
        assert not state_manager.is_in_combat()
        assert state_manager.get_current_context() is None
        assert len(state_manager.state.combat_history) == 1
        assert state_manager.state.combat_history[0]["result"] == result

    # === NPC管理测试 ===

    def test_npc_management(self, state_manager):
        """测试NPC管理"""
        # 创建测试NPC
        npc = Character(name="测试NPC", character_type=CharacterType.NPC)
        npc.id = "npc_001"

        # 添加NPC
        state_manager.add_npc(npc)
        assert state_manager.get_npc("npc_001") == npc

        # 更新关系
        state_manager.update_npc_relationship("npc_001", 10)
        assert state_manager.state.npc_relationships["npc_001"] == 10

        state_manager.update_npc_relationship("npc_001", -5)
        assert state_manager.state.npc_relationships["npc_001"] == 5

        # 移除NPC
        state_manager.remove_npc("npc_001")
        assert state_manager.get_npc("npc_001") is None

    # === 任务管理测试 ===

    def test_quest_management(self, state_manager):
        """测试任务管理"""
        # 添加任务
        quest_data = {
            "name": "初出茅庐",
            "description": "完成第一个任务",
            "progress": 0,
            "target": 1,
        }
        state_manager.add_quest("quest_001", quest_data)
        assert "quest_001" in state_manager.state.quests

        # 更新任务
        state_manager.update_quest("quest_001", {"progress": 1})
        assert state_manager.state.quests["quest_001"]["progress"] == 1

        # 完成任务
        state_manager.complete_quest("quest_001")
        assert state_manager.state.quests["quest_001"]["completed"] is True
        assert "completed_at" in state_manager.state.quests["quest_001"]

    # === 状态监听器测试 ===

    def test_state_listeners(self, state_manager):
        """测试状态监听器"""
        # 创建模拟回调
        callback = Mock()

        # 添加监听器
        state_manager.add_listener("location_changed", callback)

        # 触发事件
        state_manager.set_location("new_location")

        # 验证回调被调用
        callback.assert_called_once()
        args = callback.call_args[0][0]
        assert args["old"] == "qingyun_city"
        assert args["new"] == "new_location"

        # 移除监听器
        state_manager.remove_listener("location_changed", callback)
        callback.reset_mock()

        # 再次触发不应调用
        state_manager.set_location("another_location")
        callback.assert_not_called()

    # === 状态持久化测试 ===

    def test_save_load_state(self, state_manager, test_player):
        """测试状态保存和加载"""
        # 设置一些状态
        state_manager.set_player(test_player)
        state_manager.set_location("test_location")
        state_manager.set_flag("test_flag", True)
        state_manager.push_context(GameContext.DIALOGUE, {"npc": "test_npc"})

        # 保存状态
        with tempfile.TemporaryDirectory() as tmp_dir:
            save_path = Path(tmp_dir) / "test_save.json"
            state_manager.save_state(save_path)

            # 验证文件存在
            assert save_path.exists()

            # 创建新的状态管理器并加载
            new_manager = GameStateManager()
            new_manager.load_state(save_path)

            # 验证状态恢复
            assert new_manager.get_player().name == test_player.name
            assert new_manager.get_location() == "test_location"
            assert new_manager.get_flag("test_flag") is True
            assert new_manager.get_current_context() == GameContext.DIALOGUE
            assert new_manager.get_context_data()["npc"] == "test_npc"

    def test_snapshots(self, state_manager):
        """测试状态快照"""
        # 创建初始状态
        state_manager.set_location("location_1")
        state_manager.create_snapshot()

        # 修改状态
        state_manager.set_location("location_2")
        state_manager.create_snapshot()

        # 再次修改
        state_manager.set_location("location_3")

        # 恢复到第二个快照
        assert state_manager.restore_snapshot(-1)
        assert state_manager.get_location() == "location_2"

        # 恢复到第一个快照
        assert state_manager.restore_snapshot(0)
        assert state_manager.get_location() == "location_1"

    # === 状态验证测试 ===

    def test_validate_state(self, state_manager):
        """测试状态验证"""
        # 空状态应该有错误
        errors = state_manager.validate_state()
        assert "玩家角色未设置" in errors

        # 设置玩家后
        player = Character(name="测试玩家", character_type=CharacterType.PLAYER)
        state_manager.set_player(player)
        errors = state_manager.validate_state()
        assert "玩家角色未设置" not in errors

        # 创建不一致的状态
        state_manager.push_context(GameContext.COMBAT)
        errors = state_manager.validate_state()
        assert any("战斗上下文与战斗状态不一致" in e for e in errors)

    def test_game_info(self, state_manager, test_player):
        """测试游戏信息摘要"""
        state_manager.set_player(test_player)
        state_manager.push_context(GameContext.EXPLORATION)
        state_manager.add_quest("quest_001", {})
        state_manager.add_achievement("achievement_001")

        info = state_manager.get_game_info()

        assert info["player_name"] == test_player.name
        assert info["location"] == "qingyun_city"
        assert info["current_context"] == "EXPLORATION"
        assert info["quest_count"] == 1
        assert info["achievement_count"] == 1
        assert info["game_mode"] == "player"
        assert info["difficulty"] == "normal"

    # === 自动保存测试 ===

    @patch("xwe.core.state.game_state_manager.datetime")
    def test_auto_save(self, mock_datetime, state_manager):
        """测试自动保存功能"""
        # 设置模拟时间
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = start_time

        # 初始化时记录了最后保存时间
        state_manager._last_auto_save = start_time

        # 未到自动保存间隔
        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 4, 0)

        with patch.object(state_manager, "save_state") as mock_save:
            state_manager.check_auto_save()
            mock_save.assert_not_called()

        # 超过自动保存间隔
        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 6, 0)

        with patch.object(state_manager, "save_state") as mock_save:
            state_manager.check_auto_save()
            mock_save.assert_called_once()

            # 验证保存路径
            save_path = mock_save.call_args[0][0]
            assert str(save_path) == "saves/auto/autosave.json"


class TestGameState:
    """GameState 数据类测试"""

    def test_to_dict_from_dict(self):
        """测试序列化和反序列化"""
        # 创建原始状态
        original = GameState()
        original.game_time = 100
        original.flags = {"test": True}
        original.achievements = {"first_kill", "first_quest"}

        # 添加玩家
        player = Character(name="测试玩家", character_type=CharacterType.PLAYER)
        original.player = player

        # 序列化
        data = original.to_dict()

        # 反序列化
        restored = GameState.from_dict(data)

        # 验证
        assert restored.game_time == original.game_time
        assert restored.flags == original.flags
        assert restored.achievements == original.achievements
        assert restored.player.name == original.player.name


class TestContextInfo:
    """ContextInfo 测试"""

    def test_serialization(self):
        """测试上下文信息序列化"""
        context = ContextInfo(context_type=GameContext.COMBAT, data={"combat_id": "test_001"})

        # 序列化
        data = context.to_dict()
        assert data["context_type"] == "COMBAT"
        assert data["data"]["combat_id"] == "test_001"

        # 反序列化
        restored = ContextInfo.from_dict(data)
        assert restored.context_type == GameContext.COMBAT
        assert restored.data["combat_id"] == "test_001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
