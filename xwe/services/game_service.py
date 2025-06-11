"""
游戏服务
负责游戏的整体流程控制和协调
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import time

from . import ServiceBase, ServiceContainer
from ..events import EventBus, GameEvent


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    output: str
    state_changed: bool = False
    events: List[Dict[str, Any]] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.events is None:
            self.events = []
        if self.suggestions is None:
            self.suggestions = []


@dataclass
class GameState:
    """游戏状态"""
    initialized: bool
    in_combat: bool
    current_location: str
    game_time: float
    player_id: Optional[str] = None
    active_events: List[str] = None
    
    def __post_init__(self):
        if self.active_events is None:
            self.active_events = []


class IGameService(ABC):
    """游戏服务接口"""
    
    @abstractmethod
    def initialize_game(self, player_name: str = None) -> bool:
        """初始化游戏"""
        pass
        
    @abstractmethod
    def process_command(self, command: str) -> CommandResult:
        """处理游戏命令"""
        pass
        
    @abstractmethod
    def get_game_state(self) -> GameState:
        """获取游戏状态"""
        pass
        
    @abstractmethod
    def get_game_time(self) -> float:
        """获取游戏时间"""
        pass
        
    @abstractmethod
    def save_game(self, save_name: str) -> bool:
        """保存游戏"""
        pass
        
    @abstractmethod
    def load_game(self, save_id: str) -> bool:
        """加载游戏"""
        pass
        
    @abstractmethod
    def get_logs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """获取游戏日志"""
        pass
        
    @abstractmethod
    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取最近事件"""
        pass


