"""
输出管理器测试

测试 OutputManager 的所有功能
"""

import tempfile
from datetime import datetime
from pathlib import Path
from queue import Queue
from unittest.mock import Mock, patch

import pytest

from xwe.core.output import (
    ConsoleChannel,
    FileChannel,
    HTMLChannel,
    MessagePriority,
    MessageType,
    OutputFormatter,
    OutputManager,
    OutputMessage,
    WebChannel,
)


class TestOutputMessage:
    """OutputMessage 测试"""

    def test_create_message(self):
        """测试创建消息"""
        msg = OutputMessage(
            content="测试消息", type=MessageType.COMBAT, priority=MessagePriority.HIGH
        )

        assert msg.content == "测试消息"
        assert msg.type == MessageType.COMBAT
        assert msg.priority == MessagePriority.HIGH
        assert isinstance(msg.timestamp, datetime)

    def test_message_to_dict(self):
        """测试消息序列化"""
        msg = OutputMessage(
            content="测试", type=MessageType.SYSTEM, metadata={"key": "value"}, context_id="ctx_001"
        )

        data = msg.to_dict()
        assert data["content"] == "测试"
        assert data["type"] == "system"
        assert data["metadata"]["key"] == "value"
        assert data["context_id"] == "ctx_001"


class TestConsoleChannel:
    """ConsoleChannel 测试"""

    @patch("builtins.print")
    def test_basic_output(self, mock_print):
        """测试基本输出"""
        channel = ConsoleChannel(colored=False)
        msg = OutputMessage("Hello World", MessageType.SYSTEM)

        channel.write(msg)
        mock_print.assert_called_once_with("Hello World")

    @patch("builtins.print")
    def test_colored_output(self, mock_print):
        """测试彩色输出"""
        channel = ConsoleChannel(colored=True)
        msg = OutputMessage("Error!", MessageType.ERROR)

        channel.write(msg)

        # 验证包含颜色代码
        call_args = mock_print.call_args[0][0]
        assert "\033[91m" in call_args  # 红色
        assert "\033[0m" in call_args  # 重置
        assert "[错误] Error!" in call_args

    @patch("builtins.print")
    def test_dialogue_formatting(self, mock_print):
        """测试对话格式化"""
        channel = ConsoleChannel(colored=False)
        msg = OutputMessage("你好，少侠！", MessageType.DIALOGUE, metadata={"speaker": "掌门"})

        channel.write(msg)
        mock_print.assert_called_once_with("【掌门】: 你好，少侠！")

    def test_filter(self):
        """测试过滤器"""
        channel = ConsoleChannel()

        # 添加过滤器：只输出高优先级消息
        channel.add_filter(lambda msg: msg.priority.value >= MessagePriority.HIGH.value)

        low_msg = OutputMessage("低优先级", priority=MessagePriority.LOW)
        high_msg = OutputMessage("高优先级", priority=MessagePriority.HIGH)

        assert not channel.should_output(low_msg)
        assert channel.should_output(high_msg)


class TestFileChannel:
    """FileChannel 测试"""

    def test_file_output(self):
        """测试文件输出"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "test.log"
            channel = FileChannel(log_path)

            # 写入几条消息
            msg1 = OutputMessage("第一条消息", MessageType.SYSTEM)
            msg2 = OutputMessage("第二条消息", MessageType.COMBAT)

            channel.write(msg1)
            channel.write(msg2)

            # 刷新缓冲
            channel.flush()

            # 验证文件内容
            content = log_path.read_text(encoding="utf-8")
            assert "第一条消息" in content
            assert "第二条消息" in content
            assert "[SYSTEM]" in content
            assert "[COMBAT]" in content

    def test_auto_flush(self):
        """测试自动刷新"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "test.log"
            channel = FileChannel(log_path)
            channel.buffer_size = 2  # 设置小缓冲

            # 写入超过缓冲大小的消息
            for i in range(3):
                msg = OutputMessage(f"消息{i}")
                channel.write(msg)

            # 前两条应该已经写入
            content = log_path.read_text(encoding="utf-8")
            assert "消息0" in content
            assert "消息1" in content

            # 手动刷新获取第三条
            channel.flush()
            content = log_path.read_text(encoding="utf-8")
            assert "消息2" in content


