"""
开发者API路由
仅在开发模式下可用
"""

from flask import Blueprint, jsonify, request
import flask
import sys

# 无论环境如何都先创建蓝图，随后再在外部判断是否导出
dev_bp = Blueprint('dev', __name__)


@dev_bp.route('/debug', methods=['GET'])
def debug_info():
    """获取调试信息"""
    return jsonify({
        "python_version": sys.version.split(" ")[0],
        "flask_version": flask.__version__
    })


@dev_bp.route('/test-command', methods=['POST'])
def test_command():
    """测试命令处理"""
    data = request.get_json()
    command = data.get('command', '')
    
    # 模拟命令处理
    return jsonify({
        "input": command,
        "parsed": {
            "type": "unknown",
            "parameters": {}
        },
        "output": ["命令已接收"]
    })


@dev_bp.route('/reset-game', methods=['POST'])
def reset_game():
    """重置游戏状态"""
    # TODO: 实现游戏重置逻辑
    return jsonify({
        "success": True,
        "message": "游戏已重置"
    })


@dev_bp.route('/add-item', methods=['POST'])
def add_item():
    """添加物品（作弊）"""
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    return jsonify({
        "success": True,
        "message": f"已添加 {quantity} 个 {item_id}"
    })


@dev_bp.route('/set-level', methods=['POST'])
def set_level():
    """设置等级（作弊）"""
    data = request.get_json()
    level = data.get('level', 1)
    
    return jsonify({
        "success": True,
        "message": f"等级已设置为 {level}"
    })
