"""
存档相关API
处理游戏存档的创建、读取、更新和删除
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List

from flask import Blueprint, request, session

from ..errors import (
    InvalidRequestError,
    NotFoundError,
    SaveLimitExceededError,
    SaveNotFoundError,
)
from ..utils import api_response, paginated_response, validate_request

# 创建蓝图
save_bp = Blueprint("save", __name__)

# 存档目录
SAVES_DIR = "saves"
MAX_SAVES = 10  # 最大存档数量


def ensure_saves_dir():
    """确保存档目录存在"""
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)


@save_bp.route("/list", methods=["GET"])
@api_response
def list_saves():
    """
    获取存档列表

    Query Parameters:
        - sort: 排序方式 (created, modified, name)
        - order: 排序顺序 (asc, desc)

    Returns:
        {
            "saves": [
                {
                    "id": "save_123",
                    "name": "我的存档",
                    "created_at": 12345,
                    "modified_at": 12345,
                    "play_time": 3600,
                    "player_info": {
                        "name": "张三",
                        "level": 10,
                        "realm": "筑基期"
                    }
                }
            ],
            "count": 5
        }
    """
    ensure_saves_dir()

    # 获取排序参数
    sort_by = request.args.get("sort", "modified")
    order = request.args.get("order", "desc")

    saves = []

    # 读取所有存档文件
    for filename in os.listdir(SAVES_DIR):
        if filename.endswith(".json"):
            save_path = os.path.join(SAVES_DIR, filename)
            try:
                with open(save_path, "r", encoding="utf-8") as f:
                    save_data = json.load(f)

                save_id = filename[:-5]  # 去掉.json后缀

                saves.append(
                    {
                        "id": save_id,
                        "name": save_data.get("name", "未命名存档"),
                        "created_at": save_data.get("created_at", 0),
                        "modified_at": save_data.get("modified_at", 0),
                        "play_time": save_data.get("play_time", 0),
                        "player_info": {
                            "name": save_data.get("player", {}).get("name", "未知"),
                            "level": save_data.get("player", {}).get("level", 1),
                            "realm": save_data.get("player", {}).get("realm", "炼气期"),
                        },
                    }
                )
            except Exception as e:
                print(f"读取存档失败 {filename}: {str(e)}")
                continue

    # 排序
    if sort_by == "created":
        saves.sort(key=lambda x: x["created_at"], reverse=(order == "desc"))
    elif sort_by == "modified":
        saves.sort(key=lambda x: x["modified_at"], reverse=(order == "desc"))
    elif sort_by == "name":
        saves.sort(key=lambda x: x["name"], reverse=(order == "desc"))

    return {"saves": saves, "count": len(saves)}


@save_bp.route("/create", methods=["POST"])
@api_response
@validate_request(
    {
        "type": "object",
        "properties": {"name": {"type": "string", "minLength": 1, "maxLength": 50}},
        "required": ["name"],
    }
)
def create_save():
    """
    创建新存档

    Request:
        {
            "name": "我的存档"
        }

    Returns:
        {
            "id": "save_123",
            "name": "我的存档",
            "created_at": 12345
        }
    """
    ensure_saves_dir()

    # 检查存档数量限制
    existing_saves = len([f for f in os.listdir(SAVES_DIR) if f.endswith(".json")])
    if existing_saves >= MAX_SAVES:
        raise SaveLimitExceededError(MAX_SAVES)

    # 获取游戏数据
    game = session.get("game")
    if not game:
        raise InvalidRequestError("没有进行中的游戏")

    # 生成存档ID
    save_id = f"save_{int(time.time())}_{os.urandom(4).hex()}"
    save_name = request.json["name"]

    # 构建存档数据
    save_data = {
        "id": save_id,
        "name": save_name,
        "created_at": int(time.time()),
        "modified_at": int(time.time()),
        "play_time": getattr(game, "play_time", 0),
        "game_version": "1.0.0",
        "player": game.player.to_dict() if hasattr(game.player, "to_dict") else {},
        "game_state": game.get_save_data() if hasattr(game, "get_save_data") else {},
    }

    # 保存到文件
    save_path = os.path.join(SAVES_DIR, f"{save_id}.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    return {"id": save_id, "name": save_name, "created_at": save_data["created_at"]}


@save_bp.route("/<save_id>", methods=["GET"])
@api_response
def get_save(save_id: str):
    """
    获取存档详情

    Path Parameters:
        - save_id: 存档ID

    Returns:
        完整的存档数据
    """
    ensure_saves_dir()

    save_path = os.path.join(SAVES_DIR, f"{save_id}.json")

    if not os.path.exists(save_path):
        raise SaveNotFoundError(save_id)

    try:
        with open(save_path, "r", encoding="utf-8") as f:
            save_data = json.load(f)
        return save_data
    except Exception as e:
        raise InvalidRequestError(f"读取存档失败: {str(e)}")


@save_bp.route("/<save_id>", methods=["PUT"])
@api_response
@validate_request(
    {"type": "object", "properties": {"name": {"type": "string", "minLength": 1, "maxLength": 50}}}
)
def update_save(save_id: str):
    """
    更新存档（覆盖保存）

    Path Parameters:
        - save_id: 存档ID

    Request:
        {
            "name": "新的存档名称"  // 可选
        }

    Returns:
        {
            "message": "存档更新成功",
            "modified_at": 12345
        }
    """
    ensure_saves_dir()

    save_path = os.path.join(SAVES_DIR, f"{save_id}.json")

    if not os.path.exists(save_path):
        raise SaveNotFoundError(save_id)

    # 获取游戏数据
    game = session.get("game")
    if not game:
        raise InvalidRequestError("没有进行中的游戏")

    # 读取现有存档
    with open(save_path, "r", encoding="utf-8") as f:
        save_data = json.load(f)

    # 更新存档数据
    save_data["modified_at"] = int(time.time())
    save_data["play_time"] = getattr(game, "play_time", 0)
    save_data["player"] = game.player.to_dict() if hasattr(game.player, "to_dict") else {}
    save_data["game_state"] = game.get_save_data() if hasattr(game, "get_save_data") else {}

    # 如果提供了新名称
    if "name" in request.json:
        save_data["name"] = request.json["name"]

    # 保存到文件
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    return {"message": "存档更新成功", "modified_at": save_data["modified_at"]}


@save_bp.route("/<save_id>", methods=["DELETE"])
@api_response
def delete_save(save_id: str):
    """
    删除存档

    Path Parameters:
        - save_id: 存档ID

    Returns:
        {
            "message": "存档删除成功"
        }
    """
    ensure_saves_dir()

    save_path = os.path.join(SAVES_DIR, f"{save_id}.json")

    if not os.path.exists(save_path):
        raise SaveNotFoundError(save_id)

    try:
        os.remove(save_path)
        return {"message": "存档删除成功"}
    except Exception as e:
        raise InvalidRequestError(f"删除存档失败: {str(e)}")


@save_bp.route("/load/<save_id>", methods=["POST"])
@api_response
def load_save(save_id: str):
    """
    加载存档到当前游戏

    Path Parameters:
        - save_id: 存档ID

    Returns:
        {
            "message": "存档加载成功",
            "player_name": "张三",
            "player_level": 10
        }
    """
    ensure_saves_dir()

    save_path = os.path.join(SAVES_DIR, f"{save_id}.json")

    if not os.path.exists(save_path):
        raise SaveNotFoundError(save_id)

    try:
        # 读取存档数据
        with open(save_path, "r", encoding="utf-8") as f:
            save_data = json.load(f)

        # 创建新游戏实例并加载数据
        from xwe.game_engine import GameEngine

        game = GameEngine()

        # 加载存档数据
        if hasattr(game, "load_save_data"):
            game.load_save_data(save_data["game_state"])

        # 加载玩家数据
        if hasattr(game, "player") and hasattr(game.player, "from_dict"):
            game.player.from_dict(save_data["player"])

        # 保存到session
        session["game"] = game
        session["current_save_id"] = save_id

        return {
            "message": "存档加载成功",
            "player_name": save_data["player"].get("name", "未知"),
            "player_level": save_data["player"].get("level", 1),
        }

    except Exception as e:
        raise InvalidRequestError(f"加载存档失败: {str(e)}")


@save_bp.route("/export/<save_id>", methods=["GET"])
@api_response
def export_save(save_id: str):
    """
    导出存档文件

    Path Parameters:
        - save_id: 存档ID

    Returns:
        存档文件的下载链接或base64编码的数据
    """
    ensure_saves_dir()

    save_path = os.path.join(SAVES_DIR, f"{save_id}.json")

    if not os.path.exists(save_path):
        raise SaveNotFoundError(save_id)

    try:
        with open(save_path, "r", encoding="utf-8") as f:
            save_data = json.load(f)

        # 返回base64编码的数据
        import base64

        json_str = json.dumps(save_data, ensure_ascii=False)
        base64_data = base64.b64encode(json_str.encode("utf-8")).decode("ascii")

        return {"filename": f"{save_id}.json", "data": base64_data, "size": len(json_str)}

    except Exception as e:
        raise InvalidRequestError(f"导出存档失败: {str(e)}")
