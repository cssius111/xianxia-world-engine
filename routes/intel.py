"""情报系统路由"""

from flask import Blueprint, jsonify, session

from xwe.features.intelligence_system import intelligence_system

bp = Blueprint("intel", __name__)


@bp.get("/api/intel")
def get_intel():
    """获取情报信息"""
    if 'session_id' not in session:
        return jsonify({'global': [], 'personal': []})

    # 避免循环引用，在需要时再导入主应用模块
    from entrypoints import run_web_ui_optimized
    instance = run_web_ui_optimized.get_game_instance(session['session_id'])
    game = instance['game']
    player_id = getattr(game.game_state.player, 'id', 'player') if game.game_state.player else 'player'

    global_news = [n.to_dict() for n in intelligence_system.get_global_news()]
    personal = [n.to_dict() for n in intelligence_system.get_personal_intel(player_id)]
    return jsonify({'global': global_news, 'personal': personal})
