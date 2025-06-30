#!/usr/bin/env python3
"""
侧边栏功能API修复
添加缺失的API接口以支持侧边栏功能
"""

from flask import jsonify, request, session
import time
import json
from datetime import datetime

def register_sidebar_apis(app):
    """注册侧边栏相关的API接口"""
    
    @app.route("/api/cultivation/status")
    def get_cultivation_status():
        """获取修炼状态"""
        player_id = session.get("player_id", "default")
        
        # 模拟修炼数据
        cultivation_data = {
            "current_technique": "青云诀",
            "technique_level": "入门",
            "progress": 25,
            "max_cultivation_time": 8,
            "current_stamina": 100,
            "cultivation_speed": 1.0,
            "available_techniques": [
                {
                    "id": "qingyun",
                    "name": "青云诀",
                    "level": "黄阶下品",
                    "progress": 25,
                    "unlocked": True,
                    "description": "青云宗基础心法"
                },
                {
                    "id": "liehuo",
                    "name": "烈火诀",
                    "level": "黄阶中品", 
                    "progress": 0,
                    "unlocked": False,
                    "description": "火系攻击心法"
                },
                {
                    "id": "hanbing",
                    "name": "寒冰诀",
                    "level": "黄阶中品",
                    "progress": 0,
                    "unlocked": False,
                    "description": "冰系防御心法"
                }
            ],
            "tips": "当前体力充足，可以进行长时间修炼",
            "warning": ""
        }
        
        return jsonify({
            "success": True,
            "data": cultivation_data
        })
    
    @app.route("/api/cultivation/start", methods=["POST"])
    def start_cultivation():
        """开始修炼"""
        data = request.get_json()
        hours = data.get("hours", 1)
        technique = data.get("technique", "qingyun")
        
        # 模拟修炼结果
        if hours > 8:
            return jsonify({
                "success": False,
                "error": "修炼时间不能超过8小时",
                "max_hours": 8
            })
            
        cultivation_gain = hours * 10  # 每小时获得10点修为
        
        return jsonify({
            "success": True,
            "message": f"开始修炼{hours}小时",
            "result": f"修炼完成，获得{cultivation_gain}点修为",
            "cultivation_gain": cultivation_gain,
            "time_spent": hours
        })
    
    @app.route("/api/achievements")
    def get_achievements():
        """获取成就列表"""
        achievements = [
            {
                "id": "first_step",
                "name": "初入仙门",
                "description": "踏上修仙之路",
                "unlocked": True,
                "unlock_time": "2025-06-30 10:00:00",
                "category": "基础",
                "reward": "经验值+100"
            },
            {
                "id": "foundation_built", 
                "name": "筑基成功",
                "description": "突破至筑基期",
                "unlocked": False,
                "unlock_time": None,
                "category": "修炼",
                "reward": "灵石+50"
            },
            {
                "id": "pill_master",
                "name": "丹成九转",
                "description": "炼制出九转金丹",
                "unlocked": False,
                "unlock_time": None,
                "category": "炼丹",
                "reward": "丹方+1"
            },
            {
                "id": "sword_heart",
                "name": "剑心通明",
                "description": "领悟剑道真意",
                "unlocked": False,
                "unlock_time": None,
                "category": "剑道",
                "reward": "剑法+1"
            },
            {
                "id": "explorer",
                "name": "行万里路",
                "description": "探索超过100个地点",
                "unlocked": False,
                "unlock_time": None,
                "category": "探索",
                "reward": "地图碎片+1"
            }
        ]
        
        return jsonify({
            "success": True,
            "achievements": achievements,
            "total": len(achievements),
            "unlocked": len([a for a in achievements if a["unlocked"]])
        })
    
    @app.route("/api/map")
    def get_map_data():
        """获取地图数据"""
        map_data = {
            "current_location": session.get("location", "青云城"),
            "regions": [
                {
                    "name": "青云山脉",
                    "description": "修真者聚集的山脉",
                    "locations": [
                        {
                            "id": "qingyun_city",
                            "name": "青云城",
                            "description": "繁华的修真城市",
                            "accessible": True,
                            "discovered": True,
                            "coordinates": {"x": 100, "y": 100}
                        },
                        {
                            "id": "qingyun_peak",
                            "name": "青云峰",
                            "description": "青云宗山门所在",
                            "accessible": True,
                            "discovered": True,
                            "coordinates": {"x": 120, "y": 80}
                        },
                        {
                            "id": "spirit_forest",
                            "name": "灵兽森林",
                            "description": "危险的灵兽栖息地",
                            "accessible": True,
                            "discovered": False,
                            "coordinates": {"x": 80, "y": 120}
                        }
                    ]
                },
                {
                    "name": "东海仙岛",
                    "description": "传说中的仙人居所",
                    "locations": [
                        {
                            "id": "fairy_island",
                            "name": "蓬莱仙岛",
                            "description": "仙人聚集之地",
                            "accessible": False,
                            "discovered": False,
                            "coordinates": {"x": 200, "y": 50}
                        }
                    ]
                }
            ]
        }
        
        return jsonify({
            "success": True,
            "data": map_data
        })
    
    @app.route("/api/quests")
    def get_quests():
        """获取任务列表"""
        quests = [
            {
                "id": "intro_quest",
                "name": "初入青云",
                "description": "前往青云城了解情况，寻找修炼机会",
                "status": "active",
                "progress": 1,
                "max_progress": 3,
                "objectives": [
                    {"text": "抵达青云城", "completed": True},
                    {"text": "与城中NPC交谈", "completed": False},
                    {"text": "完成第一次修炼", "completed": False}
                ],
                "reward": {
                    "experience": 100,
                    "gold": 50,
                    "items": ["新手法器"]
                },
                "category": "主线"
            },
            {
                "id": "explore_quest",
                "name": "寻找机缘",
                "description": "探索周围区域，寻找修炼资源和宝物",
                "status": "available",
                "progress": 0,
                "max_progress": 5,
                "objectives": [
                    {"text": "探索灵兽森林", "completed": False},
                    {"text": "收集10个灵草", "completed": False},
                    {"text": "击败森林守护者", "completed": False}
                ],
                "reward": {
                    "experience": 200,
                    "gold": 100,
                    "items": ["中级丹药", "护身符"]
                },
                "category": "支线"
            },
            {
                "id": "cultivation_quest",
                "name": "修炼之路",
                "description": "提升修为，突破当前境界",
                "status": "available",
                "progress": 0,
                "max_progress": 1,
                "objectives": [
                    {"text": "修炼100小时", "completed": False}
                ],
                "reward": {
                    "experience": 500,
                    "cultivation": 1000
                },
                "category": "修炼"
            }
        ]
        
        return jsonify({
            "success": True,
            "quests": quests,
            "active_count": len([q for q in quests if q["status"] == "active"]),
            "available_count": len([q for q in quests if q["status"] == "available"])
        })
    
    @app.route("/api/intel")
    def get_intel_data():
        """获取情报数据"""
        intel_data = {
            "global": [
                {
                    "id": "sect_competition",
                    "title": "宗门大比即将开始",
                    "content": "各大宗门将在三个月后举行宗门大比，获胜者将获得珍贵奖励",
                    "importance": "high",
                    "time": "2025-06-30 08:00:00",
                    "source": "青云城消息",
                    "interactable_task_id": None
                },
                {
                    "id": "new_secret_realm",
                    "title": "发现新的秘境",
                    "content": "有修真者在东海发现了一处古老秘境，据说其中藏有上古传承",
                    "importance": "medium",
                    "time": "2025-06-29 20:30:00",
                    "source": "江湖传言",
                    "interactable_task_id": "explore_secret_realm"
                },
                {
                    "id": "market_info",
                    "title": "灵草价格上涨",
                    "content": "由于最近灵兽森林不太平静，灵草采集困难，导致市场价格上涨",
                    "importance": "low",
                    "time": "2025-06-29 15:20:00",
                    "source": "商人消息",
                    "interactable_task_id": None
                }
            ],
            "personal": [
                {
                    "id": "cultivation_reminder",
                    "title": "修炼进度提醒",
                    "content": "您的青云诀已达到入门境界25%，建议继续修炼或寻找更高级心法",
                    "importance": "medium",
                    "time": "2025-06-30 12:00:00",
                    "source": "系统提醒",
                    "interactable_task_id": "cultivation_quest"
                },
                {
                    "id": "inventory_full",
                    "title": "背包空间不足",
                    "content": "您的背包快满了，建议整理物品或扩展背包容量",
                    "importance": "low",
                    "time": "2025-06-30 11:30:00",
                    "source": "系统提醒",
                    "interactable_task_id": None
                }
            ]
        }
        
        return jsonify({
            "success": True,
            "data": intel_data
        })
    
    @app.route("/api/player/stats/detailed")
    def get_detailed_player_stats():
        """获取详细的玩家统计信息"""
        player_id = session.get("player_id", "default")
        player_name = session.get("player_name", "无名侠客")
        
        detailed_stats = {
            "basic_info": {
                "name": player_name,
                "level": 1,
                "realm": "炼气期",
                "realm_level": 1,
                "experience": 0,
                "next_level_exp": 100
            },
            "attributes": {
                "constitution": 5,    # 根骨
                "comprehension": 5,   # 悟性
                "spirit": 5,          # 神识
                "luck": 5,            # 机缘
                "charisma": 5,        # 魅力
                "willpower": 5        # 意志力
            },
            "combat_stats": {
                "current_health": 100,
                "max_health": 100,
                "current_mana": 50,
                "max_mana": 50,
                "current_stamina": 100,
                "max_stamina": 100,
                "attack_power": 10,
                "defense": 5,
                "speed": 8
            },
            "cultivation": {
                "cultivation_level": 0,
                "max_cultivation": 100,
                "cultivation_speed": 1.0,
                "current_technique": "青云诀",
                "technique_level": "入门"
            },
            "social": {
                "faction": "散修",
                "reputation": 0,
                "sect": None,
                "master": None,
                "disciples": []
            },
            "resources": {
                "gold": 100,
                "spirit_stones": 0,
                "contribution_points": 0
            },
            "progress": {
                "total_play_time": "2小时",
                "locations_discovered": 3,
                "quests_completed": 0,
                "enemies_defeated": 0,
                "items_collected": 2
            },
            "buffs": [],
            "debuffs": [],
            "achievements_unlocked": 1,
            "total_achievements": 5
        }
        
        return jsonify({
            "success": True,
            "data": detailed_stats
        })
    
    print("✅ 侧边栏API修复已注册")
    return app

if __name__ == "__main__":
    print("这是API修复模块，请在主应用中导入使用")
