"""Combat and game interaction routes."""

from __future__ import annotations

import json
import random
import time
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from flask import Blueprint, jsonify, request, session, Response, stream_with_context, make_response, render_template

from .. import (
    exploration_system,
    inventory_system,
    command_router,
    get_game_instance,
    data_loader,
    handle_attack,
    logger,
)
from src.common.request_utils import is_dev_request

combat_bp = Blueprint("combat", __name__)


@combat_bp.route("/get_audio_list")
def get_audio_list():
    audio_dir = Path("static/audio")
    audio_files = []
    if audio_dir.exists():
        for ext in [".mp3", ".ogg", ".wav"]:
            audio_files.extend([f.name for f in audio_dir.glob(f"*{ext}")])
    return jsonify({"files": audio_files})


@combat_bp.route("/save_game", methods=["POST"])
def save_game_route():
    if "session_id" not in session:
        return jsonify({"success": False, "error": "会话已过期"})

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    try:
        if hasattr(game, "technical_ops"):
            game.technical_ops.save_game(game.game_state)
        return jsonify({"success": True, "message": "游戏已保存"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@combat_bp.route("/load_game", methods=["POST"])
def load_game_route():
    if "session_id" not in session:
        return jsonify({"success": False, "error": "会话已过期"})

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    try:
        if hasattr(game, "technical_ops"):
            loaded_state = game.technical_ops.load_game()
            if loaded_state:
                game.game_state = loaded_state
                instance["need_refresh"] = True
                return jsonify({"success": True, "message": "游戏已加载"})
        return jsonify({"success": False, "error": "没有找到存档"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@combat_bp.route("/api/roll", methods=["POST"])
def api_roll():
    data = request.get_json()
    mode = data.get("mode", "random")

    from scripts.dev.gen_character import save_character  # noqa: F401
    from scripts.dev.gen_character import gen_from_prompt, gen_random, gen_template

    if mode == "random":
        character = gen_random()
    elif mode == "template":
        template_type = data.get("type", "sword")
        character = gen_template(template_type)
    elif mode == "custom":
        prompt = data.get("prompt", "")
        character = gen_from_prompt(prompt)
    else:
        character = gen_random()

    backend_attrs = character.get("attributes", {})
    frontend_attrs = {
        "constitution": backend_attrs.get("constitution", 5),
        "comprehension": backend_attrs.get("comprehension", 5),
        "spirit": backend_attrs.get("perception", backend_attrs.get("willpower", 5)),
        "luck": backend_attrs.get("fortune", backend_attrs.get("opportunity", 5)),
    }

    gender = random.choice(["male", "female"])
    background = random.choice(["poor", "merchant", "scholar", "martial"])

    destiny_data = data_loader.get_destinies()
    options = destiny_data.get("destiny_grades", [])
    destiny = random.choice(options) if options else None

    roll_result = {
        "name": character.get("name", "无名侠客"),
        "gender": gender,
        "background": background,
        "attributes": frontend_attrs,
        "destiny": destiny,
    }

    return jsonify({"success": True, "character": roll_result, "destiny": destiny})


@combat_bp.route("/command", methods=["POST"])
def process_command():
    dev_mode = is_dev_request()
    data = request.get_json()
    user_input = data.get("text", data.get("command", ""))
    player_id = session.get("player_id", "default")

    if dev_mode:
        session["dev"] = True

    command_handler, params = command_router.route_command(user_input)

    if "explanation" in params:
        logger.info(f"命令解析: {user_input} -> {command_handler} ({params.get('explanation')})")
    else:
        logger.info(f"命令解析: {user_input} -> {command_handler}")

    if command_handler == "explore":
        location = session.get("location", "青云城")

        def _add_items_cb(items: List[Dict]):
            inventory_system.add_items(player_id, items)
            logger.info("[EXPLORE] inventory_system.add_items called")

        explore_result = exploration_system.explore(
            location,
            command_context={"command": user_input, "params": params},
            inventory_add_cb=_add_items_cb,
        )

        result_text = explore_result["narration"]
        if explore_result["items"]:
            items_text = "、".join([f"{item['name']}x{item['qty']}" for item in explore_result["items"]])
            result_text += f"\n\n获得物品：{items_text}"

        return jsonify({
            "success": True,
            "result": result_text,
            "bag_updated": bool(explore_result["items"]),
            "explore_result": explore_result,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "inventory":
        inventory_data = inventory_system.get_inventory_data(player_id)

        if inventory_data["items"]:
            items_text = "\n".join([
                f"- {item['name']} x{item['quantity']}" for item in inventory_data["items"]
            ])
            result_text = (
                f"你的背包中有：\n{items_text}\n\n"
                f"金币：{inventory_data['gold']}\n"
                f"容量：{inventory_data['used']}/{inventory_data['capacity']}"
            )
        else:
            result_text = "你的背包空空如也。"

        return jsonify({
            "success": True,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "status":
        result_text = f"【{session.get('player_name', '无名侠客')}】\n境界：炼气期一层\n生命：100/100\n法力：50/50\n体力：100/100"
        return jsonify({
            "success": True,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "cultivate":
        duration = params.get("duration", "")
        if duration:
            result_text = f"你开始{params.get('mode', '打坐')}修炼{duration}，感受天地灵气缓缓流入体内..."
        else:
            result_text = "你开始打坐修炼，感受天地灵气缓缓流入体内..."
        return jsonify({
            "success": True,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "move":
        location = params.get("location", params.get("target", ""))
        if location:
            session["location"] = location
            result_text = f"你来到了{location}。"
        else:
            result_text = "你想去哪里？（可用地点：城主府、丹药铺、任务大厅、城外）"
        return jsonify({
            "success": True,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "use_item":
        item_name = params.get("item", params.get("target", ""))
        if item_name:
            if inventory_system.has_item(player_id, item_name):
                inventory_system.remove_item(player_id, item_name, 1)
                result_text = f"你使用了{item_name}。"
            else:
                result_text = f"你没有{item_name}。"
        else:
            result_text = "请指定要使用的物品。"
        return jsonify({
            "success": True,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "attack":
        target = params.get("target", "")
        instance = get_game_instance(session.get("session_id"))
        game = instance["game"]
        attack_result = handle_attack(target, game)
        return jsonify({
            **attack_result,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "talk":
        target = params.get("target", "")
        if target:
            result_text = f"你与{target}交谈。\n{target}：少侠好，有什么可以帮助你的吗？"
        else:
            result_text = "附近没有可以交谈的人。"
        return jsonify({
            "success": True,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "help":
        result_text = command_router.get_help_text()
        return jsonify({
            "success": True,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "unknown":
        confidence = params.get("confidence", 0.5)
        if confidence < 0.5:
            result_text = f"抱歉，我不太理解'{user_input}'的意思。请尝试其他表达方式。"
        else:
            result_text = f"命令'{user_input}'暂未实现。"
        return jsonify({
            "success": True,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    elif command_handler == "context_error":
        result_text = f"在当前场景下，{params.get('message', '该命令不可用')}。"
        return jsonify({
            "success": False,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })

    else:
        result_text = f"命令'{command_handler}'功能开发中..."
        return jsonify({
            "success": True,
            "result": result_text,
            "parsed_command": {"handler": command_handler, "params": params},
        })


@combat_bp.route("/api/parse_custom", methods=["POST"])
def parse_custom_text():
    try:
        data = request.get_json()
        text = data.get("text", "")
        try:
            import json as pyjson
            from src.xwe.core.nlp import LLMClient
            llm = LLMClient()
            result = llm.chat(text)
            try:
                parsed = pyjson.loads(result)
            except Exception:
                parsed = {"result": result}
            return jsonify({"success": True, "data": parsed})
        except ImportError:
            return jsonify({"success": False, "error": "NLP功能未启用或不可用"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@combat_bp.route("/nlp_monitor")
def nlp_monitor():
    return render_template("nlp_monitor.html")


@combat_bp.route("/api/nlp/stats")
def get_nlp_stats():
    try:
        from src.xwe.core.nlp.monitor import get_nlp_monitor
        monitor = get_nlp_monitor()
        stats = monitor.get_stats()
        return jsonify({"success": True, "stats": stats})
    except ImportError:
        return jsonify({"success": False, "error": "NLP功能未安装或不可用"})
    except Exception as e:
        logger.error(f"获取NLP统计失败: {e}")
        return jsonify({"success": False, "error": str(e)})


@combat_bp.route("/api/nlp/export")
def export_nlp_metrics():
    try:
        from src.xwe.core.nlp.monitor import get_nlp_monitor
        monitor = get_nlp_monitor()
        fd, path = tempfile.mkstemp(suffix=".json")
        try:
            monitor.export_metrics(path)
            with open(path, "rb") as f:
                data = f.read()
            response = make_response(data)
            response.headers["Content-Type"] = "application/json"
            response.headers["Content-Disposition"] = f'attachment; filename=nlp_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            return response
        finally:
            os.close(fd)
            os.unlink(path)
    except ImportError:
        return jsonify({"success": False, "error": "NLP功能未安装或不可用"}), 500
    except Exception as e:
        logger.error(f"导出NLP数据失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@combat_bp.route("/api/nlp/config")
def get_nlp_config():
    try:
        from src.xwe.core.nlp.config import get_nlp_config
        cfg = get_nlp_config()
        safe_config = {
            "enabled": cfg.is_enabled(),
            "provider": cfg.get("provider"),
            "model": cfg.get("model"),
            "cache_size": cfg.get("cache_size"),
            "fallback_enabled": cfg.get("fallback_enabled"),
            "performance_monitoring": cfg.get("performance_monitoring"),
        }
        return jsonify({"success": True, "config": safe_config})
    except ImportError:
        return jsonify({
            "success": True,
            "config": {
                "enabled": False,
                "provider": "none",
                "model": "none",
                "cache_size": 0,
                "fallback_enabled": True,
                "performance_monitoring": False,
            },
        })
    except Exception as e:
        logger.error(f"获取NLP配置失败: {e}")
        return jsonify({"success": False, "error": str(e)})
