"""
OutputManager 使用示例

展示如何使用新的输出管理系统
"""

from pathlib import Path
import time
from queue import Queue
from xwe.core.output import (
    OutputManager,
    ConsoleChannel,
    FileChannel,
    HTMLChannel,
    WebChannel,
    MessageType,
    MessagePriority,
    OutputFormatter
)


def example_basic_usage():
    """基础使用示例"""
    print("\n=== 基础使用示例 ===")
    
    # 创建输出管理器
    output_manager = OutputManager()
    
    # 添加控制台通道（彩色输出）
    console = ConsoleChannel(colored=True)
    output_manager.add_channel(console)
    
    # 各种类型的输出
    output_manager.system("游戏系统初始化完成")
    output_manager.narrative("你站在青云山脚下，准备开始修仙之旅...")
    output_manager.dialogue("守山弟子", "这位道友，请问有何贵干？")
    output_manager.success("成功进入青云山")
    output_manager.warning("灵力不足，无法使用高级技能")
    output_manager.error("无法读取存档文件")
    output_manager.achievement("获得成就：初入仙门")
    
    print("\n提示：如果终端支持，你应该看到不同颜色的输出")


def example_multi_channel():
    """多通道输出示例"""
    print("\n=== 多通道输出示例 ===")
    
    output_manager = OutputManager()
    
    # 添加多个输出通道
    output_manager.add_channel(ConsoleChannel(colored=False))  # 控制台
    output_manager.add_channel(FileChannel(Path("game_log.txt")))  # 文件日志
    output_manager.add_channel(HTMLChannel(Path("game_output.html"), title="游戏实况"))  # HTML
    
    # 输出会同时发送到所有通道
    output_manager.system("多通道输出测试")
    output_manager.narrative("这条消息会出现在控制台、日志文件和HTML中")
    
    # 更新HTML状态显示
    output_manager.update_status({
        "玩家": "云游侠",
        "等级": 10,
        "境界": "筑基期",
        "位置": "青云山",
        "生命": "150/150",
        "灵力": "100/100"
    })
    
    # 确保所有内容都写入
    output_manager.flush_all()
    
    print("检查生成的文件：")
    print("- game_log.txt (文本日志)")
    print("- game_output.html (可在浏览器中打开)")


def example_formatted_output():
    """格式化输出示例"""
    print("\n=== 格式化输出示例 ===")
    
    output_manager = OutputManager()
    output_manager.add_channel(ConsoleChannel())
    
    # 状态显示
    status_data = {
        "角色名": "剑尘",
        "境界": "金丹期三层",
        "攻击力": 520,
        "防御力": 380,
        "速度": 95,
        "悟性": 88,
        "福缘": 72
    }
    output_manager.output_status(status_data, "角色属性")
    
    print()  # 空行
    
    # 表格显示
    inventory_data = [
        {"物品": "回春丹", "数量": 5, "品质": "下品"},
        {"物品": "聚气丹", "数量": 3, "品质": "中品"},
        {"物品": "破障丹", "数量": 1, "品质": "上品"},
        {"物品": "灵石", "数量": 150, "品质": "标准"}
    ]
    output_manager.output_table(inventory_data, headers=["物品", "数量", "品质"])
    
    print()  # 空行
    
    # 进度条
    output_manager.output_progress(750, 1000, "修炼进度")
    output_manager.output_progress(30, 100, "任务进度")
    
    print()  # 空行
    
    # 菜单
    output_manager.menu([
        "继续修炼",
        "外出历练", 
        "拜访长老",
        "查看任务",
        "系统设置"
    ], "主菜单")


def example_combat_sequence():
    """战斗序列示例"""
    print("\n=== 战斗序列示例 ===")
    
    output_manager = OutputManager()
    output_manager.add_channel(ConsoleChannel())
    
    # 战斗开始
    output_manager.narrative("你在密林中遇到了一只三阶妖兽【赤炎虎】！")
    output_manager.combat("战斗开始！")
    
    # 使用战斗序列（相关动作会被组合）
    combat_actions = [
        "赤炎虎发出震天怒吼，气势汹汹地扑了过来！",
        "你灵巧地闪避到一旁，手中长剑泛起寒光",
        "使用技能【寒冰剑诀】！",
        "剑气呼啸而出，在赤炎虎身上留下道道冰霜",
        "造成了 285 点伤害！",
        "赤炎虎（生命：715/1000）进入【狂暴】状态！"
    ]
    
    output_manager.combat_sequence(combat_actions)
    
    # 战斗继续...
    time.sleep(0.5)  # 模拟战斗间隔
    
    output_manager.combat("赤炎虎使用技能【烈焰吐息】！")
    output_manager.warning("你受到了 120 点火焰伤害！")
    output_manager.status("当前生命值：380/500")


