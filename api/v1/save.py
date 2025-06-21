"""
存档相关API
处理游戏的保存和加载功能
"""

import os
import json
from datetime import datetime
from flask import Blueprint, jsonify, request

save_bp = Blueprint('save', __name__)

# 存档目录
SAVE_DIR = "saves"


@save_bp.route('/list', methods=['GET'])
def list_saves():
    """列出所有存档"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    
    saves = []
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(SAVE_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                    saves.append({
                        "filename": filename,
                        "timestamp": save_data.get("timestamp", "unknown"),
                        "player_name": save_data.get("player_name", "未知"),
                        "level": save_data.get("level", 1)
                    })
            except:
                pass
    
    return jsonify({"saves": saves})


@save_bp.route('/save', methods=['POST'])
def save_game():
    """保存游戏"""
    data = request.get_json()
    save_name = data.get('name', 'autosave')
    
    # 确保存档目录存在
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    
    # 生成存档文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{save_name}_{timestamp}.json"
    filepath = os.path.join(SAVE_DIR, filename)
    
    # TODO: 获取实际游戏状态
    save_data = {
        "version": "1.0.0",
        "timestamp": timestamp,
        "player_name": "测试玩家",
        "level": 1,
        "game_state": {}
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "filename": filename,
            "message": "游戏已保存"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@save_bp.route('/load/<filename>', methods=['POST'])
def load_game(filename):
    """加载游戏"""
    filepath = os.path.join(SAVE_DIR, filename)
    
    if not os.path.exists(filepath):
        return jsonify({
            "success": False,
            "error": "存档文件不存在"
        }), 404
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # TODO: 恢复游戏状态
        return jsonify({
            "success": True,
            "message": "游戏已加载",
            "data": save_data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@save_bp.route('/delete/<filename>', methods=['DELETE'])
def delete_save(filename):
    """删除存档"""
    filepath = os.path.join(SAVE_DIR, filename)
    
    if not os.path.exists(filepath):
        return jsonify({
            "success": False,
            "error": "存档文件不存在"
        }), 404
    
    try:
        os.remove(filepath)
        return jsonify({
            "success": True,
            "message": "存档已删除"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
