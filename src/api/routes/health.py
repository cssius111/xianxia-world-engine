"""
健康检查端点
"""
from flask import Blueprint, jsonify
import psutil
import os
from datetime import datetime

health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('', methods=['GET'])
def health_check():
    """系统健康检查"""
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

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """就绪检查"""
    # 检查应用是否准备好接收流量
    return jsonify({'ready': True}), 200

@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """存活检查"""
    # 简单的存活检查
    return jsonify({'alive': True}), 200
