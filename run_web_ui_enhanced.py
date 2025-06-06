"""
增强版Web UI运行器
集成了更多游戏功能和优化
"""
import threading
import webbrowser
import json
import time
from flask import Flask, render_template, request, jsonify, session
from pathlib import Path
import os

# 添加项目根目录到系统路径
import sys
sys.path.append(str(Path(__file__).parent))

from xwe.core.game_core import GameCore
from xwe.core.achievement_system import AchievementSystem
from xwe.core.immersive_event_system import ImmersiveEventSystem
from xwe.features.player_experience import enhance_player_experience, input_helper
from xwe.features.narrative_system import narrative_system
from xwe.features.visual_enhancement import visual_effects

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates_enhanced')

# 配置
app.secret_key = 'xianxia_world_engine_secret_key_2025'

# 游戏实例管理
class GameManager:
    def __init__(self):
        self.game = GameCore()
        self.achievement_system = AchievementSystem()
        self.event_system = ImmersiveEventSystem()
        self.narrative_system = NarrativeSystem()
        
        # 增强玩家体验
        enhance_player_experience(self.game)
        
        # 开始新游戏
        self.game.start_new_game()
        
        # 存储日志
        self.logs = []
        self.max_logs = 500  # 最多保留500条日志
        
        # 状态标记
        self.state_changed = True
        self.last_update_time = time.time()
        
        # 新手状态
        self.is_new_player = True
        self.tutorial_step = 0
        
        # 初始化
        self._init_game()
    
    def _init_game(self):
        """初始化游戏"""
        # 添加成就回调
        self.achievement_system.add_unlock_callback(self._on_achievement_unlock)
        
        # 添加事件回调
        self.event_system.register_callback('first_cultivation_event', self._on_first_cultivation)
        
        # 初始日志
        self.add_log("【系统】正在唤醒修仙世界，请稍候……")
    
    def add_log(self, message, log_type="system"):
        """添加日志"""
        self.logs.append({
            'text': message,
            'type': log_type,
            'timestamp': time.time()
        })
        
        # 限制日志数量
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        self.state_changed = True
    
    def flush_output(self):
        """刷新游戏输出到日志"""
        output_lines = self.game.get_output()
        for line in output_lines:
            # 解析日志类型
            log_type = "normal"
            if "【系统】" in line:
                log_type = "system"
            elif "【剧情】" in line:
                log_type = "event"
            elif "【战斗】" in line:
                log_type = "combat"
            elif "【奖励】" in line:
                log_type = "reward"
            elif "[提示]" in line:
                log_type = "tip"
            elif "【警告】" in line:
                log_type = "warning"
            elif "➤" in line:
                log_type = "player"
            
            self.add_log(line, log_type)
    
    def process_command(self, command):
        """处理命令"""
        # 检查是否是事件选择
        if command.startswith("选择 ") and self.event_system.current_event:
            try:
                choice_index = int(command.split()[1]) - 1
                success, error = self.event_system.make_choice(choice_index)
                if success:
                    self._process_event_step()
                else:
                    self.add_log(f"【系统】{error}", "system")
            except:
                self.add_log("【系统】无效的选择", "system")
            return
        
        # 处理普通命令
        processed = input_helper.process_player_input(command, self._get_game_context())
        
        # 显示命令建议
        if processed["confidence"] < 0.7 and processed["suggestions"]:
            self.add_log("💭 你是想要：", "tip")
            for suggestion in processed["suggestions"]:
                self.add_log(f"  • {suggestion}", "tip")
        
        # 执行命令
        self.game.process_command(processed["command"])
        
        # 检查成就
        self._check_achievements(processed["command"])
        
        # 检查事件触发
        self._check_event_triggers(processed["command"])
        
        # 刷新输出
        self.flush_output()
    
    def _get_game_context(self):
        """获取游戏上下文"""
        context = {
            "player_health_percent": 1.0,
            "player_mana_percent": 1.0,
            "new_location": False,
            "nearby_enemies": 0,
            "nearby_npcs": 0
        }
        
        if self.game.game_state.player:
            player = self.game.game_state.player
            attrs = player.attributes
            context["player_health_percent"] = attrs.current_health / attrs.max_health
            context["player_mana_percent"] = attrs.current_mana / attrs.max_mana
        
        return context
    
    def _check_achievements(self, command):
        """检查成就"""
        if not self.game.game_state.player:
            return
        
        player = self.game.game_state.player
        
        # 检查各种成就条件
        checks = {}
        
        # 首次使用命令
        cmd_lower = command.lower()
        if self.tutorial_step == 0 and cmd_lower in ['状态', 's']:
            self.achievement_system.check_achievement('first_step')
            self.tutorial_step = 1
        
        # 战斗相关
        if hasattr(player, 'battle_stats'):
            checks['warrior_10'] = player.battle_stats.get('enemies_defeated', 0)
            checks['warrior_50'] = player.battle_stats.get('enemies_defeated', 0)
            checks['win_streak_10'] = player.battle_stats.get('win_streak', 0)
        
        # 修炼相关
        if player.attributes.realm_level >= 4:  # 筑基期
            self.achievement_system.check_achievement('breakthrough_qi')
        if player.attributes.realm_level >= 7:  # 金丹期
            self.achievement_system.check_achievement('breakthrough_golden')
        
        # 批量检查
        self.achievement_system.check_multiple_achievements(checks)
        
        # 显示待解锁成就
        while True:
            display = self.achievement_system.get_next_unlock_display()
            if not display:
                break
            self.add_log(display, "achievement")
    
    def _check_event_triggers(self, command):
        """检查事件触发"""
        cmd_lower = command.lower()
        
        # 首次修炼
        if cmd_lower in ['修炼', 'c'] and not hasattr(self, '_first_cultivation_done'):
            self._first_cultivation_done = True
            self.event_system.trigger_event('first_cultivation_event')
            self._process_event_step()
        
        # 随机遭遇
        if cmd_lower in ['探索', 'e'] and self.game.game_state.player:
            if hasattr(self.game.game_state, 'exploration_count'):
                self.game.game_state.exploration_count += 1
                # 每探索5次触发一次特殊事件
                if self.game.game_state.exploration_count % 5 == 0:
                    if self.event_system.trigger_event('treasure_discovery'):
                        self._process_event_step()
    
    def _process_event_step(self):
        """处理事件步骤"""
        if not self.event_system.current_event:
            return
        
        # 显示当前步骤
        step_display = self.event_system.format_current_step()
        if step_display:
            self.add_log(step_display, "event")
        
        # 检查自动继续
        if self.event_system.auto_continue():
            self._process_event_step()
        
        # 检查事件完成
        if self.event_system.is_event_complete():
            self.event_system.complete_event()
            self.add_log("【系统】事件已完成", "system")
    
    def _on_achievement_unlock(self, achievement):
        """成就解锁回调"""
        display = f"🏆 成就解锁：{achievement.name} - {achievement.description}"
        self.add_log(display, "achievement")
        self.add_log(f"获得成就点数：{achievement.points}", "reward")
    
    def _on_first_cultivation(self, choices):
        """首次修炼事件回调"""
        if choices and choices[0] == 'pure_qi':
            self.add_log("【系统】你选择了纯净温和的灵气，修炼效果稳定。", "system")
        elif choices and choices[0] == 'fierce_qi':
            self.add_log("【系统】你选择了炽热狂暴的灵气，攻击力得到提升！", "system")
        elif choices and choices[0] == 'mysterious_qi':
            self.add_log("【系统】你选择了深邃神秘的灵气，悟性得到提升！", "system")
    
    def get_status(self):
        """获取游戏状态"""
        state_dict = self.game.game_state.to_dict()
        
        # 添加额外信息
        state_dict['is_new_player'] = self.is_new_player
        state_dict['tutorial_step'] = self.tutorial_step
        state_dict['location'] = getattr(self.game.game_state, 'current_location', '青云山')
        state_dict['gold'] = getattr(self.game.game_state, 'gold', 0)
        
        # 成就信息
        unlocked, total = self.achievement_system.get_unlocked_count()
        state_dict['achievement_unlocked'] = unlocked
        state_dict['achievement_total'] = total
        state_dict['achievement_points'] = self.achievement_system.total_points
        
        # 当前事件
        if self.event_system.current_event:
            state_dict['current_event'] = {
                'id': self.event_system.current_event,
                'step': self.event_system.current_step
            }
        
        return state_dict
    
    def save_game(self):
        """保存游戏"""
        save_dir = Path("saves")
        save_dir.mkdir(exist_ok=True)
        
        # 保存游戏状态
        game_save = {
            'game_state': self.game.game_state.to_dict(),
            'is_new_player': self.is_new_player,
            'tutorial_step': self.tutorial_step,
            'logs': self.logs[-100:],  # 保存最近100条日志
            'timestamp': time.time()
        }
        
        with open(save_dir / "quicksave.json", "w", encoding="utf-8") as f:
            json.dump(game_save, f, ensure_ascii=False, indent=2)
        
        # 保存成就
        self.achievement_system.save_to_file(str(save_dir / "achievements.json"))
        
        self.add_log("【系统】游戏已保存", "system")
    
    def load_game(self):
        """加载游戏"""
        save_dir = Path("saves")
        save_file = save_dir / "quicksave.json"
        
        if not save_file.exists():
            return False
        
        try:
            with open(save_file, "r", encoding="utf-8") as f:
                save_data = json.load(f)
            
            # 恢复状态
            self.is_new_player = save_data.get('is_new_player', True)
            self.tutorial_step = save_data.get('tutorial_step', 0)
            self.logs = save_data.get('logs', [])
            
            # 加载成就
            self.achievement_system.load_from_file(str(save_dir / "achievements.json"))
            
            self.add_log("【系统】游戏已加载", "system")
            return True
        except Exception as e:
            self.add_log(f"【系统】加载失败：{str(e)}", "warning")
            return False

