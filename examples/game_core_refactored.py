"""
重构后的 GameCore - 使用新架构

这是一个展示如何使用新架构重构 GameCore 的示例
"""

import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from xwe.core.orchestrator import GameOrchestrator, GameConfig, GameMode
from xwe.core.state import GameStateManager, GameContext
from xwe.core.output import OutputManager
from xwe.core.command import CommandProcessor
from xwe.core.character import Character, CharacterType
from xwe.core.command.handlers.launcher_handler import GameLauncherHandler

logger = logging.getLogger(__name__)


class GameCoreRefactored:
    """
    重构后的游戏核心类
    
    使用新的模块化架构，保持与原有接口的兼容性
    """
    
    def __init__(self, config: Optional[GameConfig] = None):
        """
        初始化游戏核心
        
        Args:
            config: 游戏配置
        """
        # 使用 GameOrchestrator 作为核心
        self.orchestrator = GameOrchestrator(config or GameConfig())
        
        # 快捷访问
        self.state_manager = self.orchestrator.state_manager
        self.output_manager = self.orchestrator.output_manager
        self.command_processor = self.orchestrator.command_processor
        
        # 兼容旧接口
        self._game_state = None  # 将在初始化后设置
        self.output_buffer = []  # 兼容旧的输出缓冲
        self.current_location = None
        self.running = False
        
        logger.info("GameCore (重构版) 初始化")
    
    def initialize(self) -> None:
        """初始化游戏系统（同步接口）"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 初始化协调器
            loop.run_until_complete(self.orchestrator.initialize())
            
            # 设置兼容性属性
            self._game_state = self.orchestrator.state_manager.state
            
            # 注册额外的处理器
            self._register_handlers()
            
            # 设置钩子
            self._setup_hooks()
            
        finally:
            loop.close()
    
    def _register_handlers(self) -> None:
        """注册命令处理器"""
        # 注册启动器命令
        launcher = GameLauncherHandler(self.orchestrator)
        self.orchestrator.command_processor.register_handler(launcher)
        
        # 可以在这里注册其他自定义处理器
    
    def _setup_hooks(self) -> None:
        """设置钩子函数"""
        # 命令后处理：更新兼容性缓冲区
        def update_buffer(orchestrator, command, result):
            if hasattr(orchestrator.output_manager, 'history'):
                # 将最新的输出添加到缓冲区
                recent = orchestrator.output_manager.get_history(count=10)
                for msg in recent:
                    self.output_buffer.append(msg.content)
        
        self.orchestrator.add_post_command_hook(update_buffer)
    
    # === 兼容旧接口 ===
    
    @property
    def game_state(self):
        """兼容旧的 game_state 属性"""
        return self.orchestrator.state_manager.state if self.orchestrator.state_manager else None
    
    def output(self, text: str) -> None:
        """兼容旧的 output 方法"""
        if self.orchestrator.output_manager:
            self.orchestrator.output_manager.system(text)
        self.output_buffer.append(text)
    
    def get_output(self) -> List[str]:
        """兼容旧的 get_output 方法"""
        output = self.output_buffer.copy()
        self.output_buffer.clear()
        return output
    
    def process_command(self, command: str) -> None:
        """兼容旧的 process_command 方法"""
        if self.orchestrator.command_processor:
            result = self.orchestrator.command_processor.process_command(command)
            
            # 处理特殊结果
            if result.data.get('should_quit'):
                self.running = False
    
    def save_game(self, filename: str) -> bool:
        """兼容旧的 save_game 方法"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self.orchestrator.save_game(filename)
            )
        finally:
            loop.close()
    
    def load_game(self, filename: str) -> bool:
        """兼容旧的 load_game 方法"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self.orchestrator.load_game(filename)
            )
        finally:
            loop.close()
    
    # === 新的改进接口 ===
    
    def run(self) -> None:
        """运行游戏（新接口）"""
        self.orchestrator.run_sync()
    
    def create_character(self, name: str, **attributes) -> Character:
        """创建角色（改进的接口）"""
        character = Character(name=name, character_type=CharacterType.PLAYER)
        
        # 设置属性
        for key, value in attributes.items():
            if hasattr(character.attributes, key):
                setattr(character.attributes, key, value)
        
        # 设置为当前玩家
        self.orchestrator.state_manager.set_player(character)
        
        return character
    
    def set_location(self, location: str) -> None:
        """设置位置（改进的接口）"""
        self.orchestrator.state_manager.set_location(location)
        self.current_location = location
    
    def add_flag(self, key: str, value: Any) -> None:
        """添加游戏标记（新接口）"""
        self.orchestrator.state_manager.set_flag(key, value)
    
    def get_flag(self, key: str, default: Any = None) -> Any:
        """获取游戏标记（新接口）"""
        return self.orchestrator.state_manager.get_flag(key, default)
    
    def emit_event(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """发送事件（新接口）"""
        self.orchestrator.state_manager.emit_event(event_type, data or {})
    
    # === 示例：使用新架构实现的方法 ===
    
    def start_combat(self, enemy_name: str) -> None:
        """开始战斗（使用新架构）"""
        # 使用状态管理器
        combat_id = f"combat_{self.game_state.game_time}"
        self.orchestrator.state_manager.start_combat(combat_id)
        
        # 使用语义化输出
        self.orchestrator.output_manager.narrative(f"你遭遇了{enemy_name}！")
        self.orchestrator.output_manager.combat("⚔️ 战斗开始！")
        
        # 设置战斗数据
        self.add_flag('current_enemy', enemy_name)
        self.add_flag('combat_round', 1)
    
    def show_status(self) -> None:
        """显示状态（使用新架构）"""
        player = self.orchestrator.state_manager.get_player()
        if not player:
            self.orchestrator.output_manager.warning("还没有创建角色")
            return
        
        # 构建状态数据
        status_data = {
            "角色名": player.name,
            "等级": player.attributes.level,
            "境界": f"{player.attributes.realm_name} {player.attributes.cultivation_level}层",
            "生命": f"{int(player.attributes.current_health)}/{int(player.attributes.max_health)}",
            "法力": f"{int(player.attributes.current_mana)}/{int(player.attributes.max_mana)}",
            "体力": f"{int(player.attributes.current_stamina)}/{int(player.attributes.max_stamina)}",
            "攻击": int(player.attributes.attack_power),
            "防御": int(player.attributes.defense),
            "位置": self.orchestrator.state_manager.get_location() or "未知",
        }
        
        # 使用格式化输出
        self.orchestrator.output_manager.output_status(status_data, "角色状态")
    
    def explore_area(self) -> None:
        """探索区域（使用新架构）"""
        location = self.orchestrator.state_manager.get_location()
        
        # 使用批处理输出
        self.orchestrator.output_manager.enable_batch_mode()
        
        self.orchestrator.output_manager.narrative(f"你仔细探索着{location}...")
        
        # 模拟发现
        import random
        discoveries = []
        
        if random.random() > 0.5:
            discoveries.append({"物品": "灵草", "数量": random.randint(1, 3)})
        if random.random() > 0.7:
            discoveries.append({"物品": "灵石", "数量": random.randint(5, 15)})
        if random.random() > 0.9:
            discoveries.append({"物品": "神秘卷轴", "数量": 1})
        
        if discoveries:
            self.orchestrator.output_manager.success("你有所发现！")
            self.orchestrator.output_manager.output_table(discoveries)
            
            # 更新统计
            self.orchestrator.state_manager.update_statistics('items_found', len(discoveries))
        else:
            self.orchestrator.output_manager.info("这里似乎没有什么特别的东西。")
        
        # 结束批处理
        self.orchestrator.output_manager.disable_batch_mode()
        
        # 更新探索统计
        self.orchestrator.state_manager.update_statistics('areas_explored', 1)


def demonstrate_refactored_core():
    """演示重构后的 GameCore"""
    print("\n=== GameCore 重构演示 ===\n")
    
    # 创建配置
    config = GameConfig(
        game_name="仙侠世界 - 重构版",
        enable_html=True,
        debug_mode=True,
    )
    
    # 创建游戏核心
    game = GameCoreRefactored(config)
    
    # 初始化
    print("初始化游戏...")
    game.initialize()
    
    # 创建角色
    print("\n创建角色...")
    player = game.create_character(
        "测试仙人",
        level=5,
        max_health=200,
        max_mana=100
    )
    print(f"角色创建成功: {player.name}")
    
    # 设置位置
    game.set_location("青云山")
    
    # 使用兼容接口
    print("\n=== 测试兼容接口 ===")
    game.output("这是通过兼容接口输出的消息")
    output = game.get_output()
    print(f"从缓冲区获取: {output}")
    
    # 使用新接口
    print("\n=== 测试新接口 ===")
    
    # 显示状态
    print("\n1. 显示状态:")
    game.show_status()
    
    # 探索区域
    print("\n2. 探索区域:")
    game.explore_area()
    
    # 开始战斗
    print("\n3. 开始战斗:")
    game.start_combat("赤炎虎")
    
    # 处理命令
    print("\n4. 处理命令:")
    game.process_command("帮助")
    
    # 保存游戏
    print("\n5. 保存游戏:")
    if game.save_game("refactored_demo"):
        print("保存成功")
    
    # 事件系统
    print("\n6. 事件系统:")
    game.emit_event('custom_event', {'message': '这是自定义事件'})
    
    print("\n演示完成！")


def compare_architectures():
    """对比新旧架构"""
    print("\n=== 架构对比 ===\n")
    
    comparison = """
    旧架构 (GameCore)                    新架构 (GameOrchestrator)
    ─────────────────────────────────────────────────────────────
    
    1. 状态管理
    - 分散在各个方法中                    - 集中的 GameStateManager
    - 手动维护状态一致性                  - 自动状态同步
    - 无事件系统                         - 完整的事件系统
    
    2. 输出系统
    - 简单的 print/output                - 多通道 OutputManager
    - 纯文本输出                         - 格式化、彩色、HTML
    - 无上下文感知                       - 智能消息分组
    
    3. 命令处理
    - 大量 if-elif 链                    - 模块化 CommandProcessor
    - 难以扩展                           - 插件式架构
    - 无中间件支持                       - 完整的中间件系统
    
    4. 代码组织
    - 单一大文件                         - 模块化设计
    - 紧耦合                            - 松耦合、高内聚
    - 难以测试                          - 易于单元测试
    
    5. 扩展性
    - 修改核心代码                       - 通过处理器扩展
    - 无插件支持                         - 支持插件系统
    - 硬编码逻辑                         - 配置驱动
    """
    
    print(comparison)


def migration_guide():
    """迁移指南"""
    print("\n=== 从旧 GameCore 迁移到新架构 ===\n")
    
    steps = """
    第1步：保持兼容性
    ─────────────────
    class GameCore:
        def __init__(self):
            # 创建协调器
            self.orchestrator = GameOrchestrator()
            
        # 保留旧接口
        def output(self, text):
            self.orchestrator.output_manager.system(text)
    
    第2步：逐步替换实现
    ─────────────────
    # 旧代码
    if command == "attack":
        self.do_attack()
    
    # 新代码
    self.orchestrator.command_processor.process_command(command)
    
    第3步：利用新功能
    ─────────────────
    # 使用事件系统
    self.orchestrator.state_manager.add_listener('level_up', on_level_up)
    
    # 使用格式化输出
    self.orchestrator.output_manager.output_table(items)
    
    # 使用中间件
    self.orchestrator.command_processor.add_middleware(CustomMiddleware())
    
    第4步：完全迁移
    ─────────────────
    # 直接使用 GameOrchestrator
    game = GameOrchestrator(config)
    game.run_sync()
    """
    
    print(steps)


def main():
    """主函数"""
    print("=" * 60)
    print("GameCore 重构示例")
    print("=" * 60)
    
    options = [
        ("1", "演示重构后的 GameCore", demonstrate_refactored_core),
        ("2", "架构对比", compare_architectures),
        ("3", "迁移指南", migration_guide),
    ]
    
    print("\n请选择：")
    for num, name, _ in options:
        print(f"{num}. {name}")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请输入选项 (0-3): ").strip()
            
            if choice == "0":
                break
            
            for num, name, func in options:
                if choice == num:
                    func()
                    break
            else:
                print("无效选项")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
