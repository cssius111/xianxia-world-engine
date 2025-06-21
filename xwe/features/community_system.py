"""
社区系统
处理玩家之间的互动和社交功能
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Message:
    """消息"""
    id: str
    sender: str
    recipient: str
    content: str
    timestamp: datetime
    read: bool = False


@dataclass
class Guild:
    """门派/公会"""
    id: str
    name: str
    description: str
    leader: str
    members: List[str] = field(default_factory=list)
    level: int = 1
    resources: Dict[str, int] = field(default_factory=dict)
    announcements: List[Dict[str, Any]] = field(default_factory=list)


class CommunitySystem:
    """
    社区系统管理器
    
    管理玩家间的社交互动、公会、消息等
    """
    
    def __init__(self):
        self.guilds: Dict[str, Guild] = {}
        self.messages: Dict[str, List[Message]] = {}  # player_id -> messages
        self.friend_lists: Dict[str, List[str]] = {}  # player_id -> friend_ids
        self.block_lists: Dict[str, List[str]] = {}   # player_id -> blocked_ids
        
        # 排行榜
        self.leaderboards = {
            "level": [],      # 等级排行
            "combat": [],     # 战力排行
            "wealth": [],     # 财富排行
            "reputation": []  # 声望排行
        }
        
        # 世界频道消息（简化版）
        self.world_chat: List[Dict[str, Any]] = []
        
    def create_guild(self, name: str, description: str, leader_id: str) -> Optional[Guild]:
        """
        创建门派
        
        Args:
            name: 门派名称
            description: 门派描述
            leader_id: 创建者ID
            
        Returns:
            创建的门派对象，如果失败返回None
        """
        # 检查名称是否已存在
        if any(g.name == name for g in self.guilds.values()):
            return None
        
        guild_id = f"guild_{len(self.guilds) + 1}"
        guild = Guild(
            id=guild_id,
            name=name,
            description=description,
            leader=leader_id,
            members=[leader_id]
        )
        
        self.guilds[guild_id] = guild
        return guild
    
    def join_guild(self, player_id: str, guild_id: str) -> bool:
        """
        加入门派
        
        Args:
            player_id: 玩家ID
            guild_id: 门派ID
            
        Returns:
            是否成功加入
        """
        guild = self.guilds.get(guild_id)
        if not guild:
            return False
        
        if player_id in guild.members:
            return False
        
        guild.members.append(player_id)
        
        # 发送欢迎消息
        self.add_guild_announcement(
            guild_id,
            f"欢迎新成员 {player_id} 加入门派！"
        )
        
        return True
    
    def leave_guild(self, player_id: str, guild_id: str) -> bool:
        """离开门派"""
        guild = self.guilds.get(guild_id)
        if not guild or player_id not in guild.members:
            return False
        
        # 不能是门主
        if player_id == guild.leader:
            return False
        
        guild.members.remove(player_id)
        return True
    
    def add_guild_announcement(self, guild_id: str, content: str) -> None:
        """添加门派公告"""
        guild = self.guilds.get(guild_id)
        if guild:
            guild.announcements.append({
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            
            # 保留最近20条公告
            if len(guild.announcements) > 20:
                guild.announcements = guild.announcements[-20:]
    
    def send_message(self, sender_id: str, recipient_id: str, content: str) -> Message:
        """
        发送私信
        
        Args:
            sender_id: 发送者ID
            recipient_id: 接收者ID
            content: 消息内容
            
        Returns:
            发送的消息对象
        """
        message = Message(
            id=f"msg_{datetime.now().timestamp()}",
            sender=sender_id,
            recipient=recipient_id,
            content=content,
            timestamp=datetime.now()
        )
        
        # 添加到接收者的消息列表
        if recipient_id not in self.messages:
            self.messages[recipient_id] = []
        
        self.messages[recipient_id].append(message)
        
        return message
    
    def get_unread_messages(self, player_id: str) -> List[Message]:
        """获取未读消息"""
        messages = self.messages.get(player_id, [])
        return [msg for msg in messages if not msg.read]
    
    def mark_message_read(self, player_id: str, message_id: str) -> bool:
        """标记消息为已读"""
        messages = self.messages.get(player_id, [])
        for msg in messages:
            if msg.id == message_id:
                msg.read = True
                return True
        return False
    
    def add_friend(self, player_id: str, friend_id: str) -> bool:
        """添加好友"""
        if player_id not in self.friend_lists:
            self.friend_lists[player_id] = []
        
        if friend_id in self.friend_lists[player_id]:
            return False
        
        self.friend_lists[player_id].append(friend_id)
        
        # 双向添加
        if friend_id not in self.friend_lists:
            self.friend_lists[friend_id] = []
        self.friend_lists[friend_id].append(player_id)
        
        return True
    
    def remove_friend(self, player_id: str, friend_id: str) -> bool:
        """删除好友"""
        if player_id in self.friend_lists and friend_id in self.friend_lists[player_id]:
            self.friend_lists[player_id].remove(friend_id)
            
            # 双向删除
            if friend_id in self.friend_lists and player_id in self.friend_lists[friend_id]:
                self.friend_lists[friend_id].remove(player_id)
            
            return True
        return False
    
    def block_player(self, player_id: str, block_id: str) -> bool:
        """屏蔽玩家"""
        if player_id not in self.block_lists:
            self.block_lists[player_id] = []
        
        if block_id not in self.block_lists[player_id]:
            self.block_lists[player_id].append(block_id)
            return True
        return False
    
    def unblock_player(self, player_id: str, block_id: str) -> bool:
        """取消屏蔽"""
        if player_id in self.block_lists and block_id in self.block_lists[player_id]:
            self.block_lists[player_id].remove(block_id)
            return True
        return False
    
    def update_leaderboard(self, board_type: str, player_data: Dict[str, Any]) -> None:
        """
        更新排行榜
        
        Args:
            board_type: 排行榜类型
            player_data: 玩家数据 {"id": str, "name": str, "value": int}
        """
        if board_type not in self.leaderboards:
            return
        
        board = self.leaderboards[board_type]
        
        # 查找是否已存在
        for i, entry in enumerate(board):
            if entry["id"] == player_data["id"]:
                board[i] = player_data
                break
        else:
            board.append(player_data)
        
        # 排序（降序）
        board.sort(key=lambda x: x["value"], reverse=True)
        
        # 保留前100名
        self.leaderboards[board_type] = board[:100]
    
    def get_leaderboard(self, board_type: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """获取排行榜前N名"""
        if board_type not in self.leaderboards:
            return []
        
        return self.leaderboards[board_type][:top_n]
    
    def broadcast_world_message(self, sender_id: str, sender_name: str, content: str) -> None:
        """
        广播世界消息
        
        Args:
            sender_id: 发送者ID
            sender_name: 发送者名称
            content: 消息内容
        """
        message = {
            "sender_id": sender_id,
            "sender_name": sender_name,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.world_chat.append(message)
        
        # 保留最近100条
        if len(self.world_chat) > 100:
            self.world_chat = self.world_chat[-100:]
    
    def get_recent_world_messages(self, count: int = 20) -> List[Dict[str, Any]]:
        """获取最近的世界消息"""
        return self.world_chat[-count:]
    
    def get_player_social_info(self, player_id: str) -> Dict[str, Any]:
        """获取玩家社交信息"""
        # 查找所在门派
        guild_info = None
        for guild in self.guilds.values():
            if player_id in guild.members:
                guild_info = {
                    "id": guild.id,
                    "name": guild.name,
                    "role": "leader" if player_id == guild.leader else "member"
                }
                break
        
        return {
            "guild": guild_info,
            "friends": self.friend_lists.get(player_id, []),
            "blocked": self.block_lists.get(player_id, []),
            "unread_messages": len(self.get_unread_messages(player_id))
        }