class TestHTMLChannel:
    """HTMLChannel 测试"""

    def test_html_generation(self):
        """测试HTML生成"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            html_path = Path(tmp_dir) / "test.html"
            channel = HTMLChannel(html_path, title="测试日志", auto_refresh=5)

            # 添加状态
            channel.update_status({"角色": "云游侠", "等级": 10, "生命": "100/100"})

            # 添加消息
            msg1 = OutputMessage("游戏开始", MessageType.SYSTEM)
            msg2 = OutputMessage(
                "欢迎来到修仙世界！", MessageType.DIALOGUE, metadata={"speaker": "系统"}
            )

            channel.write(msg1)
            channel.write(msg2)

            # 验证HTML文件
            assert html_path.exists()
            content = html_path.read_text(encoding="utf-8")

            # 检查基本结构
            assert "<title>测试日志</title>" in content
            assert 'content="5"' in content  # auto refresh

            # 检查状态
            assert "云游侠" in content
            assert "等级" in content
            assert "100/100" in content

            # 检查消息
            assert "游戏开始" in content
            assert "系统</span>: 欢迎来到修仙世界！" in content

    def test_message_grouping(self):
        """测试消息分组"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            html_path = Path(tmp_dir) / "test.html"
            channel = HTMLChannel(html_path)

            # 添加有相同上下文的消息
            ctx_id = "combat_001"
            msg1 = OutputMessage("战斗开始！", MessageType.COMBAT, context_id=ctx_id)
            msg2 = OutputMessage("你发起攻击", MessageType.COMBAT, context_id=ctx_id)
            msg3 = OutputMessage("造成50点伤害", MessageType.COMBAT, context_id=ctx_id)
            msg4 = OutputMessage("战斗结束", MessageType.SYSTEM)  # 不同上下文

            for msg in [msg1, msg2, msg3, msg4]:
                channel.write(msg)

            content = html_path.read_text(encoding="utf-8")

            # 应该有一个消息组
            assert "message-group" in content


class TestWebChannel:
    """WebChannel 测试"""

    def test_queue_output(self):
        """测试队列输出"""
        queue = Queue()
        channel = WebChannel(queue)

        msg = OutputMessage("测试消息", MessageType.INFO)
        channel.write(msg)

        # 验证消息在队列中
        assert not queue.empty()
        queued_msg = queue.get()
        assert queued_msg["content"] == "测试消息"
        assert queued_msg["type"] == "info"

    def test_queue_overflow(self):
        """测试队列溢出处理"""
        queue = Queue(maxsize=2)
        channel = WebChannel(queue)
        channel.max_queue_size = 2

        # 填满队列
        msg1 = OutputMessage("消息1")
        msg2 = OutputMessage("消息2")
        msg3 = OutputMessage("消息3")  # 这条应该导致最旧的被移除

        channel.write(msg1)
        channel.write(msg2)
        channel.write(msg3)

        # 验证队列内容
        items = []
        while not queue.empty():
            items.append(queue.get())

        assert len(items) == 2
        assert items[0]["content"] == "消息2"
        assert items[1]["content"] == "消息3"


class TestOutputFormatter:
    """OutputFormatter 测试"""

    def test_format_status(self):
        """测试状态格式化"""
        formatter = OutputFormatter()
        status = {"名字": "测试角色", "等级": 10, "经验": "1000/2000"}

        result = formatter.format_status(status, "角色信息")

        assert "=== 角色信息 ===" in result
        assert "名字 : 测试角色" in result
        assert "等级 : 10" in result
        assert "经验 : 1000/2000" in result

    def test_format_table(self):
        """测试表格格式化"""
        formatter = OutputFormatter()
        data = [
            {"名称": "长剑", "攻击": 10, "价格": 100},
            {"名称": "法杖", "攻击": 15, "价格": 200},
        ]

        result = formatter.format_table(data)

        # 验证表格结构
        lines = result.split("\n")
        assert len(lines) >= 4  # 表头 + 分隔线 + 2行数据
        assert "名称" in lines[0]
        assert "攻击" in lines[0]
        assert "长剑" in result
        assert "法杖" in result

    def test_format_menu(self):
        """测试菜单格式化"""
        formatter = OutputFormatter()
        options = ["攻击", "防御", "使用技能", "逃跑"]

        result = formatter.format_menu(options, "战斗选项")

        assert "=== 战斗选项 ===" in result
        assert "1. 攻击" in result
        assert "2. 防御" in result
        assert "3. 使用技能" in result
        assert "4. 逃跑" in result

    def test_format_progress(self):
        """测试进度条格式化"""
        formatter = OutputFormatter()

        # 50% 进度
        result = formatter.format_progress(50, 100)
        assert "50.0%" in result
        assert "█" in result
        assert "░" in result

        # 不显示百分比
        result = formatter.format_progress(30, 100, show_percentage=False)
        assert "30/100" in result


