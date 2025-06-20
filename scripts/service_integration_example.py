# @dev_only
"""
服务层集成示例
展示如何在Flask应用中使用新的服务架构
"""

from typing import Any, Dict

from flask import Flask, jsonify, request, session

from xwe.services import ServiceContainer, get_service_container, register_services
from xwe.services.game_service import IGameService
from xwe.services.interfaces.player_service import IPlayerService


def create_app_with_services() -> Flask:
    """
    创建带有服务层的Flask应用
    """
    app = Flask(__name__)
    app.secret_key = "xianxia-world-engine-secret"

    # 创建并初始化服务容器
    container = get_service_container()
    register_services(container)

    # 将容器保存到app上下文
    app.service_container = container

    return app


def integrate_services_with_api(app: Flask):
    """
    将服务层与现有API集成
    """
    container = app.service_container

    # 修改现有的API端点以使用服务

    @app.route("/api/v1/game/initialize", methods=["POST"])
    def initialize_game_with_service():
        """使用服务层的游戏初始化"""
        game_service = container.resolve(IGameService)

        # 从请求获取玩家名称
        data = request.get_json() or {}
        player_name = data.get("player_name")

        # 初始化游戏
        success = game_service.initialize_game(player_name)

        if success:
            # 保存到session
            session["game_initialized"] = True

            return jsonify(
                {
                    "success": True,
                    "data": {"message": "游戏初始化成功", "player_created": bool(player_name)},
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"code": "INIT_FAILED", "message": "游戏初始化失败"},
                    }
                ),
                500,
            )

    @app.route("/api/v1/game/command", methods=["POST"])
    def execute_command_with_service():
        """使用服务层执行命令"""
        game_service = container.resolve(IGameService)

        # 检查游戏是否初始化
        if not session.get("game_initialized"):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"code": "NOT_INITIALIZED", "message": "游戏尚未初始化"},
                    }
                ),
                400,
            )

        # 获取命令
        data = request.get_json() or {}
        command = data.get("command", "").strip()

        if not command:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {"code": "INVALID_REQUEST", "message": "命令不能为空"},
                    }
                ),
                400,
            )

        # 执行命令
        result = game_service.process_command(command)

        return jsonify(
            {
                "success": result.success,
                "data": {
                    "command": command,
                    "result": result.output,
                    "state_changed": result.state_changed,
                    "events": result.events,
                    "suggestions": result.suggestions,
                },
            }
        )

    @app.route("/api/v1/game/status", methods=["GET"])
    def get_game_status_with_service():
        """使用服务层获取游戏状态"""
        game_service = container.resolve(IGameService)
        player_service = container.resolve(IPlayerService)

        # 获取游戏状态
        game_state = game_service.get_game_state()

        # 获取玩家信息
        player_data = None
        if game_state.player_id:
            player = player_service.get_current_player()
            if player:
                player_data = {
                    "name": player.name,
                    "level": player.level,
                    "realm": player.realm,
                    "health": {"current": player.health, "max": player.max_health},
                    "mana": {"current": player.mana, "max": player.max_mana},
                    "experience": {
                        "current": player.experience,
                        "required": player.experience_to_next,
                    },
                }

        return jsonify(
            {
                "success": True,
                "data": {
                    "initialized": game_state.initialized,
                    "in_combat": game_state.in_combat,
                    "current_location": game_state.current_location,
                    "game_time": game_state.game_time,
                    "player": player_data,
                },
            }
        )


# 示例：更新现有的run_web_ui_optimized.py
def example_migration():
    """
    展示如何迁移现有代码到服务架构
    """
    print(
        """
    === 迁移步骤 ===

    1. 在你的主文件中导入服务：
    ```python
    from xwe.services import ServiceContainer, register_services
    ```

    2. 创建服务容器并注册服务：
    ```python
    # 在app创建后
    container = ServiceContainer()
    register_services(container)
    app.service_container = container
    ```

    3. 替换直接的游戏逻辑调用：

    旧代码：
    ```python
    game = GameEngine()
    game.process_command(command)
    ```

    新代码：
    ```python
    game_service = container.resolve(IGameService)
    result = game_service.process_command(command)
    ```

    4. 使用服务间通信：
    ```python
    # 在一个服务中获取另一个服务
    player_service = self.get_service(IPlayerService)
    player = player_service.get_current_player()
    ```

    5. 利用事件系统：
    ```python
    from xwe.events import subscribe_event

    # 订阅玩家升级事件
    subscribe_event('player_level_up', handle_level_up)
    ```
    """
    )


# 测试服务层
def test_services():
    """测试服务层功能"""
    print("测试服务层...")

    # 创建容器
    container = ServiceContainer()
    register_services(container)

    # 获取游戏服务
    game_service = container.resolve(IGameService)

    # 初始化游戏
    print("初始化游戏...")
    success = game_service.initialize_game("测试玩家")
    print(f"初始化结果: {success}")

    # 执行一些命令
    commands = ["帮助", "状态", "探索", "地图"]

    for cmd in commands:
        print(f"\n执行命令: {cmd}")
        result = game_service.process_command(cmd)
        print(f"结果: {result.output[:100]}...")

    # 获取游戏状态
    state = game_service.get_game_state()
    print(f"\n游戏状态: {state}")

    # 关闭所有服务
    container.shutdown_all()
    print("\n服务测试完成！")


if __name__ == "__main__":
    # 运行测试
    test_services()

    # 显示集成示例
    print("\n" + "=" * 50)
    example_migration()
