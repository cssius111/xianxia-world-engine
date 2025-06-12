"""
第4阶段功能集成示例
展示如何集成监控、日志和调试功能
"""

from flask import Flask, request
from xwe.services.log_service import StructuredLogger
from xwe.metrics import metrics_registry, inc_counter, time_histogram
from xwe.config import config, configure_logging
from api import register_api
import time
import uuid

# 创建Flask应用
app = Flask(__name__)

# 使用配置系统
app.config.from_object(config)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['ENABLE_DEV_API'] = config.ENABLE_DEV_API

# 配置日志系统
configure_logging(app)

# 创建结构化日志记录器
logger = StructuredLogger(service_name="xwe_main")

# 注册API（包含新的监控和文档功能）
register_api(app)

# 添加请求监控中间件
@app.before_request
def before_request():
    """记录请求开始"""
    request.start_time = time.time()
    request.trace_id = str(uuid.uuid4())
    
    # 设置logger的trace_id
    logger.set_trace_id(request.trace_id)
    
    logger.info("Request started", 
                method=request.method, 
                path=request.path,
                ip=request.remote_addr)

@app.after_request
def after_request(response):
    """记录请求指标"""
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        
        # 记录HTTP请求指标
        metrics_registry.observe_histogram(
            "http_request_duration_seconds",
            duration,
            {
                "method": request.method,
                "path": request.path,
                "status": str(response.status_code)
            }
        )
        
        # 记录访问日志
        logger.info("Request completed",
                   method=request.method,
                   path=request.path,
                   status=response.status_code,
                   duration_ms=round(duration * 1000, 2))
    
    return response

# 示例：在游戏事件中使用指标
def on_player_login(player_id: str):
    """玩家登录事件"""
    # 记录事件指标（注意：不包含player_id）
    inc_counter("game_events_total", 1, {
        "event_type": "player_login",
        "category": "auth"  # 使用类别代替玩家ID
    })
    
    # 记录结构化日志
    logger.info("Player logged in", 
                player_id=player_id,
                category="auth")

def on_combat_start(player_id: str, enemy_id: str):
    """战斗开始事件"""
    # 使用计时器记录战斗处理时间
    with time_histogram("combat_processing_seconds", {"type": "start"}):
        # 记录事件（服务级别标签）
        inc_counter("game_events_total", 1, {
            "event_type": "combat_start",
            "category": "combat"
        })
        
        logger.info("Combat started",
                   player_id=player_id,
                   enemy_id=enemy_id,
                   category="combat")
        
        # 模拟战斗处理
        time.sleep(0.1)

# 示例：错误处理与日志
@app.errorhandler(Exception)
def handle_error(error):
    """全局错误处理"""
    logger.error("Unhandled exception", 
                error=error,
                path=request.path)
    
    # 记录错误指标
    inc_counter("errors_total", 1, {
        "error_type": type(error).__name__,
        "severity": "error"
    })
    
    return {"error": str(error)}, 500

# 示例：使用Service层的监控
def example_with_services():
    """展示如何在Service层使用监控"""
    from xwe.services import ServiceContainer
    
    container = ServiceContainer.get_instance()
    game_service = container.resolve('IGameService')
    
    # 监控Service调用
    with time_histogram("service_call_duration_seconds", 
                       {"service": "game", "method": "process_command"}):
        result = game_service.process_command("explore", {})
    
    return result

if __name__ == '__main__':
    print("=" * 50)
    print("修仙世界引擎 - 第4阶段功能展示")
    print("=" * 50)
    print()
    print("当前配置：")
    print(f"  - 环境: {config.FLASK_ENV}")
    print(f"  - 日志级别: {config.LOG_LEVEL}")
    print(f"  - 日志格式: {config.LOG_FORMAT}")
    print(f"  - 开发API: {'启用' if config.ENABLE_DEV_API else '禁用'}")
    print(f"  - 指标启用: {'是' if config.METRICS_ENABLED else '否'}")
    print()
    print("✅ 监控指标: http://localhost:5001/api/v1/system/metrics")
    print("✅ API文档: http://localhost:5001/api/docs")
    print("✅ 调试控制台: http://localhost:5001/api/v1/dev/debug")
    print("✅ 健康检查: http://localhost:5001/api/v1/system/health")
    print("✅ 游戏界面: http://localhost:5001")
    print()
    print("提示：使用 docker-compose up 可以同时启动Prometheus监控")
    print("=" * 50)
    
    # 使用配置的调试模式
    app.run(host='0.0.0.0', port=5001, debug=config.FLASK_DEBUG)
