"""
修仙世界引擎 - 优化版Web UI服务器
使用组合式日志显示，提升阅读体验
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, request, jsonify, session
import json
import time
from datetime import datetime

# 导入游戏核心
from xwe.core.game_core_enhanced import EnhancedGameCore
from xwe.core.cultivation_system import CultivationSystem
from xwe.features.narrative_system import NarrativeSystem
from xwe.features.ai_personalization import AIPersonalization
from xwe.features.community_system import CommunitySystem
from xwe.features.technical_ops import TechnicalOps

app = Flask(__name__, template_folder='templates_enhanced')
app.secret_key = 'xianxia_world_secret_key_2025'

# 全局游戏实例管理
game_instances = {}

def get_game_instance(session_id):
    """获取或创建游戏实例"""
    if session_id not in game_instances:
        # 创建新游戏实例
        game = EnhancedGameCore()
        
        # 初始化各系统
        # CultivationSystem 构造函数不接受游戏实例参数
        game.cultivation_system = CultivationSystem()
        game.narrative_system = NarrativeSystem()
        game.ai_personalization = AIPersonalization()
        game.community_system = CommunitySystem()
        game.technical_ops = TechnicalOps()
        
        # 初始化游戏
        game.initialize()
        
        # 创建玩家
        if not game.game_state.player:
            from xwe.core.character import Character
            from xwe.core.attributes import Attributes
            
            # 使用平衡后的配置
            attrs = Attributes()
            attrs.realm_name = "聚气期"
            attrs.realm_level = 1
            attrs.level = 1
            attrs.cultivation_level = 0
            attrs.max_cultivation = 100
            
            # 使用平衡后的属性值
            attrs.current_health = 100
            attrs.max_health = 100
            attrs.current_mana = 50
            attrs.max_mana = 50
            attrs.current_stamina = 100
            attrs.max_stamina = 100
            attrs.attack_power = 10
            attrs.defense = 5
            
            player = Character("player", "无名侠客", attrs)
            game.game_state.player = player
            game.game_state.current_location = "青云城"
            
            # 清空日志，准备新游戏
            game.game_state.logs = []
            
        game_instances[session_id] = {
            'game': game,
            'last_update': time.time(),
            'need_refresh': True
        }
    
    return game_instances[session_id]

def cleanup_old_instances():
    """清理超时的游戏实例"""
    current_time = time.time()
    timeout = 3600  # 1小时超时
    
    to_remove = []
    for session_id, instance in game_instances.items():
        if current_time - instance['last_update'] > timeout:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        # 尝试保存游戏
        try:
            instance = game_instances[session_id]
            if hasattr(instance['game'], 'technical_ops'):
                instance['game'].technical_ops.save_game(instance['game'].game_state)
        except:
            pass
        
        del game_instances[session_id]

@app.route('/')
def index():
    """主页面"""
    # 清理旧实例
    cleanup_old_instances()
    
    # 确保会话ID
    if 'session_id' not in session:
        session['session_id'] = str(time.time())
    
    # 获取游戏实例
    instance = get_game_instance(session['session_id'])
    game = instance['game']
    
    # 准备渲染数据
    player = game.game_state.player
    
    return render_template('game_enhanced_optimized.html', 
                         player=player,
                         location=game.game_state.current_location,
                         buffs=[],
                         special_status=[])

@app.route('/command', methods=['POST'])
def process_command():
    """处理游戏命令"""
    data = request.get_json()
    command = data.get('command', '')
    
    if 'session_id' not in session:
        return jsonify({'error': '会话已过期，请刷新页面'})
    
    instance = get_game_instance(session['session_id'])
    game = instance['game']
    
    # 处理命令
    game.process_command(command)
    
    # 标记需要刷新
    instance['need_refresh'] = True
    instance['last_update'] = time.time()
    
    return jsonify({'success': True})

@app.route('/status')
def get_status():
    """获取游戏状态"""
    if 'session_id' not in session:
        return jsonify({'error': '会话已过期'})
    
    instance = get_game_instance(session['session_id'])
    game = instance['game']
    player = game.game_state.player
    
    # 准备状态数据
    status_data = {
        'player': None,
        'location': game.game_state.current_location,
        'location_name': game.game_state.current_location,
        'gold': 0
    }
    
    if player:
        status_data['player'] = {
            'name': player.name,
            'attributes': {
                'realm_name': player.attributes.realm_name,
                'realm_level': player.attributes.realm_level,
                'cultivation_level': player.attributes.cultivation_level,
                'max_cultivation': player.attributes.max_cultivation,
                'current_health': player.attributes.current_health,
                'max_health': player.attributes.max_health,
                'current_mana': player.attributes.current_mana,
                'max_mana': player.attributes.max_mana,
                'current_stamina': player.attributes.current_stamina,
                'max_stamina': player.attributes.max_stamina,
                'attack_power': player.attributes.attack_power,
                'defense': player.attributes.defense
            },
            'extra_data': getattr(player, 'extra_data', {})
        }
        
        # 获取金币数量
        if hasattr(player, 'inventory') and hasattr(player.inventory, 'gold'):
            status_data['gold'] = player.inventory.gold
    
    return jsonify(status_data)

@app.route('/log')
def get_log():
    """获取游戏日志"""
    if 'session_id' not in session:
        return jsonify({'logs': []})
    
    instance = get_game_instance(session['session_id'])
    game = instance['game']
    
    # 限制日志数量，避免传输过多数据
    logs = game.game_state.logs[-100:]  # 最多显示最近100条
    
    return jsonify({'logs': logs})

@app.route('/need_refresh')
def need_refresh():
    """检查是否需要刷新"""
    if 'session_id' not in session:
        return jsonify({'refresh': False})
    
    instance = get_game_instance(session['session_id'])
    need_refresh = instance.get('need_refresh', False)
    
    # 重置标记
    if need_refresh:
        instance['need_refresh'] = False
    
    return jsonify({'refresh': need_refresh})

@app.route('/save_game', methods=['POST'])
def save_game():
    """保存游戏"""
    if 'session_id' not in session:
        return jsonify({'success': False, 'error': '会话已过期'})
    
    instance = get_game_instance(session['session_id'])
    game = instance['game']
    
    try:
        if hasattr(game, 'technical_ops'):
            game.technical_ops.save_game(game.game_state)
        return jsonify({'success': True, 'message': '游戏已保存'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/load_game', methods=['POST'])
def load_game():
    """加载游戏"""
    if 'session_id' not in session:
        return jsonify({'success': False, 'error': '会话已过期'})
    
    instance = get_game_instance(session['session_id'])
    game = instance['game']
    
    try:
        if hasattr(game, 'technical_ops'):
            loaded_state = game.technical_ops.load_game()
            if loaded_state:
                game.game_state = loaded_state
                instance['need_refresh'] = True
                return jsonify({'success': True, 'message': '游戏已加载'})
        return jsonify({'success': False, 'error': '没有找到存档'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("=== 修仙世界引擎 Web UI (优化版) ===")
    print("访问 http://localhost:5000 开始游戏")
    print("使用 Ctrl+C 停止服务器")
    print("=====================================")
    
    # 确保存档目录存在
    os.makedirs('saves', exist_ok=True)
    
    # 启动服务器
    app.run(debug=False, host='0.0.0.0', port=5000)
