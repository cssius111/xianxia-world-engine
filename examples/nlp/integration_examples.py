#!/usr/bin/env python
"""
NLP 集成示例

演示如何将 NLP 模块集成到游戏系统中，包括：
- 与游戏引擎集成
- 与 Flask API 集成
- 实时命令处理
- 多用户支持
- 状态管理
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from xwe.core.nlp import DeepSeekNLPProcessor
from xwe.core.nlp.tool_router import register_tool, dispatch


@dataclass
class Player:
    """玩家数据模型"""
    id: str
    name: str
    level: int = 1
    location: str = "新手村"
    hp: int = 100
    mp: int = 100
    inventory: Dict[str, int] = field(default_factory=dict)
    active_quests: List[str] = field(default_factory=list)


@dataclass
class GameSession:
    """游戏会话"""
    session_id: str
    player: Player
    start_time: datetime
    command_history: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


class GameEngine:
    """简化的游戏引擎"""
    
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
        self.locations = {
            "新手村": {"连接": ["东门", "西门", "市集"]},
            "东门": {"连接": ["新手村", "野外"]},
            "野外": {"连接": ["东门", "洞府"], "怪物": ["野兔", "野狼"]},
            "洞府": {"连接": ["野外"], "特殊": "修炼场所"}
        }
    
    def create_session(self, player_id: str, player_name: str) -> GameSession:
        """创建新游戏会话"""
        player = Player(id=player_id, name=player_name)
        session = GameSession(
            session_id=f"session_{player_id}",
            player=player,
            start_time=datetime.now()
        )
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[GameSession]:
        """获取游戏会话"""
        return self.sessions.get(session_id)
    
    def move_player(self, session: GameSession, destination: str) -> Dict[str, Any]:
        """移动玩家"""
        current_loc = self.locations.get(session.player.location, {})
        connections = current_loc.get("连接", [])
        
        if destination in connections:
            session.player.location = destination
            return {
                "success": True,
                "message": f"你来到了{destination}",
                "new_location": destination
            }
        else:
            return {
                "success": False,
                "message": f"无法从{session.player.location}前往{destination}"
            }
    
    def combat(self, session: GameSession, action: str, target: str = None) -> Dict[str, Any]:
        """战斗系统"""
        if action == "attack":
            damage = 10 + session.player.level * 2
            return {
                "success": True,
                "message": f"你对{target or '敌人'}造成了{damage}点伤害",
                "damage": damage
            }
        elif action == "defend":
            return {
                "success": True,
                "message": "你进入防御姿态",
                "defense_boost": 5
            }
        else:
            return {
                "success": False,
                "message": "未知的战斗动作"
            }


class NLPGameIntegration:
    """NLP 与游戏引擎的集成层"""
    
    def __init__(self):
        self.nlp = DeepSeekNLPProcessor()
        self.engine = GameEngine()
        self._register_game_tools()
    
    def _register_game_tools(self):
        """注册游戏相关的工具"""
        
        @register_tool("game_move")
        def game_move(payload: Dict[str, Any]) -> Dict[str, Any]:
            """处理移动命令"""
            session_id = payload.get("session_id")
            destination = payload.get("destination", "")
            
            session = self.engine.get_session(session_id)
            if not session:
                return {"success": False, "message": "会话不存在"}
            
            return self.engine.move_player(session, destination)
        
        @register_tool("game_combat")
        def game_combat(payload: Dict[str, Any]) -> Dict[str, Any]:
            """处理战斗命令"""
            session_id = payload.get("session_id")
            action = payload.get("action", "attack")
            target = payload.get("target")
            
            session = self.engine.get_session(session_id)
            if not session:
                return {"success": False, "message": "会话不存在"}
            
            return self.engine.combat(session, action, target)
        
        @register_tool("game_status")
        def game_status(payload: Dict[str, Any]) -> Dict[str, Any]:
            """查看游戏状态"""
            session_id = payload.get("session_id")
            
            session = self.engine.get_session(session_id)
            if not session:
                return {"success": False, "message": "会话不存在"}
            
            player = session.player
            return {
                "success": True,
                "player_info": {
                    "name": player.name,
                    "level": player.level,
                    "location": player.location,
                    "hp": player.hp,
                    "mp": player.mp
                }
            }
    
    def process_command(self, session_id: str, raw_input: str) -> Dict[str, Any]:
        """处理玩家命令"""
        session = self.engine.get_session(session_id)
        if not session:
            return {"error": "会话不存在"}
        
        # 构建上下文
        context = {
            "player": {
                "name": session.player.name,
                "level": session.player.level,
                "location": session.player.location
            },
            "location_info": self.engine.locations.get(session.player.location, {}),
            "command_history": session.command_history[-5:]  # 最近5条历史
        }
        
        # 解析命令
        parsed = self.nlp.parse_command(raw_input, context)
        
        # 记录命令历史
        session.command_history.append({
            "time": datetime.now().isoformat(),
            "input": raw_input,
            "parsed": parsed.normalized_command,
            "intent": parsed.intent
        })
        
        # 根据意图调用相应的工具
        tool_name, payload = self._map_intent_to_tool(parsed, session_id)
        
        if tool_name:
            result = dispatch(tool_name, payload)
            return {
                "command": parsed.normalized_command,
                "intent": parsed.intent,
                "result": result
            }
        else:
            return {
                "command": parsed.normalized_command,
                "intent": parsed.intent,
                "result": {"success": False, "message": "无法理解的命令"}
            }
    
    def _map_intent_to_tool(self, parsed, session_id):
        """将解析的意图映射到具体工具"""
        intent = parsed.intent
        args = parsed.args
        
        # 基础 payload
        base_payload = {"session_id": session_id}
        
        if intent.startswith("exploration.move"):
            return "game_move", {**base_payload, "destination": args.get("destination", "")}
        elif intent.startswith("combat."):
            action = intent.split(".")[-1]
            return "game_combat", {**base_payload, "action": action, "target": args.get("target")}
        elif intent.startswith("information.status"):
            return "game_status", base_payload
        else:
            return None, None


def example_1_basic_integration():
    """示例1: 基础游戏集成"""
    print("=== 示例1: 基础游戏集成 ===\n")
    
    # 创建集成实例
    game = NLPGameIntegration()
    
    # 创建玩家会话
    session = game.engine.create_session("player1", "云逸")
    print(f"创建会话: {session.session_id}")
    print(f"玩家: {session.player.name}, 位置: {session.player.location}\n")
    
    # 测试各种命令
    commands = [
        "查看我的状态",
        "我要去东门",
        "继续前往野外",
        "攻击野狼",
        "防御",
        "去洞府修炼"
    ]
    
    for cmd in commands:
        print(f"\n玩家输入: '{cmd}'")
        result = game.process_command(session.session_id, cmd)
        
        print(f"解析意图: {result['intent']}")
        print(f"执行结果: {result['result']['message']}")
        
        if result['result']['success']:
            print(f"当前位置: {session.player.location}")


def example_2_flask_api_integration():
    """示例2: Flask API 集成"""
    print("\n\n=== 示例2: Flask API 集成 ===\n")
    
    from flask import Flask, request, jsonify
    
    # 模拟 Flask 应用
    class MockFlaskApp:
        def __init__(self):
            self.game = NLPGameIntegration()
            self.routes = {}
        
        def route(self, path, methods=['GET']):
            def decorator(func):
                self.routes[path] = func
                return func
            return decorator
        
        def process_request(self, path, data=None):
            """模拟处理请求"""
            if path in self.routes:
                return self.routes[path](data)
            return {"error": "路由不存在"}, 404
    
    app = MockFlaskApp()
    
    @app.route('/api/session', methods=['POST'])
    def create_session(data):
        """创建游戏会话"""
        player_id = data.get('player_id')
        player_name = data.get('player_name')
        
        session = app.game.engine.create_session(player_id, player_name)
        
        return {
            'session_id': session.session_id,
            'player': {
                'name': session.player.name,
                'level': session.player.level,
                'location': session.player.location
            }
        }, 200
    
    @app.route('/api/command', methods=['POST'])
    def process_command(data):
        """处理游戏命令"""
        session_id = data.get('session_id')
        command = data.get('command')
        
        if not session_id or not command:
            return {'error': '缺少必要参数'}, 400
        
        result = app.game.process_command(session_id, command)
        return result, 200
    
    # 模拟 API 调用
    print("模拟 API 调用流程:")
    
    # 1. 创建会话
    response, status = app.process_request('/api/session', {
        'player_id': 'user123',
        'player_name': '剑仙'
    })
    print(f"\n1. 创建会话 - 状态码: {status}")
    print(f"   响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    session_id = response['session_id']
    
    # 2. 发送命令
    test_commands = [
        "我想看看周围有什么",
        "去市集逛逛",
        "查看背包"
    ]
    
    for cmd in test_commands:
        response, status = app.process_request('/api/command', {
            'session_id': session_id,
            'command': cmd
        })
        print(f"\n2. 命令: '{cmd}' - 状态码: {status}")
        print(f"   响应: {json.dumps(response, ensure_ascii=False, indent=2)}")


def example_3_realtime_processing():
    """示例3: 实时命令处理"""
    print("\n\n=== 示例3: 实时命令处理 ===\n")
    
    import asyncio
    from queue import Queue
    import threading
    
    class RealtimeGameServer:
        """实时游戏服务器"""
        
        def __init__(self):
            self.game = NLPGameIntegration()
            self.command_queue = asyncio.Queue()
            self.sessions = {}
        
        async def handle_player_input(self, session_id: str, command: str):
            """处理玩家输入（异步）"""
            # 添加到命令队列
            await self.command_queue.put({
                'session_id': session_id,
                'command': command,
                'timestamp': datetime.now()
            })
        
        async def process_command_queue(self):
            """处理命令队列"""
            while True:
                try:
                    # 获取下一个命令
                    cmd_data = await asyncio.wait_for(
                        self.command_queue.get(), 
                        timeout=1.0
                    )
                    
                    # 处理命令
                    result = self.game.process_command(
                        cmd_data['session_id'],
                        cmd_data['command']
                    )
                    
                    # 模拟发送结果给客户端
                    print(f"\n[{cmd_data['timestamp'].strftime('%H:%M:%S')}] "
                          f"玩家 {cmd_data['session_id']}: {cmd_data['command']}")
                    print(f"→ {result['result']['message']}")
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"处理错误: {e}")
    
    async def simulate_multiplayer():
        """模拟多人游戏"""
        server = RealtimeGameServer()
        
        # 创建多个玩家会话
        players = [
            ("player1", "剑客"),
            ("player2", "法师"),
            ("player3", "道士")
        ]
        
        for player_id, player_name in players:
            session = server.game.engine.create_session(player_id, player_name)
            server.sessions[session.session_id] = session
        
        # 启动命令处理器
        processor_task = asyncio.create_task(server.process_command_queue())
        
        # 模拟玩家输入
        player_commands = [
            ("session_player1", "去东门"),
            ("session_player2", "查看状态"),
            ("session_player3", "去市集"),
            ("session_player1", "继续前进到野外"),
            ("session_player2", "也去东门"),
            ("session_player1", "攻击野兔"),
        ]
        
        # 发送命令
        for session_id, command in player_commands:
            await server.handle_player_input(session_id, command)
            await asyncio.sleep(0.5)  # 模拟玩家输入延迟
        
        # 等待所有命令处理完成
        await asyncio.sleep(2)
        processor_task.cancel()
    
    # 运行模拟
    print("模拟多人实时游戏:")
    asyncio.run(simulate_multiplayer())


def example_4_state_management():
    """示例4: 状态管理"""
    print("\n\n=== 示例4: 状态管理 ===\n")
    
    class StatefulGameEngine(GameEngine):
        """带状态管理的游戏引擎"""
        
        def __init__(self):
            super().__init__()
            self.world_state = {
                "time": "白天",
                "weather": "晴朗",
                "events": []
            }
        
        def save_session(self, session_id: str) -> Dict[str, Any]:
            """保存会话状态"""
            session = self.get_session(session_id)
            if not session:
                return None
            
            return {
                "session_id": session.session_id,
                "player": {
                    "id": session.player.id,
                    "name": session.player.name,
                    "level": session.player.level,
                    "location": session.player.location,
                    "hp": session.player.hp,
                    "mp": session.player.mp,
                    "inventory": dict(session.player.inventory),
                    "active_quests": list(session.player.active_quests)
                },
                "start_time": session.start_time.isoformat(),
                "command_count": len(session.command_history)
            }
        
        def load_session(self, save_data: Dict[str, Any]) -> GameSession:
            """加载会话状态"""
            player_data = save_data["player"]
            player = Player(
                id=player_data["id"],
                name=player_data["name"],
                level=player_data["level"],
                location=player_data["location"],
                hp=player_data["hp"],
                mp=player_data["mp"],
                inventory=player_data["inventory"],
                active_quests=player_data["active_quests"]
            )
            
            session = GameSession(
                session_id=save_data["session_id"],
                player=player,
                start_time=datetime.fromisoformat(save_data["start_time"])
            )
            
            self.sessions[session.session_id] = session
            return session
    
    # 使用状态管理
    engine = StatefulGameEngine()
    
    # 创建并玩一会儿
    session = engine.create_session("player1", "云游者")
    print(f"创建新会话: {session.player.name}")
    
    # 执行一些操作
    engine.move_player(session, "东门")
    session.player.level = 5
    session.player.inventory["灵石"] = 10
    session.player.active_quests.append("新手任务")
    
    print(f"\n当前状态:")
    print(f"  位置: {session.player.location}")
    print(f"  等级: {session.player.level}")
    print(f"  物品: {session.player.inventory}")
    print(f"  任务: {session.player.active_quests}")
    
    # 保存状态
    save_data = engine.save_session(session.session_id)
    print(f"\n保存状态...")
    print(f"保存数据: {json.dumps(save_data, ensure_ascii=False, indent=2)}")
    
    # 模拟重启（清空会话）
    engine.sessions.clear()
    print(f"\n模拟重启...")
    
    # 加载状态
    loaded_session = engine.load_session(save_data)
    print(f"\n加载状态成功!")
    print(f"  玩家: {loaded_session.player.name}")
    print(f"  位置: {loaded_session.player.location}")
    print(f"  等级: {loaded_session.player.level}")
    print(f"  物品: {loaded_session.player.inventory}")


def main():
    """运行所有集成示例"""
    print("修仙世界引擎 - NLP 集成示例")
    print("=" * 50)
    
    # 使用模拟模式
    os.environ["USE_MOCK_LLM"] = "true"
    
    try:
        example_1_basic_integration()
        example_2_flask_api_integration()
        example_3_realtime_processing()
        example_4_state_management()
        
        print("\n✅ 所有集成示例运行完成！")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()