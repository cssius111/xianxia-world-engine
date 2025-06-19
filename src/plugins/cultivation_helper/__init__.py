# plugins/cultivation_helper/__init__.py

"""
修炼助手插件 - 提供修炼辅助功能
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Callable
from xwe.core.plugin_system import Plugin


class CultivationHelperPlugin(Plugin):
    """修炼助手插件"""
    
    @property
    def name(self) -> str:
        return "cultivation_helper"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def dependencies(self) -> List[str]:
        return []
        
    async def initialize(self, engine) -> None:
        """初始化插件"""
        self.engine = engine
        self.cultivation_sessions = {}
        self.auto_cultivate_enabled = {}
        
        # 加载配置
        self.config = self.get_config_schema()
        
        # 注册定时任务
        self.cultivation_timer = asyncio.create_task(self._cultivation_timer())
        
        print(f"[{self.name}] 修炼助手插件已启动！")
        
    async def shutdown(self) -> None:
        """关闭插件"""
        # 取消定时任务
        if hasattr(self, 'cultivation_timer'):
            self.cultivation_timer.cancel()
            
        # 保存会话数据
        self._save_sessions()
        
        print(f"[{self.name}] 修炼助手插件已关闭。")
        
    def register_commands(self) -> Dict[str, Callable]:
        """注册命令"""
        return {
            '自动修炼': self._auto_cultivate_command,
            '修炼统计': self._cultivation_stats_command,
            '最佳修炼地': self._best_location_command,
            '修炼提醒': self._cultivation_reminder_command
        }
        
    def register_events(self) -> Dict[str, List[Callable]]:
        """注册事件处理器"""
        return {
            'cultivation_complete': [self._on_cultivation_complete],
            'player_move': [self._on_player_move],
            'realm_breakthrough': [self._on_realm_breakthrough]
        }
        
    def get_config_schema(self) -> Dict:
        """获取配置架构"""
        return {
            'auto_cultivate_interval': 300,  # 5分钟
            'reminder_interval': 1800,  # 30分钟
            'best_location_bonus': 1.5,  # 最佳地点加成
            'cultivation_efficiency_threshold': 0.7  # 效率阈值
        }
        
    def _auto_cultivate_command(self, player, args):
        """自动修炼命令"""
        player_id = player.id if hasattr(player, 'id') else str(player)
        
        if not args:
            # 切换自动修炼状态
            current_state = self.auto_cultivate_enabled.get(player_id, False)
            self.auto_cultivate_enabled[player_id] = not current_state
            
            if self.auto_cultivate_enabled[player_id]:
                self._init_cultivation_session(player_id)
                return "自动修炼已开启！系统将在合适的时机自动为你修炼。"
            else:
                return "自动修炼已关闭。"
                
        elif args[0] == '设置':
            if len(args) >= 2:
                try:
                    interval = int(args[1])
                    self.config['auto_cultivate_interval'] = interval * 60
                    return f"自动修炼间隔已设置为 {interval} 分钟。"
                except ValueError:
                    return "请输入有效的分钟数。"
                    
        return "用法：自动修炼 [设置 分钟数]"
        
    def _cultivation_stats_command(self, player, args):
        """修炼统计命令"""
        player_id = player.id if hasattr(player, 'id') else str(player)
        session = self.cultivation_sessions.get(player_id)
        
        if not session:
            return "暂无修炼记录。"
            
        stats = self._calculate_stats(session)
        
        return f"""