def example_dialogue_system():
    """对话系统示例"""
    print("\n=== 对话系统示例 ===")
    
    output_manager = OutputManager()
    output_manager.add_channel(ConsoleChannel())
    
    # 简单对话
    output_manager.narrative("你走进炼丹房，看到李长老正在炼制丹药")
    output_manager.dialogue("李长老", "哦？是你啊，来得正好。")
    output_manager.dialogue("李长老", "我这里正缺一味【千年灵芝】，你能帮我找来吗？")
    
    # 对话选项
    output_manager.menu([
        "没问题，我这就去找",
        "千年灵芝在哪里能找到？",
        "我能得到什么报酬？",
        "抱歉，我还有其他事"
    ], "选择回应")
    
    # 使用对话交流（批量对话）
    print("\n--- 完整对话示例 ---")
    
    dialogue_exchanges = [
        ("你", "李长老，千年灵芝在哪里能找到？"),
        ("李长老", "据说在后山的【灵药谷】深处有生长，但那里妖兽众多，你要小心。"),
        ("李长老", "另外，采摘灵芝需要特殊的手法，否则会损失药性。"),
        ("你", "我明白了，这就去准备。"),
        ("李长老", "很好，期待你的好消息。这是【采药手册】，会对你有帮助的。"),
    ]
    
    output_manager.dialogue_exchange(dialogue_exchanges)
    output_manager.success("获得物品：采药手册 x1")


def example_context_grouping():
    """上下文分组示例"""
    print("\n=== 上下文分组示例 ===")
    
    output_manager = OutputManager()
    output_manager.add_channel(ConsoleChannel())
    
    # 创建任务完成的上下文
    quest_ctx = output_manager.create_context("quest_001", "quest_complete")
    
    # 所有相关输出都在同一个上下文中
    output_manager.achievement("任务完成：初出茅庐", context_id="quest_001")
    output_manager.narrative("你成功完成了第一个任务，获得了长老的认可。", context_id="quest_001")
    output_manager.success("获得经验值：500", context_id="quest_001")
    output_manager.success("获得灵石：50", context_id="quest_001") 
    output_manager.success("获得物品：精铁剑 x1", context_id="quest_001")
    output_manager.system("声望提升：青云门声望 +10", context_id="quest_001")
    
    # 结束上下文
    output_manager.end_context("quest_001")
    
    print("\n提示：相关的输出会被智能分组显示")


def example_filtering():
    """消息过滤示例"""
    print("\n=== 消息过滤示例 ===")
    
    output_manager = OutputManager()
    
    # 普通控制台（显示所有）
    console_all = ConsoleChannel()
    console_all.name = "console_all"
    
    # 重要信息控制台（只显示高优先级）
    console_important = ConsoleChannel(colored=True)
    console_important.name = "console_important"
    console_important.add_filter(
        lambda msg: msg.priority.value >= MessagePriority.HIGH.value
    )
    
    # 战斗日志文件（只记录战斗信息）
    combat_log = FileChannel(Path("combat_only.log"))
    combat_log.add_filter(
        lambda msg: msg.type == MessageType.COMBAT
    )
    
    output_manager.add_channel(console_all)
    output_manager.add_channel(combat_log)
    
    print("--- 所有消息 ---")
    output_manager.debug("调试信息：加载配置文件")
    output_manager.info("普通信息：进入战斗场景")
    output_manager.combat("战斗开始！")
    output_manager.combat("你发起攻击，造成50点伤害")
    output_manager.error("错误：技能冷却中")
    output_manager.achievement("获得成就：首次战斗")
    
    # 切换到重要信息控制台
    output_manager.remove_channel("console_all")
    output_manager.add_channel(console_important)
    
    print("\n--- 只显示重要消息 ---")
    output_manager.debug("调试信息2")  # 不会显示
    output_manager.info("普通信息2")   # 不会显示
    output_manager.error("严重错误！")  # 会显示
    output_manager.achievement("重要成就！")  # 会显示
    
    output_manager.flush_all()
    print("\n检查 combat_only.log，应该只包含战斗信息")