class TestOutputManager:
    """OutputManager 主类测试"""

    @pytest.fixture
    def manager(self):
        """创建测试用的管理器"""
        return OutputManager()

    def test_add_remove_channel(self, manager):
        """测试添加和移除通道"""
        channel = ConsoleChannel()

        # 添加通道
        manager.add_channel(channel)
        assert "console" in manager.channels
        assert manager.get_channel("console") == channel

        # 移除通道
        manager.remove_channel("console")
        assert "console" not in manager.channels

    def test_basic_output(self, manager):
        """测试基本输出"""
        # 添加模拟通道
        mock_channel = Mock(spec=ConsoleChannel)
        mock_channel.name = "test"
        manager.add_channel(mock_channel)

        # 输出消息
        manager.output("测试消息", MessageType.SYSTEM)

        # 验证通道收到消息
        mock_channel.write.assert_called_once()
        msg = mock_channel.write.call_args[0][0]
        assert msg.content == "测试消息"
        assert msg.type == MessageType.SYSTEM

    def test_convenience_methods(self, manager):
        """测试便捷方法"""
        mock_channel = Mock(spec=ConsoleChannel)
        mock_channel.name = "test"
        manager.add_channel(mock_channel)

        # 测试各种便捷方法
        manager.system("系统消息")
        manager.combat("战斗消息")
        manager.dialogue("NPC", "对话内容")
        manager.error("错误消息")
        manager.achievement("获得成就")

        # 验证调用次数
        assert mock_channel.write.call_count == 5

        # 验证对话元数据
        dialogue_call = mock_channel.write.call_args_list[2]
        msg = dialogue_call[0][0]
        assert msg.metadata["speaker"] == "NPC"

    def test_context_management(self, manager):
        """测试上下文管理"""
        # 创建上下文
        ctx = manager.create_context("ctx_001", "combat")
        assert ctx.id == "ctx_001"
        assert ctx.type == "combat"

        # 设置活动上下文
        manager.set_active_context("ctx_001")
        assert manager.active_context == "ctx_001"

        # 输出带上下文的消息
        manager.output("战斗消息", MessageType.COMBAT)

        # 验证消息被添加到上下文
        assert len(ctx.messages) == 1
        assert ctx.messages[0].content == "战斗消息"

        # 结束上下文
        manager.end_context("ctx_001")
        assert not ctx.is_active
        assert manager.active_context is None

    def test_batch_mode(self, manager):
        """测试批处理模式"""
        mock_channel = Mock(spec=ConsoleChannel)
        mock_channel.name = "test"
        manager.add_channel(mock_channel)

        # 启用批处理
        manager.enable_batch_mode(batch_size=3)

        # 输出消息（不应立即写入）
        manager.output("消息1")
        manager.output("消息2")
        assert mock_channel.write.call_count == 0

        # 第三条消息触发批处理
        manager.output("消息3")
        assert mock_channel.write.call_count == 3

        # 禁用批处理
        manager.output("消息4")
        manager.output("消息5")
        manager.disable_batch_mode()

        # 应该刷新剩余消息
        assert mock_channel.write.call_count == 5

    def test_history(self, manager):
        """测试历史记录"""
        # 输出一些消息
        manager.output("消息1", MessageType.SYSTEM)
        manager.output("消息2", MessageType.COMBAT)
        manager.output("消息3", MessageType.SYSTEM)

        # 获取历史
        history = manager.get_history(count=2)
        assert len(history) == 2
        assert history[0].content == "消息2"
        assert history[1].content == "消息3"

        # 按类型过滤
        system_history = manager.get_history(msg_type=MessageType.SYSTEM)
        assert len(system_history) == 2
        assert all(msg.type == MessageType.SYSTEM for msg in system_history)

    def test_search_history(self, manager):
        """测试历史搜索"""
        manager.output("找到宝物")
        manager.output("战斗开始")
        manager.output("找到线索")

        # 搜索包含"找到"的消息
        results = manager.search_history("找到")
        assert len(results) == 2
        assert all("找到" in msg.content for msg in results)

    def test_combat_sequence(self, manager):
        """测试战斗序列输出"""
        mock_channel = Mock(spec=ConsoleChannel)
        mock_channel.name = "test"
        manager.add_channel(mock_channel)

        actions = ["战斗开始！", "你发起攻击", "造成50点伤害", "敌人反击", "战斗胜利！"]

        manager.combat_sequence(actions)

        # 验证所有动作都被输出
        assert mock_channel.write.call_count == 5

        # 验证它们有相同的上下文
        calls = mock_channel.write.call_args_list
        context_ids = [call[0][0].context_id for call in calls]
        assert len(set(context_ids)) == 1  # 所有消息应该有相同的上下文ID

    def test_dialogue_exchange(self, manager):
        """测试对话交流输出"""
        mock_channel = Mock(spec=ConsoleChannel)
        mock_channel.name = "test"
        manager.add_channel(mock_channel)

        exchanges = [
            ("掌门", "欢迎来到青云门"),
            ("玩家", "多谢掌门"),
            ("掌门", "好好修炼，不要辜负期望"),
        ]

        manager.dialogue_exchange(exchanges)

        # 验证对话输出
        assert mock_channel.write.call_count == 3

        # 验证speaker元数据
        calls = mock_channel.write.call_args_list
        assert calls[0][0][0].metadata["speaker"] == "掌门"
        assert calls[1][0][0].metadata["speaker"] == "玩家"

    def test_formatted_outputs(self, manager):
        """测试格式化输出"""
        mock_channel = Mock(spec=ConsoleChannel)
        mock_channel.name = "test"
        manager.add_channel(mock_channel)

        # 输出状态
        status = {"生命": "100/100", "法力": "50/50"}
        manager.output_status(status)

        # 输出表格
        items = [{"名称": "剑", "价格": 100}]
        manager.output_table(items)

        # 输出进度
        manager.output_progress(50, 100, "修炼进度")

        # 输出菜单
        manager.menu(["选项1", "选项2"], "主菜单")

        # 验证所有输出
        assert mock_channel.write.call_count == 4

    def test_thread_safety(self, manager):
        """测试线程安全"""
        import threading

        mock_channel = Mock(spec=ConsoleChannel)
        mock_channel.name = "test"
        manager.add_channel(mock_channel)

        def output_messages(start, count):
            for i in range(count):
                manager.output(f"线程消息{start + i}")

        # 创建多个线程同时输出
        threads = []
        for i in range(3):
            t = threading.Thread(target=output_messages, args=(i * 10, 10))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证所有消息都被输出
        assert mock_channel.write.call_count == 30