=== 修炼统计 ===
总修炼时间：{stats['total_time']} 小时
总获得经验：{stats['total_exp']}
平均效率：{stats['avg_efficiency']:.2%}
最佳地点：{stats['best_location']}
最高单次收益：{stats['max_gain']} 经验
境界突破次数：{stats['breakthroughs']}
"""
        
    def _best_location_command(self, player, args):
        """最佳修炼地命令"""
        # 分析当前可用的修炼地点
        locations = self._analyze_cultivation_locations(player)
        
        if not locations:
            return "未找到合适的修炼地点。"
            
        lines = ["=== 推荐修炼地点 ==="]
        for i, loc in enumerate(locations[:5], 1):
            lines.append(
                f"{i}. {loc['name']} - "
                f"灵气浓度：{loc['spiritual_energy']:.1f} "
                f"预期效率：{loc['efficiency']:.2%}"
            )
            
        lines.append("\n提示：在灵气浓郁的地方修炼事半功倍！")
        
        return "\n".join(lines)
        
    def _cultivation_reminder_command(self, player, args):
        """修炼提醒命令"""
        player_id = player.id if hasattr(player, 'id') else str(player)
        
        if not args:
            return "用法：修炼提醒 [开启/关闭/间隔 分钟数]"
            
        if args[0] == '开启':
            self._enable_reminder(player_id)
            return "修炼提醒已开启，我会定时提醒你修炼。"
            
        elif args[0] == '关闭':
            self._disable_reminder(player_id)
            return "修炼提醒已关闭。"
            
        elif args[0] == '间隔' and len(args) >= 2:
            try:
                interval = int(args[1])
                self.config['reminder_interval'] = interval * 60
                return f"提醒间隔已设置为 {interval} 分钟。"
            except ValueError:
                return "请输入有效的分钟数。"
                
        return "无效的参数。"
        
    async def _cultivation_timer(self):
        """修炼定时器"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                
                # 检查自动修炼
                await self._check_auto_cultivation()
                
                # 检查修炼提醒
                await self._check_cultivation_reminders()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[{self.name}] 定时器错误：{e}")
                
    async def _check_auto_cultivation(self):
        """检查自动修炼"""
        current_time = time.time()
        
        for player_id, enabled in self.auto_cultivate_enabled.items():
            if not enabled:
                continue
                
            session = self.cultivation_sessions.get(player_id)
            if not session:
                continue
                
            # 检查是否到了修炼时间
            last_cultivation = session.get('last_cultivation', 0)
            interval = self.config['auto_cultivate_interval']
            
            if current_time - last_cultivation >= interval:
                # 触发自动修炼
                await self._perform_auto_cultivation(player_id)
                
    async def _perform_auto_cultivation(self, player_id: str):
        """执行自动修炼"""
        # 检查玩家状态
        if not self._can_cultivate(player_id):
            return
            
        # 触发修炼事件
        if hasattr(self.engine, 'emit_async_event'):
            await self.engine.emit_async_event('auto_cultivation', {
                'player_id': player_id,
                'location': self._get_player_location(player_id)
            })
            
        # 更新会话
        session = self.cultivation_sessions[player_id]
        session['last_cultivation'] = time.time()
        session['auto_count'] = session.get('auto_count', 0) + 1
        
    def _on_cultivation_complete(self, event):
        """修炼完成事件处理"""
        player_id = event.get('player_id')
        if not player_id:
            return
            
        # 记录修炼数据
        session = self.cultivation_sessions.get(player_id, {})
        
        if 'history' not in session:
            session['history'] = []
            
        session['history'].append({
            'timestamp': time.time(),
            'exp_gained': event.get('exp_gained', 0),
            'location': event.get('location', 'unknown'),
            'efficiency': event.get('efficiency', 1.0)
        })
        
        # 保持历史记录在合理范围
        if len(session['history']) > 1000:
            session['history'] = session['history'][-500:]
            
        self.cultivation_sessions[player_id] = session
        
    def _on_player_move(self, event):
        """玩家移动事件处理"""
        player_id = event.get('player_id')
        new_location = event.get('location')
        
        if player_id and new_location:
            # 检查新位置是否是更好的修炼地点
            efficiency = self._calculate_location_efficiency(new_location)
            
            if efficiency >= self.config['cultivation_efficiency_threshold']:
                # 提示玩家这是个好的修炼地点
                self._notify_good_location(player_id, new_location, efficiency)
                
    def _on_realm_breakthrough(self, event):
        """境界突破事件处理"""
        player_id = event.get('player_id')
        if player_id:
            session = self.cultivation_sessions.get(player_id, {})
            session['breakthroughs'] = session.get('breakthroughs', 0) + 1
            self.cultivation_sessions[player_id] = session
            
    def _init_cultivation_session(self, player_id: str):
        """初始化修炼会话"""
        if player_id not in self.cultivation_sessions:
            self.cultivation_sessions[player_id] = {
                'start_time': time.time(),
                'history': [],
                'breakthroughs': 0,
                'auto_count': 0
            }
            
    def _calculate_stats(self, session: Dict) -> Dict:
        """计算统计数据"""
        history = session.get('history', [])
        
        if not history:
            return {
                'total_time': 0,
                'total_exp': 0,
                'avg_efficiency': 0,
                'best_location': 'N/A',
                'max_gain': 0,
                'breakthroughs': 0
            }
            
        total_exp = sum(h.get('exp_gained', 0) for h in history)
        efficiencies = [h.get('efficiency', 1.0) for h in history]
        avg_efficiency = sum(efficiencies) / len(efficiencies)
        
        # 找出最佳地点
        location_stats = {}
        for h in history:
            loc = h.get('location', 'unknown')
            if loc not in location_stats:
                location_stats[loc] = []
            location_stats[loc].append(h.get('efficiency', 1.0))
            
        best_location = max(
            location_stats.items(),
            key=lambda x: sum(x[1]) / len(x[1])
        )[0] if location_stats else 'N/A'
        
        max_gain = max((h.get('exp_gained', 0) for h in history), default=0)
        
        total_time = (time.time() - session.get('start_time', time.time())) / 3600
        
        return {
            'total_time': round(total_time, 2),
            'total_exp': total_exp,
            'avg_efficiency': avg_efficiency,
            'best_location': best_location,
            'max_gain': max_gain,
            'breakthroughs': session.get('breakthroughs', 0)
        }
        
    def _analyze_cultivation_locations(self, player) -> List[Dict]:
        """分析修炼地点"""
        # 这里应该调用游戏引擎获取实际的地点数据
        # 现在返回示例数据
        locations = [
            {
                'name': '灵气洞府',
                'spiritual_energy': 9.5,
                'efficiency': 0.95
            },
            {
                'name': '云顶天池',
                'spiritual_energy': 8.8,
                'efficiency': 0.88
            },
            {
                'name': '青莲峰',
                'spiritual_energy': 7.5,
                'efficiency': 0.75
            }
        ]
        
        return sorted(locations, key=lambda x: x['efficiency'], reverse=True)
        
    def _can_cultivate(self, player_id: str) -> bool:
        """检查是否可以修炼"""
        # 这里应该检查玩家的实际状态
        # 例如：是否在战斗中、是否有足够的体力等
        return True
        
    def _get_player_location(self, player_id: str) -> str:
        """获取玩家位置"""
        # 从游戏引擎获取实际位置
        return "default_location"
        
    def _calculate_location_efficiency(self, location: str) -> float:
        """计算地点效率"""
        # 这里应该根据地点的实际属性计算
        # 现在返回随机值
        import random
        return random.uniform(0.5, 1.0)
        
    def _notify_good_location(self, player_id: str, location: str, efficiency: float):
        """通知玩家发现好的修炼地点"""
        # 这里应该通过游戏引擎发送消息给玩家
        print(f"[{player_id}] 发现绝佳修炼地点：{location}（效率：{efficiency:.2%}）")
        
    def _enable_reminder(self, player_id: str):
        """启用修炼提醒"""
        # 记录提醒设置
        pass
        
    def _disable_reminder(self, player_id: str):
        """禁用修炼提醒"""
        # 取消提醒设置
        pass
        
    async def _check_cultivation_reminders(self):
        """检查修炼提醒"""
        # 实现提醒逻辑
        pass
        
    def _save_sessions(self):
        """保存会话数据"""
        # 可以将会话数据保存到文件
        try:
            with open('cultivation_sessions.json', 'w') as f:
                json.dump(self.cultivation_sessions, f)
        except Exception as e:
            print(f"[{self.name}] 保存会话数据失败：{e}")


# 导出插件类
__all__ = ['CultivationHelperPlugin']