# 全局游戏管理器
game_manager = GameManager()

@app.route('/')
def index():
    """游戏主页"""
    game_manager.flush_output()
    state = game_manager.get_status()
    
    # 获取Buff和特殊状态
    player = state.get('player')
    buffs = []
    special_status = []
    
    if player and 'status_effects' in player:
        effects = player['status_effects']
        for effect in effects:
            if effect['type'] == 'buff':
                buffs.append(f"{effect['name']}（{effect['description']}）")
            else:
                special_status.append(effect['name'])
    
    # 只传递最近的日志，避免性能问题
    recent_logs = game_manager.logs[-200:]
    
    return render_template(
        'game_enhanced.html',
        player=player,
        logs=recent_logs,
        buffs=buffs,
        special_status=special_status,
        state=state
    )

@app.route('/status')
def status():
    """返回当前游戏状态"""
    game_manager.flush_output()
    return jsonify(game_manager.get_status())

@app.route('/log')
def log():
    """返回最新日志"""
    game_manager.flush_output()
    # 返回格式化的日志
    formatted_logs = []
    for log in game_manager.logs[-200:]:
        formatted_logs.append(log['text'])
    return jsonify({'logs': formatted_logs})

@app.route('/command', methods=['POST'])
def command():
    """处理来自前端的指令"""
    data = request.get_json()
    cmd = data.get('command', '')
    
    if cmd:
        # 特殊命令处理
        if cmd == '保存':
            game_manager.save_game()
        elif cmd == '载入':
            game_manager.load_game()
        else:
            game_manager.process_command(cmd)
    
    game_manager.flush_output()
    
    # 返回最新日志
    formatted_logs = []
    for log in game_manager.logs[-200:]:
        formatted_logs.append(log['text'])
    
    return jsonify({
        'logs': formatted_logs,
        'state': game_manager.get_status()
    })