class TestIntegration:
    """集成测试"""

    def test_multi_channel_output(self):
        """测试多通道输出"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 创建管理器和通道
            manager = OutputManager()

            # 控制台通道（使用mock）
            console = Mock(spec=ConsoleChannel)
            console.name = "console"

            # 文件通道
            log_path = Path(tmp_dir) / "game.log"
            file_channel = FileChannel(log_path)

            # HTML通道
            html_path = Path(tmp_dir) / "game.html"
            html_channel = HTMLChannel(html_path)

            # 添加所有通道
            manager.add_channel(console)
            manager.add_channel(file_channel)
            manager.add_channel(html_channel)

            # 输出各种消息
            manager.system("游戏启动")
            manager.dialogue("NPC", "欢迎！")
            manager.combat("战斗开始")
            manager.achievement("首次登录")

            # 刷新所有通道
            manager.flush_all()

            # 验证控制台
            assert console.write.call_count == 4

            # 验证文件
            log_content = log_path.read_text(encoding="utf-8")
            assert "游戏启动" in log_content
            assert "欢迎！" in log_content

            # 验证HTML
            html_content = html_path.read_text(encoding="utf-8")
            assert "游戏启动" in html_content
            assert "NPC" in html_content
            assert "首次登录" in html_content

    def test_filter_by_priority(self):
        """测试按优先级过滤"""
        manager = OutputManager()

        # 创建两个通道，一个只接收高优先级
        all_channel = Mock(spec=ConsoleChannel)
        all_channel.name = "all"

        important_channel = Mock(spec=ConsoleChannel)
        important_channel.name = "important"

        # 添加过滤器到重要通道
        def high_priority_filter(msg):
            return msg.priority.value >= MessagePriority.HIGH.value

        important_channel.should_output = Mock(side_effect=high_priority_filter)

        manager.add_channel(all_channel)
        manager.add_channel(important_channel)

        # 输出不同优先级的消息
        manager.debug("调试信息")
        manager.info("普通信息")
        manager.error("错误信息")  # HIGH priority
        manager.achievement("获得成就")  # HIGH priority

        # 验证
        assert all_channel.write.call_count == 4
        assert important_channel.write.call_count == 2  # 只有错误和成就


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
