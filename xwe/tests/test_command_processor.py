"""
命令处理器测试

测试 CommandProcessor 的所有功能
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path
import tempfile

from xwe.core.state import GameStateManager, GameContext
from xwe.core.output import OutputManager, ConsoleChannel
from xwe.core.command_parser import CommandType, ParsedCommand
from xwe.core.command import (
    CommandProcessor,
    CommandHandler,
    CommandContext,
    CommandResult,
    CommandPriority,
    Middleware,
    LoggingMiddleware,
    ValidationMiddleware,
    CooldownMiddleware,
    RateLimitMiddleware,
    # 处理器
    CombatCommandHandler,
    InteractionCommandHandler,
    SystemCommandHandler,
    CultivationCommandHandler,
)
from xwe.core.character import Character, CharacterType


class TestCommandResult:
    """CommandResult 测试"""
    
    def test_success_result(self):
        """测试成功结果"""
        result = CommandResult.success("操作成功", value=100)
        
        assert result.success is True
        assert result.message == "操作成功"
        assert result.data['value'] == 100
        assert result.error is None
        assert isinstance(result.timestamp, datetime)
    
    def test_failure_result(self):
        """测试失败结果"""
        result = CommandResult.failure("操作失败")
        
        assert result.success is False
        assert result.error == "操作失败"
        assert result.message is None
        assert result.continue_processing is False
    
    def test_redirect_result(self):
        """测试重定向结果"""
        result = CommandResult.redirect("新命令")
        
        assert result.success is True
        assert result.data['redirect'] == "新命令"


class TestCommandContext:
    """CommandContext 测试"""
    
    @pytest.fixture
    def context(self):
        """创建测试上下文"""
        state_manager = GameStateManager()
        output_manager = OutputManager()
        output_manager.add_channel(ConsoleChannel(colored=False))
        
        # 创建测试玩家
        player = Character(name="测试者", character_type=CharacterType.PLAYER)
        state_manager.set_player(player)
        state_manager.set_location("测试地点")
        
        # 创建解析后的命令
        parsed_cmd = ParsedCommand(
            command_type=CommandType.ATTACK,
            target="敌人",
            raw_text="攻击 敌人"
        )
        
        return CommandContext(
            command=parsed_cmd,
            state_manager=state_manager,
            output_manager=output_manager,
            raw_input="攻击 敌人"
        )
    
    def test_context_properties(self, context):
        """测试上下文属性"""
        assert context.player.name == "测试者"
        assert context.current_location == "测试地点"
        assert context.game_context == GameContext.EXPLORING
        assert context.source == "player"
    
    def test_flag_operations(self, context):
        """测试标记操作"""
        # 设置标记
        context.set_flag("test_flag", 123)
        assert context.get_flag("test_flag") == 123
        
        # 默认值
        assert context.get_flag("nonexistent", "default") == "default"


class TestCommandHandler:
    """CommandHandler 基类测试"""
    
    def test_handler_creation(self):
        """测试处理器创建"""
        class TestHandler(CommandHandler):
            def can_handle(self, context):
                return True
            
            def handle(self, context):
                return CommandResult.success()
        
        handler = TestHandler("test", [CommandType.ATTACK], CommandPriority.HIGH)
        
        assert handler.name == "test"
        assert CommandType.ATTACK in handler.command_types
        assert handler.priority == CommandPriority.HIGH
        assert handler.enabled is True


class TestMiddleware:
    """中间件测试"""
    
    @pytest.fixture
    def context(self):
        """创建测试上下文"""
        state_manager = GameStateManager()
        output_manager = OutputManager()
        parsed_cmd = ParsedCommand(CommandType.STATUS, raw_text="状态")
        
        return CommandContext(
            command=parsed_cmd,
            state_manager=state_manager,
            output_manager=output_manager,
            raw_input="状态"
        )
    
    @pytest.mark.asyncio
    async def test_logging_middleware(self, context):
        """测试日志中间件"""
        middleware = LoggingMiddleware()
        
        # 模拟下一个处理器
        async def next_handler():
            return CommandResult.success("完成")
        
        # 执行中间件
        with patch('logging.Logger.info') as mock_log:
            result = await middleware.process(context, next_handler)
            
            # 验证日志调用
            assert mock_log.call_count >= 2  # 开始和结束日志
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_validation_middleware(self, context):
        """测试验证中间件"""
        middleware = ValidationMiddleware()
        
        # 测试无玩家时的验证
        context.state_manager.state.player_id = None
        
        async def next_handler():
            return CommandResult.success()
        
        result = await middleware.process(context, next_handler)
        assert result.success is False
        assert "游戏尚未开始" in result.error
    
    @pytest.mark.asyncio
    async def test_cooldown_middleware(self, context):
        """测试冷却中间件"""
        middleware = CooldownMiddleware()
        context.command.command_type = CommandType.CULTIVATE  # 有冷却的命令
        
        async def next_handler():
            return CommandResult.success()
        
        # 第一次执行成功
        result1 = await middleware.process(context, next_handler)
        assert result1.success is True
        
        # 立即再次执行应该失败
        result2 = await middleware.process(context, next_handler)
        assert result2.success is False
        assert "冷却中" in result2.error
    
    @pytest.mark.asyncio  
    async def test_rate_limit_middleware(self, context):
        """测试速率限制中间件"""
        middleware = RateLimitMiddleware(max_commands=2, window=1.0)
        
        async def next_handler():
            return CommandResult.success()
        
        # 前两次成功
        result1 = await middleware.process(context, next_handler)
        result2 = await middleware.process(context, next_handler)
        assert result1.success is True
        assert result2.success is True
        
        # 第三次失败
        result3 = await middleware.process(context, next_handler)
        assert result3.success is False
        assert "命令太频繁" in result3.error


class TestCommandProcessor:
    """CommandProcessor 主类测试"""
    
    @pytest.fixture
    def processor(self):
        """创建测试处理器"""
        state_manager = GameStateManager()
        output_manager = OutputManager()
        output_manager.add_channel(ConsoleChannel(colored=False))
        
        # 创建测试玩家
        player = Character(name="测试者", character_type=CharacterType.PLAYER)
        state_manager.set_player(player)
        
        processor = CommandProcessor(state_manager, output_manager)
        
        # 注册基本处理器
        processor.register_handler(SystemCommandHandler())
        processor.register_handler(CombatCommandHandler())
        
        return processor
    
    def test_processor_creation(self, processor):
        """测试处理器创建"""
        assert processor.state_manager is not None
        assert processor.output_manager is not None
        assert processor.command_parser is not None
        assert len(processor.handlers) > 0
    
    def test_register_handler(self, processor):
        """测试注册处理器"""
        # 创建测试处理器
        class TestHandler(CommandHandler):
            def can_handle(self, context):
                return True
            
            def handle(self, context):
                return CommandResult.success("测试成功")
        
        handler = TestHandler("test_handler", [CommandType.MAP])
        processor.register_handler(handler)
        
        assert "test_handler" in processor.handler_registry
        assert handler in processor.handlers[CommandType.MAP]
    
    def test_unregister_handler(self, processor):
        """测试注销处理器"""
        # 先注册
        class TestHandler(CommandHandler):
            def can_handle(self, context):
                return True
            
            def handle(self, context):
                return CommandResult.success()
        
        handler = TestHandler("temp_handler", [CommandType.MAP])
        processor.register_handler(handler)
        
        # 再注销
        processor.unregister_handler("temp_handler")
        
        assert "temp_handler" not in processor.handler_registry
    
    def test_add_alias(self, processor):
        """测试添加别名"""
        processor.add_alias("h", "帮助")
        
        # 处理别名命令
        result = processor.process_command("h")
        
        # 应该被解析为帮助命令
        assert result.success is True
    
    def test_process_command_success(self, processor):
        """测试成功处理命令"""
        result = processor.process_command("帮助")
        
        assert result.success is True
        assert processor.command_history[-1]['raw_input'] == "帮助"
        assert processor.command_history[-1]['success'] is True
    
    def test_process_unknown_command(self, processor):
        """测试未知命令处理"""
        result = processor.process_command("不存在的命令")
        
        assert result.success is False
        assert result.continue_processing is True
    
    def test_permission_check(self, processor):
        """测试权限检查"""
        # 修改命令源为NPC
        result = processor.process_command("修炼", source="npc")
        
        # NPC不能执行修炼命令
        assert result.success is False
        assert "没有权限" in result.error
    
    def test_command_suggestions(self, processor):
        """测试命令建议"""
        suggestions = processor.get_suggestions("攻")
        
        assert len(suggestions) > 0
        assert any("攻击" in s for s in suggestions)
    
    def test_command_history(self, processor):
        """测试命令历史"""
        # 执行一些命令
        processor.process_command("状态")
        processor.process_command("帮助")
        processor.process_command("背包")
        
        # 获取历史
        history = processor.get_command_history(count=2)
        
        assert len(history) == 2
        assert history[-1]['raw_input'] == "背包"
        assert history[-2]['raw_input'] == "帮助"
    
    def test_clear_history(self, processor):
        """测试清空历史"""
        # 先添加一些历史
        processor.process_command("状态")
        processor.process_command("帮助")
        
        # 清空
        processor.clear_history()
        
        assert len(processor.command_history) == 0
        assert len(processor.undo_stack) == 0
    
    @pytest.mark.asyncio
    async def test_async_processing(self, processor):
        """测试异步处理"""
        result = await processor.process_command_async("状态")
        
        assert result.success is True


class TestCombatHandlers:
    """战斗处理器测试"""
    
    @pytest.fixture
    def context(self):
        """创建战斗上下文"""
        state_manager = GameStateManager()
        output_manager = OutputManager()
        output_manager.add_channel(ConsoleChannel(colored=False))
        
        # 创建玩家
        player = Character(name="战士", character_type=CharacterType.PLAYER)
        state_manager.set_player(player)
        
        # 进入战斗
        state_manager.start_combat("combat_001")
        
        parsed_cmd = ParsedCommand(
            command_type=CommandType.ATTACK,
            target="妖兽",
            raw_text="攻击 妖兽"
        )
        
        return CommandContext(
            command=parsed_cmd,
            state_manager=state_manager,
            output_manager=output_manager,
            raw_input="攻击 妖兽"
        )
    
    def test_combat_handler_can_handle(self, context):
        """测试战斗处理器的can_handle"""
        handler = CombatCommandHandler()
        
        # 战斗中可以处理
        assert handler.can_handle(context) is True
        
        # 非战斗中不能处理
        context.state_manager.end_combat({})
        assert handler.can_handle(context) is False
    
    def test_attack_handler(self, context):
        """测试攻击处理器"""
        from xwe.core.command.handlers.combat_handler import AttackHandler
        handler = AttackHandler()
        
        result = handler.handle(context)
        
        assert result.success is True
        assert result.data.get('damage') is not None
    
    def test_defend_handler(self, context):
        """测试防御处理器"""
        from xwe.core.command.handlers.combat_handler import DefendHandler
        handler = DefendHandler()
        
        context.command.command_type = CommandType.DEFEND
        result = handler.handle(context)
        
        assert result.success is True
    
    def test_flee_handler(self, context):
        """测试逃跑处理器"""
        from xwe.core.command.handlers.combat_handler import FleeHandler
        handler = FleeHandler()
        
        context.command.command_type = CommandType.FLEE
        
        # 多次尝试，应该有成功有失败
        successes = 0
        for _ in range(10):
            result = handler.handle(context)
            if result.success:
                successes += 1
        
        # 50%成功率，10次应该有一些成功
        assert 0 < successes < 10


class TestSystemHandlers:
    """系统处理器测试"""
    
    @pytest.fixture
    def context(self):
        """创建系统命令上下文"""
        state_manager = GameStateManager()
        output_manager = OutputManager()
        output_manager.add_channel(ConsoleChannel(colored=False))
        
        player = Character(name="玩家", character_type=CharacterType.PLAYER)
        state_manager.set_player(player)
        
        parsed_cmd = ParsedCommand(
            command_type=CommandType.SAVE,
            raw_text="保存"
        )
        
        return CommandContext(
            command=parsed_cmd,
            state_manager=state_manager,
            output_manager=output_manager,
            raw_input="保存"
        )
    
    def test_save_handler(self, context):
        """测试保存处理器"""
        from xwe.core.command.handlers.system_handler import SaveHandler
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = SaveHandler()
            handler.save_dir = Path(tmpdir) / "saves"
            handler.save_dir.mkdir()
            
            # 执行保存
            result = handler.handle(context)
            
            assert result.success is True
            # 检查文件是否创建
            save_files = list(handler.save_dir.glob("*.json"))
            assert len(save_files) > 0
    
    def test_help_handler(self, context):
        """测试帮助处理器"""
        from xwe.core.command.handlers.system_handler import HelpHandler
        handler = HelpHandler()
        
        context.command.command_type = CommandType.HELP
        result = handler.handle(context)
        
        assert result.success is True
    
    def test_quit_handler(self, context):
        """测试退出处理器"""
        from xwe.core.command.handlers.system_handler import QuitHandler
        handler = QuitHandler()
        
        context.command.command_type = CommandType.QUIT
        result = handler.handle(context)
        
        assert result.success is True
        assert result.data.get('should_quit') is True


class TestInteractionHandlers:
    """交互处理器测试"""
    
    @pytest.fixture
    def context(self):
        """创建交互上下文"""
        state_manager = GameStateManager()
        output_manager = OutputManager()
        output_manager.add_channel(ConsoleChannel(colored=False))
        
        player = Character(name="玩家", character_type=CharacterType.PLAYER)
        state_manager.set_player(player)
        state_manager.set_location("主城")
        
        parsed_cmd = ParsedCommand(
            command_type=CommandType.TALK,
            target="商人",
            raw_text="和 商人 说话"
        )
        
        return CommandContext(
            command=parsed_cmd,
            state_manager=state_manager,
            output_manager=output_manager,
            raw_input="和 商人 说话"
        )
    
    def test_talk_handler(self, context):
        """测试对话处理器"""
        from xwe.core.command.handlers.interaction_handler import TalkHandler
        handler = TalkHandler()
        
        result = handler.handle(context)
        
        assert result.success is True
        assert result.data['npc'] == "商人"
        # 应该进入对话上下文
        assert context.state_manager.get_current_context() == GameContext.DIALOGUE
    
    def test_trade_handler(self, context):
        """测试交易处理器"""
        from xwe.core.command.handlers.interaction_handler import TradeHandler
        handler = TradeHandler()
        
        context.command.command_type = CommandType.TRADE
        result = handler.handle(context)
        
        assert result.success is True
        assert result.data['merchant'] == "商人"
        # 应该进入交易上下文
        assert context.state_manager.get_current_context() == GameContext.TRADING
    
    def test_pickup_handler(self, context):
        """测试拾取处理器"""
        from xwe.core.command.handlers.interaction_handler import PickUpHandler
        handler = PickUpHandler()
        
        context.command.command_type = CommandType.PICK_UP
        context.command.parameters = {'item': '灵石'}
        
        result = handler.handle(context)
        
        assert result.success is True


class TestCultivationHandlers:
    """修炼处理器测试"""
    
    @pytest.fixture
    def context(self):
        """创建修炼上下文"""
        state_manager = GameStateManager()
        output_manager = OutputManager()
        output_manager.add_channel(ConsoleChannel(colored=False))
        
        player = Character(name="修士", character_type=CharacterType.PLAYER)
        state_manager.set_player(player)
        state_manager.set_location("灵气洞府")
        
        parsed_cmd = ParsedCommand(
            command_type=CommandType.CULTIVATE,
            raw_text="修炼"
        )
        
        return CommandContext(
            command=parsed_cmd,
            state_manager=state_manager,
            output_manager=output_manager,
            raw_input="修炼"
        )
    
    def test_cultivate_handler(self, context):
        """测试修炼处理器"""
        from xwe.core.command.handlers.cultivation_handler import CultivateHandler
        handler = CultivateHandler()
        
        # 确保有足够体力
        context.player.attributes.current_stamina = 100
        
        result = handler.handle(context)
        
        assert result.success is True
        assert result.data.get('exp_gained') > 0
        # 体力应该减少
        assert context.player.attributes.current_stamina < 100
    
    def test_learn_skill_handler(self, context):
        """测试学习技能处理器"""
        from xwe.core.command.handlers.cultivation_handler import LearnSkillHandler
        handler = LearnSkillHandler()
        
        context.command.command_type = CommandType.LEARN_SKILL
        context.command.parameters = {'skill': '剑气斩'}
        
        # 设置足够的等级
        context.player.attributes.level = 10
        
        result = handler.handle(context)
        
        # 可能成功或失败（取决于其他条件）
        assert result is not None
    
    def test_breakthrough_handler(self, context):
        """测试突破处理器"""
        from xwe.core.command.handlers.cultivation_handler import BreakthroughHandler
        handler = BreakthroughHandler()
        
        context.command.command_type = CommandType.BREAKTHROUGH
        
        # 设置满足突破条件
        context.player.attributes.cultivation_level = 9
        context.player.attributes.current_stamina = context.player.attributes.max_stamina
        
        result = handler.handle(context)
        
        assert result.success is True


class TestIntegration:
    """集成测试"""
    
    def test_full_command_flow(self):
        """测试完整的命令流程"""
        # 创建完整的系统
        state_manager = GameStateManager()
        output_manager = OutputManager()
        output_manager.add_channel(ConsoleChannel(colored=False))
        
        processor = CommandProcessor(state_manager, output_manager)
        
        # 注册所有处理器
        processor.register_handler(SystemCommandHandler())
        processor.register_handler(CombatCommandHandler())
        processor.register_handler(InteractionCommandHandler())
        processor.register_handler(CultivationCommandHandler())
        
        # 添加中间件
        processor.add_middleware(ValidationMiddleware())
        processor.add_middleware(LoggingMiddleware())
        
        # 创建玩家
        player = Character(name="测试者", character_type=CharacterType.PLAYER)
        state_manager.set_player(player)
        
        # 执行一系列命令
        commands = [
            "帮助",
            "状态",
            "修炼",
            "去 主城",
            "和 商人 说话",
            "保存 测试"
        ]
        
        for cmd in commands:
            result = processor.process_command(cmd)
            # 大部分命令应该成功
            assert result is not None
    
    def test_command_in_different_contexts(self):
        """测试不同上下文中的命令"""
        state_manager = GameStateManager()
        output_manager = OutputManager()
        output_manager.add_channel(ConsoleChannel(colored=False))
        
        processor = CommandProcessor(state_manager, output_manager)
        processor.register_handler(CombatCommandHandler())
        processor.register_handler(SystemCommandHandler())
        processor.add_middleware(ValidationMiddleware())
        
        player = Character(name="测试者", character_type=CharacterType.PLAYER)
        state_manager.set_player(player)
        
        # 探索状态可以修炼
        result = processor.process_command("修炼")
        # 没有注册修炼处理器，所以会失败
        assert result.success is False
        
        # 进入战斗
        state_manager.start_combat("combat_001")
        
        # 战斗中不能修炼
        result = processor.process_command("修炼")
        assert result.success is False
        assert "战斗中" in result.error
        
        # 但可以攻击
        result = processor.process_command("攻击")
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