@app.route('/need_refresh')
def need_refresh():
    """检查是否有新的游戏状态或日志需要刷新"""
    current_time = time.time()
    if game_manager.state_changed or (current_time - game_manager.last_update_time) > 30:
        game_manager.state_changed = False
        game_manager.last_update_time = current_time
        return jsonify({'refresh': True})
    return jsonify({'refresh': False})

@app.route('/commands')
def get_commands():
    """获取可用命令列表"""
    commands = [
        {'cmd': '状态', 'desc': '查看角色状态', 'shortcut': 's'},
        {'cmd': '修炼', 'desc': '打坐修炼', 'shortcut': 'c'},
        {'cmd': '探索', 'desc': '探索当前区域', 'shortcut': 'e'},
        {'cmd': '背包', 'desc': '查看物品', 'shortcut': 'b'},
        {'cmd': '功法', 'desc': '查看技能', 'shortcut': 'k'},
        {'cmd': '地图', 'desc': '查看地图', 'shortcut': 'm'},
        {'cmd': '帮助', 'desc': '显示帮助', 'shortcut': 'h'},
        {'cmd': '攻击', 'desc': '攻击目标', 'shortcut': 'a'},
        {'cmd': '防御', 'desc': '防御姿态', 'shortcut': 'd'},
        {'cmd': '使用', 'desc': '使用物品', 'shortcut': 'u'},
        {'cmd': '对话', 'desc': '与NPC交谈', 'shortcut': 't'},
        {'cmd': '商店', 'desc': '查看商店', 'shortcut': None},
        {'cmd': '任务', 'desc': '查看任务', 'shortcut': 'q'},
        {'cmd': '成就', 'desc': '查看成就', 'shortcut': None},
        {'cmd': '保存', 'desc': '保存游戏', 'shortcut': None},
        {'cmd': '载入', 'desc': '载入游戏', 'shortcut': None},
        {'cmd': '退出', 'desc': '退出游戏', 'shortcut': None}
    ]
    return jsonify(commands)

def open_browser():
    """延迟打开浏览器"""
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════╗
    ║      修仙世界引擎 - Web版          ║
    ║                                    ║
    ║  正在启动服务器...                 ║
    ║  浏览器将自动打开                  ║
    ║                                    ║
    ║  如果浏览器没有自动打开，请访问:   ║
    ║  http://127.0.0.1:5000            ║
    ╚════════════════════════════════════╝
    """)
    
    # 在新线程中打开浏览器
    threading.Thread(target=open_browser).start()
    
    # 启动Flask服务器
    app.run(host='127.0.0.1', port=5000, debug=False)