class GameService(ServiceBase[IGameService], IGameService):
    """游戏服务实现"""
    
    def __init__(self, container: ServiceContainer):
        super().__init__(container)
        self._initialized = False
        self._game_start_time = 0
        self._game_time = 0
        self._in_combat = False
        self._current_location = "天南镇"
        self._logs = []
        self._events = []
        self._event_bus = None
        self._player_service = None
        self._world_service = None
        self._combat_service = None
        
    def _do_initialize(self) -> None:
        """初始化服务"""
        # 延迟导入避免循环依赖
        from .player_service import IPlayerService
        from .world_service import IWorldService
        from .combat_service import ICombatService
        
        # 获取依赖的服务
        self._player_service = self.get_service(IPlayerService)
        self._world_service = self.get_service(IWorldService)
        self._combat_service = self.get_service(ICombatService)
        
        # 创建事件总线
        self._event_bus = EventBus()
        
        # 注册事件处理器
        self._register_event_handlers()
        
    def _register_event_handlers(self) -> None:
        """注册事件处理器"""
        self._event_bus.subscribe('player_level_up', self._on_player_level_up)
        self._event_bus.subscribe('combat_start', self._on_combat_start)
        self._event_bus.subscribe('combat_end', self._on_combat_end)
        self._event_bus.subscribe('location_changed', self._on_location_changed)
        
    def initialize_game(self, player_name: str = None) -> bool:
        """初始化游戏"""
        try:
            self.logger.info("Initializing new game")
            
            # 初始化游戏时间
            self._game_start_time = time.time()
            self._game_time = 0
            
            # 创建玩家
            if player_name:
                player_id = self._player_service.create_player(player_name)
                if not player_id:
                    return False
            
            # 初始化世界
            self._world_service.initialize_world()
            
            # 设置初始位置
            self._current_location = "天南镇"
            
            # 清空日志
            self._logs.clear()
            self._events.clear()
            
            # 添加欢迎日志
            self._add_log("system", "欢迎来到修仙世界！")
            self._add_log("system", f"你现在位于{self._current_location}")
            
            self._initialized = True
            
            # 发布游戏初始化事件
            self._publish_event(GameEvent('game_initialized', {
                'location': self._current_location,
                'player_name': player_name
            }))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize game: {e}")
            return False
            
    def process_command(self, command: str) -> CommandResult:
        """处理游戏命令"""
        if not self._initialized:
            return CommandResult(
                success=False,
                output="游戏尚未初始化，请先开始游戏",
                suggestions=["开始游戏", "创建角色"]
            )
            
        self.logger.debug(f"Processing command: {command}")
        
        # 清理命令
        command = command.strip().lower()
        
        # 命令路由
        if command in ["帮助", "help", "?"]:
            return self._handle_help()
        elif command in ["状态", "status", "s"]:
            return self._handle_status()
        elif command.startswith("攻击") or command.startswith("a "):
            return self._handle_attack(command)
        elif command in ["防御", "defend", "d"]:
            return self._handle_defend()
        elif command in ["逃跑", "flee", "run"]:
            return self._handle_flee()
        elif command in ["探索", "explore", "e"]:
            return self._handle_explore()
        elif command in ["地图", "map", "m"]:
            return self._handle_map()
        elif command in ["修炼", "cultivate"]:
            return self._handle_cultivate()
        else:
            # 尝试自然语言处理
            return self._handle_natural_language(command)
            
    def _handle_help(self) -> CommandResult:
        """处理帮助命令"""
        help_text = """
=== 游戏命令帮助 ===

基础命令：
- 帮助/help/? - 显示此帮助信息
- 状态/status/s - 查看角色状态
- 地图/map/m - 查看当前位置
- 探索/explore/e - 探索当前区域

战斗命令：
- 攻击 [目标] - 攻击指定目标
- 防御/defend/d - 进入防御姿态
- 逃跑/flee/run - 尝试逃离战斗
- 使用 [技能] [目标] - 使用技能

修炼命令：
- 修炼/cultivate - 进行修炼
- 突破 - 尝试突破境界

交互命令：
- 对话 [NPC] - 与NPC对话
- 交易 [NPC] - 进行交易

系统命令：
- 保存 - 保存游戏
- 退出 - 退出游戏
"""
        self._add_log("system", help_text)
        return CommandResult(success=True, output=help_text)
        
    def _handle_status(self) -> CommandResult:
        """处理状态命令"""
        player = self._player_service.get_current_player()
        if not player:
            return CommandResult(
                success=False,
                output="未找到玩家信息"
            )
            
        status_text = f"""
=== 角色状态 ===
姓名：{player.name}
等级：{player.level}
境界：{player.realm}
生命：{player.health}/{player.max_health}
灵力：{player.mana}/{player.max_mana}
经验：{player.experience}/{player.experience_to_next}

属性：
- 攻击：{player.attack}
- 防御：{player.defense}
- 速度：{player.speed}

位置：{self._current_location}
"""
        self._add_log("info", status_text)
        return CommandResult(success=True, output=status_text)
        
    def _handle_attack(self, command: str) -> CommandResult:
        """处理攻击命令"""
        if not self._in_combat:
            return CommandResult(
                success=False,
                output="当前不在战斗中",
                suggestions=["探索", "地图"]
            )
            
        # 解析目标
        parts = command.split()
        target = parts[1] if len(parts) > 1 else None
        
        # 执行攻击
        result = self._combat_service.execute_attack(target)
        
        self._add_log("combat", result.output)
        return result
        
    def _handle_defend(self) -> CommandResult:
        """处理防御命令"""
        if not self._in_combat:
            return CommandResult(
                success=False,
                output="当前不在战斗中"
            )
            
        result = self._combat_service.execute_defend()
        self._add_log("combat", result.output)
        return result
        
    def _handle_flee(self) -> CommandResult:
        """处理逃跑命令"""
        if not self._in_combat:
            return CommandResult(
                success=False,
                output="当前不在战斗中"
            )
            
        result = self._combat_service.attempt_flee()
        self._add_log("combat", result.output)
        
        if result.success:
            self._in_combat = False
            
        return result
        
    def _handle_explore(self) -> CommandResult:
        """处理探索命令"""
        if self._in_combat:
            return CommandResult(
                success=False,
                output="战斗中无法探索",
                suggestions=["攻击", "防御", "逃跑"]
            )
            
        # 执行探索
        explore_result = self._world_service.explore_location(self._current_location)
        
        self._add_log("exploration", explore_result['description'])
        
        # 处理探索结果
        if explore_result['encounter']:
            # 遭遇事件
            if explore_result['encounter']['type'] == 'combat':
                self._start_combat(explore_result['encounter']['enemy'])
                
        return CommandResult(
            success=True,
            output=explore_result['description'],
            state_changed=True,
            events=[explore_result]
        )
        
    def _handle_map(self) -> CommandResult:
        """处理地图命令"""
        map_info = self._world_service.get_map_info(self._current_location)
        
        map_text = f"""
=== 当前位置：{self._current_location} ===
{map_info['description']}

可以前往的地点：
"""
        for location in map_info['connections']:
            map_text += f"- {location}\n"
            
        self._add_log("info", map_text)
        return CommandResult(success=True, output=map_text)
        
    def _handle_cultivate(self) -> CommandResult:
        """处理修炼命令"""
        if self._in_combat:
            return CommandResult(
                success=False,
                output="战斗中无法修炼"
            )
            
        # 执行修炼
        from .cultivation_service import ICultivationService
        cultivation_service = self.get_service(ICultivationService)
        
        result = cultivation_service.cultivate()
        self._add_log("cultivation", result['message'])
        
        return CommandResult(
            success=True,
            output=result['message'],
            state_changed=True,
            events=[result]
        )
        
    def _handle_natural_language(self, command: str) -> CommandResult:
        """处理自然语言命令"""
        # 这里可以集成NLP处理
        # 暂时返回未识别
        return CommandResult(
            success=False,
            output=f"未识别的命令：{command}",
            suggestions=["帮助", "状态", "探索", "地图"]
        )
        
    def _start_combat(self, enemy_data: Dict[str, Any]) -> None:
        """开始战斗"""
        self._in_combat = True
        self._combat_service.start_combat(enemy_data)
        
        self._publish_event(GameEvent('combat_start', {
            'enemy': enemy_data,
            'location': self._current_location
        }))
        
    def get_game_state(self) -> GameState:
        """获取游戏状态"""
        player = self._player_service.get_current_player()
        
        return GameState(
            initialized=self._initialized,
            in_combat=self._in_combat,
            current_location=self._current_location,
            game_time=self._game_time,
            player_id=player.id if player else None,
            active_events=[e['type'] for e in self._events[-5:]]
        )
        
    def get_game_time(self) -> float:
        """获取游戏时间"""
        if self._initialized:
            return time.time() - self._game_start_time + self._game_time
        return 0
        
    def save_game(self, save_name: str) -> bool:
        """保存游戏"""
        from .save_service import ISaveService
        save_service = self.get_service(ISaveService)
        
        save_data = {
            'game_state': {
                'game_time': self.get_game_time(),
                'current_location': self._current_location,
                'in_combat': self._in_combat
            },
            'player': self._player_service.get_current_player_data(),
            'world': self._world_service.get_world_data()
        }
        
        return save_service.create_save(save_name, save_data)
        
    def load_game(self, save_id: str) -> bool:
        """加载游戏"""
        from .save_service import ISaveService
        save_service = self.get_service(ISaveService)
        
        save_data = save_service.load_save(save_id)
        if not save_data:
            return False
            
        # 恢复游戏状态
        game_state = save_data.get('game_state', {})
        self._game_time = game_state.get('game_time', 0)
        self._current_location = game_state.get('current_location', '天南镇')
        self._in_combat = game_state.get('in_combat', False)
        
        # 恢复玩家数据
        self._player_service.load_player_data(save_data.get('player', {}))
        
        # 恢复世界数据
        self._world_service.load_world_data(save_data.get('world', {}))
        
        self._initialized = True
        return True
        
    def get_logs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """获取游戏日志"""
        return self._logs[offset:offset + limit]
        
    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取最近事件"""
        return self._events[-limit:]
        
    def _add_log(self, log_type: str, message: str) -> None:
        """添加日志"""
        log_entry = {
            'timestamp': time.time(),
            'type': log_type,
            'message': message
        }
        self._logs.append(log_entry)
        
        # 限制日志数量
        if len(self._logs) > 1000:
            self._logs = self._logs[-500:]
            
    def _publish_event(self, event: GameEvent) -> None:
        """发布事件"""
        self._event_bus.publish(event)
        
        # 记录事件
        event_data = {
            'id': f"evt_{int(time.time() * 1000)}",
            'type': event.type,
            'timestamp': time.time(),
            'data': event.data
        }
        self._events.append(event_data)
        
        # 限制事件数量
        if len(self._events) > 100:
            self._events = self._events[-50:]
            
    # 事件处理器
    def _on_player_level_up(self, event: GameEvent) -> None:
        """处理玩家升级事件"""
        self._add_log("achievement", f"恭喜！你升到了{event.data['new_level']}级！")
        
    def _on_combat_start(self, event: GameEvent) -> None:
        """处理战斗开始事件"""
        enemy_name = event.data.get('enemy', {}).get('name', '未知敌人')
        self._add_log("combat", f"战斗开始！你遭遇了{enemy_name}！")
        
    def _on_combat_end(self, event: GameEvent) -> None:
        """处理战斗结束事件"""
        self._in_combat = False
        result = event.data.get('result', 'unknown')
        
        if result == 'victory':
            self._add_log("combat", "战斗胜利！")
        elif result == 'defeat':
            self._add_log("combat", "战斗失败...")
        elif result == 'fled':
            self._add_log("combat", "你成功逃离了战斗")
            
    def _on_location_changed(self, event: GameEvent) -> None:
        """处理位置变更事件"""
        old_location = event.data.get('from', '未知')
        new_location = event.data.get('to', '未知')
        
        self._current_location = new_location
        self._add_log("movement", f"你从{old_location}来到了{new_location}")
