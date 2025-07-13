"""
测试用 Flask 应用 - 完整版本
"""
from flask import Flask, jsonify, request, session, Response, stream_with_context, render_template, send_from_directory
import os
import time
import json
import psutil
from datetime import datetime

# 设置环境变量，允许外部覆盖
os.environ.setdefault('ENABLE_PROMETHEUS', 'true')

# 导入 Prometheus 指标
try:
    from prometheus_flask_exporter import PrometheusMetrics
    from src.xwe.metrics.prometheus_metrics import (
        nlp_request_seconds,
        nlp_error_total,
        command_execution_seconds,
        REGISTRY
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__, 
                template_folder='src/web/templates',
                static_folder='src/web/static')
    
    # 配置
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # 初始化游戏实例存储
    app.game_instances = {}
    
    # 初始化 Prometheus 指标
    if PROMETHEUS_AVAILABLE and os.getenv('ENABLE_PROMETHEUS', 'true').lower() == 'true':
        from prometheus_client import CollectorRegistry
        registry = CollectorRegistry()
        metrics = PrometheusMetrics(app, registry=registry)
        metrics.info('xwe_app_info', 'Application info', version='0.3.4')
    
    # 主页路由
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    # API主页
    @app.route('/api')
    def api_index():
        """API文档页面"""
        return jsonify({
            'name': '修仙世界引擎 API',
            'version': '0.3.4',
            'endpoints': {
                'health': '/api/health',
                'game': {
                    'start': 'POST /api/game/start',
                    'status': 'GET /api/game/status',
                    'command': 'POST /api/game/command'
                },
                'cultivation': {
                    'status': 'GET /api/cultivation/status',
                    'start': 'POST /api/cultivation/start'
                },
                'achievements': 'GET /api/achievements/',
                'inventory': 'GET /api/inventory/'
            },
            'documentation': '/docs'
        })
    
    # 文档路由
    @app.route('/docs')
    @app.route('/docs/<path:filename>')
    def docs(filename='index.html'):
        """文档页面"""
        # 简单的文档索引
        if filename == 'index.html':
            docs_list = [
                {'name': 'API文档', 'url': '/docs/API.md'},
                {'name': '架构设计', 'url': '/docs/ARCHITECTURE.md'},
                {'name': '开发者指南', 'url': '/docs/DEVELOPER_GUIDE.md'},
                {'name': 'README', 'url': '/docs/README.md'}
            ]
            return jsonify({
                'title': '修仙世界引擎文档',
                'documents': docs_list
            })
        # 返回Markdown文件内容
        try:
            from pathlib import Path
            doc_path = Path('docs') / filename
            if doc_path.exists() and doc_path.suffix == '.md':
                content = doc_path.read_text(encoding='utf-8')
                return Response(content, mimetype='text/markdown')
            else:
                return jsonify({'error': 'Document not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # 游戏页面
    @app.route('/game')
    def game():
        """游戏页面"""
        return render_template('game.html')
    
    # 健康检查端点
    @app.route('/health')
    @app.route('/api/health')
    def health():
        try:
            # 检查系统资源
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 检查关键服务
            checks = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '0.3.4',
                'checks': {
                    'cpu': {
                        'status': 'ok' if cpu_percent < 80 else 'warning',
                        'value': f'{cpu_percent}%'
                    },
                    'memory': {
                        'status': 'ok' if memory.percent < 80 else 'warning',
                        'value': f'{memory.percent}%'
                    },
                    'disk': {
                        'status': 'ok' if disk.percent < 90 else 'warning',
                        'value': f'{disk.percent}%'
                    }
                }
            }
            
            # 如果有任何警告，将总状态设为警告
            if any(check['status'] == 'warning' for check in checks['checks'].values()):
                checks['status'] = 'warning'
            
            return jsonify(checks), 200
            
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500
    
    @app.route('/health/detailed')
    def health_detailed():
        return jsonify({
            'status': 'healthy',
            'components': {
                'nlp': 'healthy',
                'database': 'healthy',
                'cache': 'healthy'
            },
            'timestamp': time.time()
        }), 200
    
    @app.route('/ready')
    def ready():
        """就绪检查"""
        return jsonify({'ready': True}), 200
    
    @app.route('/live')
    def live():
        """存活检查"""
        return jsonify({'alive': True}), 200
    
    # API 路由
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        return jsonify({'success': True, 'token': 'test-token'}), 200
    
    @app.route('/api/game/start', methods=['POST'])
    def start_game():
        session_id = f'session_{int(time.time())}'
        app.game_instances[session_id] = {
            'game': None,  # 实际游戏实例
            'created_at': time.time()
        }
        session['session_id'] = session_id
        return jsonify({'success': True, 'session_id': session_id}), 201
    
    @app.route('/api/game/command', methods=['POST'])
    def game_command():
        command = request.json.get('command', '')
        
        # 记录指标
        if PROMETHEUS_AVAILABLE:
            start_time = time.time()
            try:
                result = {
                    'success': True,
                    'result': f'执行命令: {command}',
                    'command': command
                }
                # 记录成功的命令执行
                nlp_request_seconds.labels(command_type='game_command', status='success').observe(time.time() - start_time)
            except Exception as e:
                # 记录错误
                nlp_error_total.labels(error_type='command_error').inc()
                result = {'success': False, 'error': str(e)}
        else:
            result = {
                'success': True,
                'result': f'执行命令: {command}',
                'command': command
            }
        
        return jsonify(result), 200
    
    @app.route('/api/game/status')
    def game_status():
        return jsonify({
            'player': {'name': '测试玩家', 'level': 1},
            'location': '新手村',
            'health': 100,
            'mana': 100
        }), 200
    
    @app.route('/api/nlp/process', methods=['POST'])
    def process_nlp():
        text = request.json.get('text', '')
        return jsonify({
            'raw': text,
            'normalized_command': '探索',
            'intent': 'action',
            'args': {},
            'explanation': '测试解析'
        }), 200
    
    @app.route('/api/v1/session', methods=['POST'])
    def create_session():
        user_id = request.json.get('user_id', 'anonymous')
        session_id = f'session_{user_id}_{int(time.time())}'
        app.game_instances[session_id] = {
            'game': None,
            'created_at': time.time()
        }
        return jsonify({
            'session_id': session_id,
            'created_at': time.time()
        }), 200
    
    @app.route('/api/v1/command', methods=['POST'])
    def api_command():
        session_id = request.json.get('session_id')
        command = request.json.get('command')
        return jsonify({
            'result': f'执行命令: {command}',
            'session_id': session_id
        }), 200
    
    @app.route('/api/v1/session/<session_id>/status')
    def session_status(session_id):
        if session_id in app.game_instances:
            instance = app.game_instances[session_id]
            return jsonify({
                'status': 'active',
                'session_id': session_id,
                'created_at': instance['created_at'],
                'last_activity': time.time()
            }), 200
        return jsonify({'error': 'Session not found'}), 404

    # 侧边栏API端点
    @app.route('/api/achievements/')
    def achievements():
        return jsonify({
            'achievements': [
                {
                    'id': 'first_cultivation',
                    'name': '初入修行',
                    'description': '完成第一次修炼',
                    'unlocked': True,
                    'unlocked_at': '2025-01-13T10:30:00Z'
                }
            ]
        }), 200

    @app.route('/api/inventory/')
    def inventory():
        return jsonify({
            'items': [
                {
                    'id': 'healing_pill',
                    'name': '疗伤丹',
                    'quantity': 5,
                    'type': 'consumable'
                }
            ],
            'capacity': 50,
            'used': 5
        }), 200

    @app.route('/api/map')
    def map_data():
        return jsonify({
            'data': [
                {'x': 0, 'y': 0, 'type': 'village', 'name': '新手村'},
                {'x': 1, 'y': 0, 'type': 'forest', 'name': '迷雾森林'}
            ]
        }), 200

    @app.route('/api/quests')
    def quests():
        return jsonify({
            'quests': [
                {
                    'id': 'intro_quest',
                    'name': '初入江湖',
                    'status': 'in_progress',
                    'objectives': [
                        {'text': '与村长对话', 'completed': True},
                        {'text': '完成第一次修炼', 'completed': False}
                    ]
                }
            ]
        }), 200

    @app.route('/api/intel')
    def intel():
        return jsonify({
            'data': [
                {
                    'id': 'rumor_1',
                    'type': 'rumor',
                    'content': '听说迷雾森林深处有宝物'
                }
            ]
        }), 200

    @app.route('/api/player/stats/detailed')
    def player_stats_detailed():
        return jsonify({
            'data': {
                'attributes': {
                    'strength': 10,
                    'agility': 12,
                    'intelligence': 15,
                    'vitality': 11
                },
                'skills': {
                    'sword_mastery': 1,
                    'meditation': 2
                }
            }
        }), 200

    @app.route('/api/cultivation/status')
    def cultivation_status():
        session_id = session.get('session_id')
        if session_id and session_id in app.game_instances:
            # 模拟游戏状态
            return jsonify({
                'realm': '练气期',
                'progress': 45.5,
                'next_realm': '筑基期',
                'tribulation_ready': False
            }), 200
        return jsonify({'realm': '未知', 'progress': 0}), 200

    @app.route('/api/cultivation/start', methods=['POST'])
    def cultivation_start():
        hours = request.json.get('hours', 1)
        session_id = session.get('session_id')
        
        # 模拟修炼结果
        exp_gained = hours * 10
        return jsonify({
            'success': True,
            'exp_gained': exp_gained,
            'result': f'修炼{hours}小时，获得{exp_gained}点经验'
        }), 200

    # 实现简单的事件流接口，供测试使用
    def _generate_events():
        """Yield a single status payload for SSE tests"""
        data = {
            "type": "status_update",
            "player": {
                "name": "测试玩家",
                "health": 100,
                "mana": 100
            },
            "inventory": {
                "items": 5,
                "capacity": 50
            }
        }
        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    @app.route('/events')
    def events():
        return Response(stream_with_context(_generate_events()), mimetype='text/event-stream')
    
    # 性能指标端点
    @app.route('/api/metrics')
    def api_metrics():
        """API性能指标"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return jsonify({
            'cpu': cpu_percent,
            'memory': memory.percent,
            'responseTime': {
                'p50': 125,
                'p90': 180,
                'p95': 220,
                'p99': 450
            },
            'timestamp': time.time()
        }), 200
    
    # 指标端点（如果 Prometheus 不可用）
    if not PROMETHEUS_AVAILABLE:
        @app.route('/metrics')
        def metrics():
            # 返回基本的指标格式
            metrics_text = '''# HELP xwe_nlp_request_seconds NLP request processing time in seconds
# TYPE xwe_nlp_request_seconds histogram
xwe_nlp_request_seconds_bucket{command_type="unknown",status="success",le="0.1"} 10
xwe_nlp_request_seconds_bucket{command_type="unknown",status="success",le="0.25"} 20
xwe_nlp_request_seconds_bucket{command_type="unknown",status="success",le="0.5"} 30
xwe_nlp_request_seconds_bucket{command_type="unknown",status="success",le="1.0"} 40
xwe_nlp_request_seconds_bucket{command_type="unknown",status="success",le="+Inf"} 50
xwe_nlp_request_seconds_count{command_type="unknown",status="success"} 50
xwe_nlp_request_seconds_sum{command_type="unknown",status="success"} 12.5

# HELP xwe_app_info Application info
# TYPE xwe_app_info gauge
xwe_app_info{version="0.3.4"} 1
'''
            return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
