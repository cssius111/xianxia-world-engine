#!/usr/bin/env python3
"""
修仙世界引擎 Web UI 启动器 v2.0
优化版本，包含完整的错误处理、性能监控和开发者工具
"""

import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.exceptions import HTTPException

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 导入项目模块
try:
    from api import register_api
    from routes import character, intel, lore
    from xwe.core.cultivation_system import CultivationSystem
    from xwe.core.game_core import create_enhanced_game
    from xwe.features.ai_personalization import AIPersonalization
    from xwe.features.community_system import CommunitySystem
    from xwe.features.narrative_system import NarrativeSystem
    from xwe.features.technical_ops import TechnicalOps
    from xwe.core.attributes import CharacterAttributes
    from xwe.core.character import Character, CharacterType
    from game_config import config
except ImportError as e:
    print(f"错误：无法导入必要模块 - {e}")
    print("请确保所有依赖都已正确安装")
    sys.exit(1)


class XianxiaWebServer:
    """修仙世界引擎Web服务器类"""
    
    def __init__(self):
        self.app = None
        self.game_instances: Dict[str, Dict[str, Any]] = {}
        self.logger = None
        self.setup_logging()
        self.setup_flask_app()
        self.setup_routes()
        
    def setup_logging(self):
        """设置日志系统"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 配置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 创建日志器
        self.logger = logging.getLogger('XianxiaEngine')
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            log_dir / f"game_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("日志系统初始化完成")
    
    def setup_flask_app(self):
        """设置Flask应用"""
        # 使用项目根目录下的模板和静态文件
        templates_path = PROJECT_ROOT / "templates"
        static_path = PROJECT_ROOT / "static"
        
        self.app = Flask(
            __name__,
            template_folder=str(templates_path),
            static_folder=str(static_path)
        )
        
        # 配置应用
        self.app.config.update({
            'SECRET_KEY': os.getenv('FLASK_SECRET_KEY', 'xianxia_world_secret_key_2025'),
            'DEBUG': config.debug_mode,
            'JSON_AS_ASCII': False,  # 支持中文JSON
            'SEND_FILE_MAX_AGE_DEFAULT': 31536000 if not config.debug_mode else 0,  # 生产环境缓存静态文件
        })
        
        # 注册API和蓝图
        try:
            register_api(self.app)
            self.app.register_blueprint(lore.bp)
            self.app.register_blueprint(character.bp)
            self.app.register_blueprint(intel.bp)
            self.logger.info("API和蓝图注册完成")
        except Exception as e:
            self.logger.error(f"注册API失败: {e}")
            
        # 设置错误处理
        self.setup_error_handlers()
        
        # 设置请求前后处理
        self.setup_request_handlers()
    
    def setup_error_handlers(self):
        """设置错误处理器"""
        
        @self.app.errorhandler(Exception)
        def handle_exception(e):
            # 记录异常
            self.logger.error(f"未处理的异常: {str(e)}\n{traceback.format_exc()}")
            
            if isinstance(e, HTTPException):
                # 返回HTTP异常的原始响应
                response = e.get_response()
                response.data = json.dumps({
                    "error": e.description,
                    "code": e.code
                }, ensure_ascii=False)
                response.content_type = "application/json"
                return response
            
            # 非HTTP异常
            if self.app.config['DEBUG']:
                return jsonify({
                    "error": "内部服务器错误",
                    "debug": str(e),
                    "traceback": traceback.format_exc()
                }), 500
            else:
                return jsonify({
                    "error": "服务器内部错误，请稍后重试"
                }), 500
    
    def setup_request_handlers(self):
        """设置请求处理器"""
        
        @self.app.before_request
        def before_request():
            # 记录请求信息（仅在调试模式）
            if self.app.config['DEBUG'] and request.endpoint not in ['static']:
                self.logger.debug(f"请求: {request.method} {request.path}")
            
            # 清理过期的游戏实例
            self.cleanup_old_instances()
        
        @self.app.after_request
        def after_request(response):
            # 添加CORS头（如果需要）
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.route("/")
        def index():
            """主页面 - 重定向到欢迎页面"""
            return redirect(url_for('welcome'))

        @self.app.route("/welcome")
        def welcome():
            """欢迎页面"""
            try:
                # 检查是否有存档
                save_exists = (Path("saves") / "autosave.json").exists()
                return render_template("welcome_optimized.html", 
                                     save_exists=save_exists,
                                     build_time=datetime.now().strftime('%Y.%m.%d'))
            except Exception as e:
                self.logger.error(f"加载欢迎页面失败: {e}")
                return "页面加载失败", 500

        @self.app.route("/intro")
        def intro():
            """角色创建介绍页面"""
            try:
                if "session_id" not in session:
                    session["session_id"] = self.generate_session_id()
                
                dev_mode = request.args.get('mode') == 'dev'
                return render_template("intro_optimized.html", dev_mode=dev_mode)
            except Exception as e:
                self.logger.error(f"加载介绍页面失败: {e}")
                return "页面加载失败", 500

        @self.app.route("/game")
        def game():
            """游戏主界面"""
            try:
                # 确保会话ID
                if "session_id" not in session:
                    session["session_id"] = self.generate_session_id()
                    session["is_new_session"] = True
                else:
                    session["is_new_session"] = False

                # 获取游戏实例
                instance = self.get_game_instance(session["session_id"])
                game_obj = instance["game"]
                player = game_obj.game_state.player
                
                # 检查开发模式
                dev_mode = request.args.get('mode') == 'dev' or session.get('dev_mode', False)
                if dev_mode:
                    session['dev_mode'] = True
                    self.logger.info(f"[DEV] 开发模式访问游戏页面，会话ID: {session['session_id']}")

                # 渲染模板 - 使用新的优化模板
                return render_template(
                    "game_enhanced_optimized_v2.html",
                    player=player,
                    location=game_obj.game_state.current_location,
                    buffs=[],
                    special_status=[],
                    is_new_session=session.get("is_new_session", False),
                    dev_mode=dev_mode,
                )
            except Exception as e:
                self.logger.error(f"加载游戏页面失败: {e}")
                return f"游戏加载失败: {str(e)}", 500

        @self.app.route("/command", methods=["POST"])
        def process_command():
            """处理游戏命令"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "无效的请求数据"}), 400
                
                command = data.get("command", "").strip()
                if not command:
                    return jsonify({"error": "命令不能为空"}), 400

                if "session_id" not in session:
                    return jsonify({"error": "会话已过期，请刷新页面"}), 401

                instance = self.get_game_instance(session["session_id"])
                game_obj = instance["game"]
                
                # 开发模式日志
                if session.get('dev_mode', False):
                    self.logger.info(f"[DEV] 处理命令: {command}, 会话: {session['session_id']}")

                # 处理命令
                result = game_obj.process_command(command)
                
                # 标记需要刷新
                instance["need_refresh"] = True
                instance["last_update"] = time.time()

                return jsonify({"success": True, "result": result})
                
            except Exception as e:
                self.logger.error(f"处理命令失败: {e}")
                return jsonify({"error": "命令处理失败"}), 500

        @self.app.route("/status")
        def get_status():
            """获取游戏状态"""
            try:
                if "session_id" not in session:
                    return jsonify({"error": "会话已过期"}), 401

                instance = self.get_game_instance(session["session_id"])
                game_obj = instance["game"]
                player = game_obj.game_state.player

                status_data = {
                    "player": None,
                    "location": game_obj.game_state.current_location,
                    "location_name": game_obj.game_state.current_location,
                    "gold": 0,
                    "timestamp": time.time()
                }

                if player:
                    status_data["player"] = {
                        "name": player.name,
                        "attributes": {
                            "realm_name": getattr(player.attributes, 'realm_name', '炼气期'),
                            "realm_level": getattr(player.attributes, 'realm_level', 1),
                            "cultivation_level": getattr(player.attributes, 'cultivation_level', 0),
                            "max_cultivation": getattr(player.attributes, 'max_cultivation', 100),
                            "realm_progress": getattr(player.attributes, 'realm_progress', 0),
                            "current_health": getattr(player.attributes, 'current_health', 100),
                            "max_health": getattr(player.attributes, 'max_health', 100),
                            "current_mana": getattr(player.attributes, 'current_mana', 50),
                            "max_mana": getattr(player.attributes, 'max_mana', 50),
                            "current_stamina": getattr(player.attributes, 'current_stamina', 100),
                            "max_stamina": getattr(player.attributes, 'max_stamina', 100),
                            "attack_power": getattr(player.attributes, 'attack_power', 10),
                            "defense": getattr(player.attributes, 'defense', 5),
                            "speed": getattr(player.attributes, 'speed', 10),
                        },
                        "extra_data": getattr(player, "extra_data", {}),
                    }

                    # 获取金币数量
                    if hasattr(player, "inventory") and hasattr(player.inventory, "gold"):
                        status_data["gold"] = player.inventory.gold

                return jsonify(status_data)
                
            except Exception as e:
                self.logger.error(f"获取状态失败: {e}")
                return jsonify({"error": "获取状态失败"}), 500

        @self.app.route("/log")
        def get_log():
            """获取游戏日志"""
            try:
                if "session_id" not in session:
                    return jsonify({"logs": []})

                instance = self.get_game_instance(session["session_id"])
                game_obj = instance["game"]

                # 限制日志数量，避免传输过多数据
                logs = game_obj.game_state.logs[-100:]
                
                return jsonify({
                    "logs": logs,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                self.logger.error(f"获取日志失败: {e}")
                return jsonify({"logs": [], "error": str(e)})

        @self.app.route("/need_refresh")
        def need_refresh():
            """检查是否需要刷新"""
            try:
                if "session_id" not in session:
                    return jsonify({"refresh": False})

                instance = self.get_game_instance(session["session_id"])
                need_refresh = instance.get("need_refresh", False)
                last_update = instance.get("last_update", 0)

                # 重置标记
                if need_refresh:
                    instance["need_refresh"] = False

                return jsonify({
                    "refresh": need_refresh,
                    "last_update": last_update
                })
                
            except Exception as e:
                self.logger.error(f"检查刷新失败: {e}")
                return jsonify({"refresh": False})

        @self.app.route("/save_game", methods=["POST"])
        def save_game():
            """保存游戏"""
            try:
                if "session_id" not in session:
                    return jsonify({"success": False, "error": "会话已过期"}), 401

                instance = self.get_game_instance(session["session_id"])
                game_obj = instance["game"]

                if hasattr(game_obj, "technical_ops"):
                    game_obj.technical_ops.save_game(game_obj.game_state)
                    self.logger.info(f"游戏保存成功，会话: {session['session_id']}")
                    return jsonify({"success": True, "message": "游戏已保存"})
                else:
                    return jsonify({"success": False, "error": "保存系统未初始化"})
                    
            except Exception as e:
                self.logger.error(f"保存游戏失败: {e}")
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/load_game", methods=["POST"])
        def load_game():
            """加载游戏"""
            try:
                if "session_id" not in session:
                    return jsonify({"success": False, "error": "会话已过期"}), 401

                instance = self.get_game_instance(session["session_id"])
                game_obj = instance["game"]

                if hasattr(game_obj, "technical_ops"):
                    loaded_state = game_obj.technical_ops.load_game()
                    if loaded_state:
                        game_obj.game_state = loaded_state
                        instance["need_refresh"] = True
                        self.logger.info(f"游戏加载成功，会话: {session['session_id']}")
                        return jsonify({"success": True, "message": "游戏已加载"})
                    else:
                        return jsonify({"success": False, "error": "没有找到存档"})
                else:
                    return jsonify({"success": False, "error": "加载系统未初始化"})
                    
            except Exception as e:
                self.logger.error(f"加载游戏失败: {e}")
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/create_character", methods=["POST"])
        def create_character():
            """创建角色"""
            try:
                if "session_id" not in session:
                    session["session_id"] = self.generate_session_id()
                
                data = request.get_json()
                if not data:
                    return jsonify({"success": False, "error": "无效的角色数据"}), 400

                instance = self.get_game_instance(session["session_id"])
                game_obj = instance["game"]
                
                # 创建新角色
                if game_obj.game_state.player:
                    player = game_obj.game_state.player
                    player.name = data.get('name', '无名侠客')
                    
                    # 初始化extra_data
                    if not hasattr(player, 'extra_data') or player.extra_data is None:
                        player.extra_data = {}
                    
                    # 根据选择的模式设置属性
                    character_type = data.get('type', 'random')
                    if character_type == 'sword':  # 剑修
                        player.attributes.attack_power += 5
                        player.attributes.defense = max(1, player.attributes.defense - 2)
                        player.extra_data.update({'faction': '剑宗', 'spiritual_root': '金'})
                    elif character_type == 'body':  # 体修
                        player.attributes.defense += 5
                        player.attributes.speed = max(1, getattr(player.attributes, 'speed', 10) - 2)
                        player.extra_data.update({'faction': '炼体宗', 'spiritual_root': '土'})
                    elif character_type == 'magic':  # 法修
                        player.attributes.max_mana += 20
                        player.attributes.current_mana += 20
                        player.attributes.max_health = max(10, player.attributes.max_health - 10)
                        player.extra_data.update({'faction': '玄天宗', 'spiritual_root': '水'})
                    
                    # 重新计算衍生属性
                    if hasattr(player.attributes, 'calculate_derived_attributes'):
                        player.attributes.calculate_derived_attributes()
                    
                    self.logger.info(f"角色创建成功: {player.name}, 类型: {character_type}")
                    
                instance["need_refresh"] = True
                return jsonify({"success": True})
                
            except Exception as e:
                self.logger.error(f"创建角色失败: {e}")
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/modal/<modal_name>")
        def load_modal(modal_name):
            """加载模态框内容"""
            try:
                # 白名单验证
                allowed_modals = [
                    'status', 'inventory', 'cultivation', 'achievement', 
                    'exploration', 'map', 'quest', 'save', 'load', 
                    'help', 'settings', 'exit'
                ]
                
                if modal_name not in allowed_modals:
                    return "无效的模态框", 404
                
                # 获取当前游戏状态
                player = None
                game_obj = None
                if "session_id" in session:
                    try:
                        instance = self.get_game_instance(session["session_id"])
                        game_obj = instance["game"]
                        player = game_obj.game_state.player
                    except Exception:
                        pass  # 忽略游戏状态获取错误
                
                # 加载模态框模板
                return render_template(f"modals/{modal_name}.html", player=player, game=game_obj)
                
            except Exception as e:
                self.logger.error(f"加载模态框失败: {modal_name}, 错误: {e}")
                return f"<h3>{modal_name.title()}</h3><p>功能暂时不可用，请稍后重试。</p>"

        @self.app.route("/get_audio_list")
        def get_audio_list():
            """获取音频文件列表"""
            try:
                audio_dir = Path("static/audio")
                audio_files = []
                
                if audio_dir.exists():
                    # 递归查找所有子目录中的音频文件
                    audio_extensions = ['.mp3', '.ogg', '.wav']
                    for ext in audio_extensions:
                        audio_files.extend([f.name for f in audio_dir.rglob(f"*{ext}")])
                
                return jsonify({"files": audio_files})
            except Exception as e:
                self.logger.error(f"获取音频列表失败: {e}")
                return jsonify({"files": []})

        @self.app.route("/sw.js")
        def service_worker():
            """服务工作者文件"""
            try:
                sw_path = Path("static/sw.js")
                if sw_path.exists():
                    return self.app.send_static_file('sw.js'), 200, {
                        'Content-Type': 'application/javascript',
                        'Cache-Control': 'no-cache'
                    }
                else:
                    return "Service Worker not found", 404
            except Exception as e:
                self.logger.error(f"加载服务工作者失败: {e}")
                return "Service Worker error", 500

        # 开发模式专用路由
        if config.debug_mode:
            @self.app.route("/dev/stats")
            def dev_stats():
                """开发模式：服务器统计"""
                return jsonify({
                    "active_sessions": len(self.game_instances),
                    "uptime": time.time() - getattr(self, 'start_time', time.time()),
                    "config": {
                        "debug_mode": config.debug_mode,
                        "version": config.version
                    }
                })
            
            @self.app.route("/dev/cache_info")
            def dev_cache_info():
                """开发模式：缓存信息"""
                return jsonify({
                    "cache_enabled": True,
                    "service_worker_available": True,
                    "static_files_count": len(list(Path("static").rglob("*"))),
                    "template_files_count": len(list(Path("templates").rglob("*.html")))
                })

    def generate_session_id(self) -> str:
        """生成唯一的会话ID"""
        return f"{int(time.time() * 1000)}_{os.urandom(8).hex()}"

    def get_game_instance(self, session_id: str) -> Dict[str, Any]:
        """获取或创建游戏实例"""
        if session_id not in self.game_instances:
            try:
                # 创建新游戏实例
                game_mode = os.getenv("GAME_MODE", "player")
                game = create_enhanced_game(game_mode=game_mode)

                # 初始化各系统
                game.cultivation_system = CultivationSystem()
                game.narrative_system = NarrativeSystem()
                game.ai_personalization = AIPersonalization()
                game.community_system = CommunitySystem()
                game.technical_ops = TechnicalOps()

                # 创建玩家
                if not game.game_state.player:
                    attrs = CharacterAttributes()
                    attrs.realm_name = "炼气期"
                    attrs.realm_level = 1
                    attrs.level = 1
                    attrs.cultivation_level = 0
                    attrs.max_cultivation = 100
                    attrs.realm_progress = 0

                    # 使用配置的基础属性值
                    attrs.current_health = config.max_health
                    attrs.max_health = config.max_health
                    attrs.current_mana = 50
                    attrs.max_mana = 50
                    attrs.current_stamina = 100
                    attrs.max_stamina = 100
                    attrs.attack_power = int(config.base_damage)
                    attrs.defense = 5

                    player = Character(
                        id="player", 
                        name="无名侠客", 
                        character_type=CharacterType.PLAYER, 
                        attributes=attrs
                    )
                    game.game_state.player = player
                    game.game_state.current_location = "青云城"
                    game.game_state.logs = []

                self.game_instances[session_id] = {
                    "game": game,
                    "last_update": time.time(),
                    "need_refresh": True,
                    "created_at": time.time()
                }
                
                self.logger.info(f"创建新游戏实例，会话ID: {session_id}")
                
            except Exception as e:
                self.logger.error(f"创建游戏实例失败: {e}")
                raise

        # 更新最后访问时间
        self.game_instances[session_id]["last_update"] = time.time()
        return self.game_instances[session_id]

    def cleanup_old_instances(self):
        """清理超时的游戏实例"""
        current_time = time.time()
        timeout = 3600  # 1小时超时

        to_remove = []
        for session_id, instance in self.game_instances.items():
            if current_time - instance["last_update"] > timeout:
                to_remove.append(session_id)

        for session_id in to_remove:
            try:
                # 尝试自动保存
                instance = self.game_instances[session_id]
                if hasattr(instance["game"], "technical_ops"):
                    instance["game"].technical_ops.save_game(instance["game"].game_state)
                self.logger.info(f"清理过期会话并自动保存: {session_id}")
            except Exception as e:
                self.logger.warning(f"清理会话时保存失败: {session_id}, 错误: {e}")
            finally:
                del self.game_instances[session_id]

    def run(self, host: str = "0.0.0.0", port: int = 5001, debug: Optional[bool] = None):
        """启动服务器"""
        if debug is None:
            debug = config.debug_mode
            
        # 确保必要目录存在
        for directory in ["saves", "logs", "static/audio"]:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # 记录启动时间
        self.start_time = time.time()
        
        # 打印启动信息
        print("=" * 60)
        print(f"🎮 修仙世界引擎 Web UI v{config.version} (水墨风传奇版)")
        print("=" * 50)
        print(f"🌐 访问地址: http://localhost:{port}")
        print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
        print(f"📝 日志目录: {Path('logs').absolute()}")
        print(f"💾 存档目录: {Path('saves').absolute()}")
        print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print("使用 Ctrl+C 停止服务器")
        print("🌊 特色：水墨风界面、PWA支持、离线游戏")
        if debug:
            print("🔧 开发模式已启用，访问 /dev/stats 查看统计信息")
        print("=" * 50)
        
        self.logger.info(f"服务器启动，监听 {host}:{port}")
        
        try:
            self.app.run(
                debug=debug,
                host=host,
                port=port,
                threaded=True,
                use_reloader=False  # 避免重载器在生产环境中的问题
            )
        except KeyboardInterrupt:
            self.logger.info("服务器被用户中断")
        except Exception as e:
            self.logger.error(f"服务器启动失败: {e}")
            raise
        finally:
            self.logger.info("服务器关闭")


def main():
    """主函数"""
    server = XianxiaWebServer()
    server.run()


if __name__ == "__main__":
    main()
