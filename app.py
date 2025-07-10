"""
测试用 Flask 应用
"""
from flask import Flask, jsonify, request
import os
import time

# 设置环境变量
os.environ['ENABLE_PROMETHEUS'] = 'true'

# 导入 Prometheus 指标
try:
    from prometheus_flask_exporter import PrometheusMetrics
    from xwe.metrics.prometheus_metrics import (
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
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # 初始化 Prometheus 指标
    if PROMETHEUS_AVAILABLE:
        metrics = PrometheusMetrics(app, registry=REGISTRY)
        # 添加默认指标（避免重复注册）
        if REGISTRY.get_sample_value('xwe_app_info') is None:
            metrics.info('xwe_app_info', 'Application info', version='1.0.0')
    
    # 健康检查端点
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0'
        }), 200
    
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
        return jsonify({'ready': True}), 200
    
    # API 路由
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        return jsonify({'success': True, 'token': 'test-token'}), 200
    
    @app.route('/api/game/start', methods=['POST'])
    def start_game():
        return jsonify({'success': True, 'session_id': 'test-session'}), 201
    
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
        return jsonify({
            'session_id': f'session_{user_id}_{int(time.time())}',
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
        return jsonify({
            'status': 'active',
            'session_id': session_id,
            'created_at': time.time() - 3600,
            'last_activity': time.time()
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
'''
            return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