def example_batch_mode():
    """批处理模式示例"""
    print("\n=== 批处理模式示例 ===")
    
    output_manager = OutputManager()
    output_manager.add_channel(ConsoleChannel())
    
    print("--- 普通模式（立即输出）---")
    start_time = time.time()
    for i in range(5):
        output_manager.info(f"处理项目 {i+1}/5")
        time.sleep(0.1)  # 模拟处理延迟
    
    normal_time = time.time() - start_time
    print(f"普通模式耗时：{normal_time:.2f}秒")
    
    print("\n--- 批处理模式（延迟输出）---")
    output_manager.enable_batch_mode(batch_size=5)
    
    start_time = time.time()
    for i in range(5):
        output_manager.info(f"批处理项目 {i+1}/5")
        time.sleep(0.1)  # 模拟处理延迟
    
    # 批处理会在达到批量大小时自动刷新
    batch_time = time.time() - start_time
    print(f"批处理模式耗时：{batch_time:.2f}秒")
    
    output_manager.disable_batch_mode()


def example_web_integration():
    """Web集成示例"""
    print("\n=== Web集成示例 ===")
    
    # 创建消息队列
    message_queue = Queue()
    
    # 创建输出管理器
    output_manager = OutputManager()
    output_manager.add_channel(ConsoleChannel())
    output_manager.add_channel(WebChannel(message_queue))
    
    # 输出一些消息
    output_manager.system("Web集成测试")
    output_manager.dialogue("NPC", "这条消息会被发送到Web队列")
    output_manager.achievement("测试成就")
    
    # 模拟Web端获取消息
    print("\n--- 从队列获取的消息 ---")
    while not message_queue.empty():
        msg = message_queue.get()
        print(f"Web消息: {msg['type']} - {msg['content']}")


def example_custom_formatter():
    """自定义格式化示例"""
    print("\n=== 自定义格式化示例 ===")
    
    output_manager = OutputManager()
    output_manager.add_channel(ConsoleChannel())
    
    # 使用格式化器创建复杂输出
    formatter = OutputFormatter()
    
    # 技能列表
    skills_data = [
        {"技能": "寒冰剑诀", "等级": 3, "冷却": "0秒", "消耗": "30灵力"},
        {"技能": "御剑术", "等级": 2, "冷却": "5秒", "消耗": "20灵力"},
        {"技能": "金刚护体", "等级": 1, "冷却": "0秒", "消耗": "50灵力"},
    ]
    
    skill_table = formatter.format_table(skills_data)
    output_manager.system("可用技能：")
    output_manager.info(skill_table)
    
    # 多个进度条
    print("\n--- 修炼进度 ---")
    realms = [
        ("炼气期", 100, 100),
        ("筑基期", 80, 100),
        ("金丹期", 15, 100),
        ("元婴期", 0, 100)
    ]
    
    for realm, current, total in realms:
        progress = formatter.format_progress(current, total, width=15)
        output_manager.status(f"{realm}: {progress}")


def example_history_search():
    """历史记录和搜索示例"""
    print("\n=== 历史记录和搜索示例 ===")
    
    output_manager = OutputManager()
    output_manager.add_channel(ConsoleChannel())
    
    # 输出一些消息
    messages = [
        ("在青云山找到了灵草", MessageType.SYSTEM),
        ("战胜了妖兽获得100经验", MessageType.COMBAT),
        ("找到隐藏的宝箱", MessageType.SUCCESS),
        ("妖兽掉落了稀有材料", MessageType.COMBAT),
        ("在洞穴中找到了秘籍", MessageType.SUCCESS),
    ]
    
    for content, msg_type in messages:
        output_manager.output(content, msg_type)
    
    # 搜索包含"找到"的消息
    print("\n--- 搜索结果：包含'找到'的消息 ---")
    results = output_manager.search_history("找到")
    for msg in results:
        print(f"[{msg.type.value}] {msg.content}")
    
    # 获取战斗历史
    print("\n--- 战斗历史 ---")
    combat_history = output_manager.get_history(msg_type=MessageType.COMBAT)
    for msg in combat_history:
        print(f"⚔️  {msg.content}")


def main():
    """运行所有示例"""
    examples = [
        ("基础使用", example_basic_usage),
        ("多通道输出", example_multi_channel),
        ("格式化输出", example_formatted_output),
        ("战斗序列", example_combat_sequence),
        ("对话系统", example_dialogue_system),
        ("上下文分组", example_context_grouping),
        ("消息过滤", example_filtering),
        ("批处理模式", example_batch_mode),
        ("Web集成", example_web_integration),
        ("自定义格式化", example_custom_formatter),
        ("历史记录搜索", example_history_search),
    ]
    
    print("OutputManager 功能演示")
    print("=" * 50)
    
    for name, example_func in examples:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            example_func()
            time.sleep(0.5)  # 暂停一下，便于观察
        except Exception as e:
            print(f"示例 {name} 出错: {e}")
    
    print("\n" + "="*50)
    print("所有示例运行完成！")
    print("\n生成的文件：")
    print("- game_log.txt")
    print("- game_output.html") 
    print("- combat_only.log")


if __name__ == "__main__":
    main()
