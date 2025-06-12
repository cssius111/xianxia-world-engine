"""
成长型社区和反馈系统
- 游戏内反馈
- 社区链接
- 数据收集
- 玩家互动
"""

import os
import json
import time
import sqlite3
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import hashlib
import platform
from collections import defaultdict

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """反馈类型"""
    BUG = "bug"  # 错误报告
    SUGGESTION = "suggestion"  # 建议
    PRAISE = "praise"  # 表扬
    QUESTION = "question"  # 问题
    COMPLAINT = "complaint"  # 投诉
    FEATURE = "feature"  # 功能请求


class FeedbackPriority(Enum):
    """反馈优先级"""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Feedback:
    """反馈数据"""
    id: str
    type: FeedbackType
    content: str
    player_id: str
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    status: str = "new"  # new, reviewing, resolved, rejected
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "player_id": self.player_id,
            "timestamp": self.timestamp,
            "context": self.context,
            "priority": self.priority.value,
            "status": self.status,
            "tags": self.tags
        }


@dataclass
class CommunityLink:
    """社区链接"""
    name: str
    url: str
    description: str
    icon: str = "🔗"
    category: str = "general"


class FeedbackCollector:
    """反馈收集器"""
    
    def __init__(self, data_dir: str = "feedback"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化数据库
        self.db_path = os.path.join(data_dir, "feedback.db")
        self._init_database()
        
        # 反馈处理器
        self.processors: Dict[FeedbackType, List[Callable]] = {
            feedback_type: [] for feedback_type in FeedbackType
        }
        
        # 自动标签规则
        self.tag_rules = {
            "崩溃": ["crash", "critical"],
            "闪退": ["crash", "critical"],
            "卡死": ["freeze", "critical"],
            "bug": ["bug"],
            "错误": ["error"],
            "建议": ["suggestion"],
            "希望": ["feature"],
            "太难": ["difficulty", "balance"],
            "太简单": ["difficulty", "balance"],
            "不平衡": ["balance"],
            "界面": ["ui"],
            "操作": ["controls"],
            "剧情": ["story"],
            "任务": ["quest"],
            "NPC": ["npc"],
            "技能": ["skill"],
            "物品": ["item"]
        }
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                player_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                context TEXT,
                priority INTEGER DEFAULT 1,
                status TEXT DEFAULT 'new',
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(type);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_player ON feedback(player_id);
        ''')
        
        conn.commit()
        conn.close()
    
    def submit_feedback(self, 
                       feedback_type: FeedbackType,
                       content: str,
                       player_id: str,
                       context: Optional[Dict[str, Any]] = None) -> Feedback:
        """提交反馈"""
        # 生成ID
        feedback_id = self._generate_feedback_id(player_id, content)
        
        # 自动标记
        tags = self._auto_tag(content)
        
        # 自动设置优先级
        priority = self._auto_prioritize(feedback_type, content, tags)
        
        # 创建反馈对象
        feedback = Feedback(
            id=feedback_id,
            type=feedback_type,
            content=content,
            player_id=player_id,
            timestamp=time.time(),
            context=context or {},
            priority=priority,
            tags=tags
        )
        
        # 保存到数据库
        self._save_feedback(feedback)
        
        # 触发处理器
        for processor in self.processors.get(feedback_type, []):
            try:
                processor(feedback)
            except Exception as e:
                logger.error(f"反馈处理器错误: {e}")
        
        logger.info(f"收到反馈 [{feedback_type.value}]: {content[:50]}...")
        
        return feedback
    
    def _generate_feedback_id(self, player_id: str, content: str) -> str:
        """生成反馈ID"""
        hash_input = f"{player_id}:{content}:{time.time()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def _auto_tag(self, content: str) -> List[str]:
        """自动标记"""
        tags = []
        content_lower = content.lower()
        
        for keyword, tag_list in self.tag_rules.items():
            if keyword in content_lower:
                tags.extend(tag_list)
        
        return list(set(tags))  # 去重
    
    def _auto_prioritize(self, 
                        feedback_type: FeedbackType,
                        content: str,
                        tags: List[str]) -> FeedbackPriority:
        """自动设置优先级"""
        # 关键词优先级
        if any(tag in ["crash", "critical", "freeze"] for tag in tags):
            return FeedbackPriority.CRITICAL
        
        if feedback_type == FeedbackType.BUG:
            if any(tag in ["error", "bug"] for tag in tags):
                return FeedbackPriority.HIGH
            return FeedbackPriority.MEDIUM
        
        if feedback_type == FeedbackType.COMPLAINT:
            return FeedbackPriority.HIGH
        
        if feedback_type == FeedbackType.SUGGESTION:
            return FeedbackPriority.MEDIUM
        
        return FeedbackPriority.LOW
    
    def _save_feedback(self, feedback: Feedback):
        """保存反馈到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (id, type, content, player_id, timestamp, 
                                context, priority, status, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback.id,
            feedback.type.value,
            feedback.content,
            feedback.player_id,
            feedback.timestamp,
            json.dumps(feedback.context),
            feedback.priority.value,
            feedback.status,
            json.dumps(feedback.tags)
        ))
        
        conn.commit()
        conn.close()
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """获取反馈统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总数统计
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_count = cursor.fetchone()[0]
        
        # 按类型统计
        type_stats = {}
        for feedback_type in FeedbackType:
            cursor.execute(
                "SELECT COUNT(*) FROM feedback WHERE type = ?",
                (feedback_type.value,)
            )
            type_stats[feedback_type.value] = cursor.fetchone()[0]
        
        # 按状态统计
        cursor.execute('''
            SELECT status, COUNT(*) FROM feedback 
            GROUP BY status
        ''')
        status_stats = dict(cursor.fetchall())
        
        # 按优先级统计
        cursor.execute('''
            SELECT priority, COUNT(*) FROM feedback 
            GROUP BY priority
        ''')
        priority_stats = {
            FeedbackPriority(p).name: count 
            for p, count in cursor.fetchall()
        }
        
        # 最近反馈
        cursor.execute('''
            SELECT type, content, timestamp FROM feedback 
            ORDER BY timestamp DESC LIMIT 5
        ''')
        recent_feedback = [
            {
                "type": row[0],
                "content": row[1][:50] + "..." if len(row[1]) > 50 else row[1],
                "time_ago": self._format_time_ago(row[2])
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "total_count": total_count,
            "by_type": type_stats,
            "by_status": status_stats,
            "by_priority": priority_stats,
            "recent_feedback": recent_feedback
        }
    
    def _format_time_ago(self, timestamp: float) -> str:
        """格式化时间差"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "刚刚"
        elif diff < 3600:
            return f"{int(diff / 60)}分钟前"
        elif diff < 86400:
            return f"{int(diff / 3600)}小时前"
        else:
            return f"{int(diff / 86400)}天前"
    
    def export_feedback_report(self, output_path: str):
        """导出反馈报告"""
        stats = self.get_feedback_stats()
        
        report = f"""# 游戏反馈报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体统计
- 总反馈数：{stats['total_count']}

## 按类型分布
"""
        
        for feedback_type, count in stats['by_type'].items():
            report += f"- {feedback_type}: {count}\n"
        
        report += "\n## 按状态分布\n"
        for status, count in stats['by_status'].items():
            report += f"- {status}: {count}\n"
        
        report += "\n## 按优先级分布\n"
        for priority, count in stats['by_priority'].items():
            report += f"- {priority}: {count}\n"
        
        report += "\n## 最近反馈\n"
        for feedback in stats['recent_feedback']:
            report += f"- [{feedback['type']}] {feedback['content']} ({feedback['time_ago']})\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"反馈报告已导出到: {output_path}")


class CommunityHub:
    """社区中心"""
    
    def __init__(self):
        self.links = [
            CommunityLink(
                name="官方Discord",
                url="https://discord.gg/xianxia",
                description="加入官方Discord服务器，与其他玩家交流",
                icon="💬",
                category="social"
            ),
            CommunityLink(
                name="游戏论坛",
                url="https://forum.xianxia.game",
                description="分享攻略、提问题、参与讨论",
                icon="📝",
                category="forum"
            ),
            CommunityLink(
                name="Wiki百科",
                url="https://wiki.xianxia.game",
                description="查阅游戏资料、攻略和数据",
                icon="📚",
                category="wiki"
            ),
            CommunityLink(
                name="B站官方账号",
                url="https://space.bilibili.com/xianxia",
                description="观看游戏视频、直播和教程",
                icon="🎥",
                category="video"
            ),
            CommunityLink(
                name="微博",
                url="https://weibo.com/xianxiagame",
                description="获取最新游戏资讯和活动信息",
                icon="📢",
                category="news"
            ),
            CommunityLink(
                name="QQ群",
                url="qq://group/123456789",
                description="QQ群：123456789",
                icon="👥",
                category="social"
            ),
            CommunityLink(
                name="GitHub",
                url="https://github.com/xianxia-world-engine",
                description="查看源代码、提交Issue、贡献代码",
                icon="🐙",
                category="development"
            ),
            CommunityLink(
                name="赞助支持",
                url="https://donate.xianxia.game",
                description="支持游戏开发，获得专属称号",
                icon="❤️",
                category="support"
            )
        ]
        
        self.announcements = []
        self.community_events = []
    
    def get_links_by_category(self, category: str) -> List[CommunityLink]:
        """按分类获取链接"""
        return [link for link in self.links if link.category == category]
    
    def format_community_info(self) -> str:
        """格式化社区信息"""
        info = "=== 社区链接 ===\n\n"
        
        # 按分类整理
        categories = {
            "social": "社交平台",
            "forum": "论坛社区",
            "wiki": "资料百科",
            "video": "视频平台",
            "news": "新闻资讯",
            "development": "开发相关",
            "support": "支持我们"
        }
        
        for cat_id, cat_name in categories.items():
            links = self.get_links_by_category(cat_id)
            if links:
                info += f"【{cat_name}】\n"
                for link in links:
                    info += f"{link.icon} {link.name}\n"
                    info += f"   {link.description}\n"
                    info += f"   {link.url}\n\n"
        
        return info
    
    def add_announcement(self, title: str, content: str, priority: str = "normal"):
        """添加公告"""
        self.announcements.append({
            "title": title,
            "content": content,
            "priority": priority,
            "timestamp": time.time()
        })
        
        # 保留最新的10条
        self.announcements = sorted(
            self.announcements, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )[:10]
    
    def get_latest_announcements(self, limit: int = 3) -> List[Dict[str, Any]]:
        """获取最新公告"""
        return self.announcements[:limit]


class PlayerDataAnalytics:
    """玩家数据分析"""
    
    def __init__(self, data_dir: str = "analytics"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.session_data: Dict[str, Dict[str, Any]] = {}
        self.aggregate_data = {
            "daily_active_users": set(),
            "total_play_time": 0,
            "popular_features": defaultdict(int),
            "error_count": defaultdict(int),
            "retention_data": {}
        }
    
    def track_session_start(self, player_id: str):
        """记录会话开始"""
        self.session_data[player_id] = {
            "start_time": time.time(),
            "actions": [],
            "errors": []
        }
        
        # 记录日活
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.aggregate_data["daily_active_users"]:
            self.aggregate_data["daily_active_users"] = set()
        self.aggregate_data["daily_active_users"].add(player_id)
    
    def track_action(self, player_id: str, action: str, details: Dict[str, Any] = None):
        """记录玩家行动"""
        if player_id in self.session_data:
            self.session_data[player_id]["actions"].append({
                "action": action,
                "details": details or {},
                "timestamp": time.time()
            })
            
            # 更新热门功能统计
            self.aggregate_data["popular_features"][action] += 1
    
    def track_error(self, player_id: str, error_type: str, error_msg: str):
        """记录错误"""
        if player_id in self.session_data:
            self.session_data[player_id]["errors"].append({
                "type": error_type,
                "message": error_msg,
                "timestamp": time.time()
            })
            
            # 更新错误统计
            self.aggregate_data["error_count"][error_type] += 1
    
    def track_session_end(self, player_id: str):
        """记录会话结束"""
        if player_id in self.session_data:
            session = self.session_data[player_id]
            play_time = time.time() - session["start_time"]
            
            # 更新总游戏时间
            self.aggregate_data["total_play_time"] += play_time
            
            # 保存会话数据
            self._save_session_data(player_id, session, play_time)
            
            # 清理会话数据
            del self.session_data[player_id]
    
    def _save_session_data(self, player_id: str, session: Dict[str, Any], play_time: float):
        """保存会话数据"""
        session_file = os.path.join(
            self.data_dir,
            f"session_{player_id}_{int(session['start_time'])}.json"
        )
        
        session_summary = {
            "player_id": player_id,
            "start_time": session["start_time"],
            "play_time": play_time,
            "action_count": len(session["actions"]),
            "error_count": len(session["errors"]),
            "actions": session["actions"][-100:],  # 只保存最后100个动作
            "errors": session["errors"]
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_summary, f, ensure_ascii=False, indent=2)
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        return {
            "daily_active_users": len(self.aggregate_data["daily_active_users"]),
            "total_play_time_hours": round(self.aggregate_data["total_play_time"] / 3600, 2),
            "top_features": sorted(
                self.aggregate_data["popular_features"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "top_errors": sorted(
                self.aggregate_data["error_count"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "active_sessions": len(self.session_data)
        }


class CommunitySystem:
    """社区系统管理器"""
    
    def __init__(self):
        self.feedback_collector = FeedbackCollector()
        self.community_hub = CommunityHub()
        self.analytics = PlayerDataAnalytics()
        
        # 注册反馈处理器
        self._register_feedback_processors()
        
        # 系统信息
        self.system_info = {
            "game_version": "1.0.0",
            "platform": platform.system(),
            "python_version": platform.python_version()
        }
    
    def _register_feedback_processors(self):
        """注册反馈处理器"""
        # Bug处理器
        def process_bug(feedback: Feedback):
            if feedback.priority == FeedbackPriority.CRITICAL:
                logger.critical(f"严重BUG报告: {feedback.content}")
                # 可以发送通知给开发者
        
        # 建议处理器
        def process_suggestion(feedback: Feedback):
            logger.info(f"收到建议: {feedback.content[:100]}...")
            # 可以添加到待办列表
        
        self.feedback_collector.processors[FeedbackType.BUG].append(process_bug)
        self.feedback_collector.processors[FeedbackType.SUGGESTION].append(process_suggestion)
    
    def process_feedback_command(self, player_id: str, feedback_text: str) -> str:
        """处理反馈命令"""
        # 解析反馈类型
        feedback_type = FeedbackType.SUGGESTION  # 默认为建议
        
        if any(word in feedback_text.lower() for word in ["bug", "错误", "崩溃"]):
            feedback_type = FeedbackType.BUG
        elif any(word in feedback_text.lower() for word in ["建议", "希望"]):
            feedback_type = FeedbackType.SUGGESTION
        elif any(word in feedback_text.lower() for word in ["问题", "怎么"]):
            feedback_type = FeedbackType.QUESTION
        elif any(word in feedback_text.lower() for word in ["投诉", "太差"]):
            feedback_type = FeedbackType.COMPLAINT
        elif any(word in feedback_text.lower() for word in ["赞", "好", "棒"]):
            feedback_type = FeedbackType.PRAISE
        
        # 收集游戏上下文
        context = {
            "system_info": self.system_info,
            "timestamp": time.time()
        }
        
        # 提交反馈
        feedback = self.feedback_collector.submit_feedback(
            feedback_type=feedback_type,
            content=feedback_text,
            player_id=player_id,
            context=context
        )
        
        # 返回确认信息
        responses = {
            FeedbackType.BUG: "感谢你的错误报告！我们会尽快修复。",
            FeedbackType.SUGGESTION: "感谢你的建议！我们会认真考虑。",
            FeedbackType.QUESTION: "你的问题已收到，可以查看帮助文档或社区获取答案。",
            FeedbackType.COMPLAINT: "很抱歉给你带来不好的体验，我们会努力改进。",
            FeedbackType.PRAISE: "感谢你的支持和鼓励！❤️",
            FeedbackType.FEATURE: "功能请求已记录，我们会评估其可行性。"
        }
        
        response = responses.get(feedback_type, "感谢你的反馈！")
        response += f"\n反馈ID: {feedback.id}"
        
        return response
    
    def show_community_info(self) -> str:
        """显示社区信息"""
        info = self.community_hub.format_community_info()
        
        # 添加最新公告
        announcements = self.community_hub.get_latest_announcements()
        if announcements:
            info += "\n=== 最新公告 ===\n"
            for ann in announcements:
                info += f"\n【{ann['title']}】\n{ann['content']}\n"
        
        # 添加反馈统计
        stats = self.feedback_collector.get_feedback_stats()
        info += f"\n=== 社区反馈 ===\n"
        info += f"总反馈数：{stats['total_count']}\n"
        info += f"待处理：{stats['by_status'].get('new', 0)}\n"
        info += f"已解决：{stats['by_status'].get('resolved', 0)}\n"
        
        return info
    
    def export_community_report(self, output_dir: str):
        """导出社区报告"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 导出反馈报告
        feedback_report_path = os.path.join(output_dir, "feedback_report.md")
        self.feedback_collector.export_feedback_report(feedback_report_path)
        
        # 导出分析报告
        analytics_summary = self.analytics.get_analytics_summary()
        analytics_report_path = os.path.join(output_dir, "analytics_report.json")
        
        with open(analytics_report_path, 'w', encoding='utf-8') as f:
            json.dump(analytics_summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"社区报告已导出到: {output_dir}")


# 全局实例
community_system = CommunitySystem()

def integrate_community_features(game_core):
    """集成社区功能到游戏核心"""
    # 添加反馈命令处理
    original_process_command = game_core.process_command
    
    def enhanced_process_command(input_text: str):
        """增强的命令处理"""
        # 检查是否是反馈命令
        if input_text.startswith("反馈：") or input_text.startswith("反馈:"):
            feedback_text = input_text[3:].strip()
            if feedback_text:
                player_id = getattr(game_core.game_state.player, 'id', 'anonymous')
                response = community_system.process_feedback_command(player_id, feedback_text)
                game_core.output(response)
                return
        
        # 检查是否是社区命令
        elif input_text in ["社区", "community", "链接", "links"]:
            game_core.output(community_system.show_community_info())
            return
        
        # 记录玩家行动
        if hasattr(game_core.game_state, 'player') and game_core.game_state.player:
            player_id = game_core.game_state.player.id
            community_system.analytics.track_action(player_id, "command", {"input": input_text})
        
        # 调用原始方法
        original_process_command(input_text)
    
    # 替换方法
    game_core.process_command = enhanced_process_command
    
    # 添加会话跟踪
    if hasattr(game_core, 'start_new_game'):
        original_start_game = game_core.start_new_game
        
        def tracked_start_game(*args, **kwargs):
            result = original_start_game(*args, **kwargs)
            if hasattr(game_core.game_state, 'player') and game_core.game_state.player:
                community_system.analytics.track_session_start(game_core.game_state.player.id)
            return result
        
        game_core.start_new_game = tracked_start_game
    
    logger.info("社区功能已集成")


# 便捷命令
def submit_feedback(content: str, player_id: str = "anonymous") -> str:
    """提交反馈的便捷方法"""
    return community_system.process_feedback_command(player_id, content)

def show_community() -> str:
    """显示社区信息的便捷方法"""
    return community_system.show_community_info()
