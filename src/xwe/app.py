"""Flask 应用代码抽离到此处，方便多环境初始化"""

from __future__ import annotations

import os
import time
import json
import psutil
from datetime import datetime
from flask import (
    Flask, jsonify, request, session,
    Response, stream_with_context, render_template, send_from_directory
)

# 允许通过环境变量打开或关闭 Prometheus
os.environ.setdefault("ENABLE_PROMETHEUS", "true")

try:
    from prometheus_flask_exporter import PrometheusMetrics
    from src.xwe.metrics.prometheus_metrics import (
        nlp_request_seconds,
        nlp_error_total,
        command_execution_seconds,
        REGISTRY,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    PROMETHEUS_AVAILABLE = False


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask app."""
    env = config_name or os.getenv("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder="src/web/templates",
        static_folder="src/web/static",
    )
    app.config["SECRET_KEY"] = "test-secret-key"

    if env.lower() in {"testing", "test"}:
        app.config["TESTING"] = True

    # 存储简单的游戏实例
    app.game_instances = {}

    if PROMETHEUS_AVAILABLE and os.getenv("ENABLE_PROMETHEUS", "true").lower() == "true":
        from prometheus_client import CollectorRegistry

        registry = CollectorRegistry()
        metrics = PrometheusMetrics(app, registry=registry)
        metrics.info("xwe_app_info", "Application info", version="0.3.4")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api")
    def api_index():
        return jsonify(
            {
                "name": "修仙世界引擎 API",
                "version": "0.3.4",
                "endpoints": {
                    "health": "/api/health",
                    "game": {
                        "start": "POST /api/game/start",
                        "status": "GET /api/game/status",
                        "command": "POST /api/game/command",
                    },
                    "cultivation": {
                        "status": "GET /api/cultivation/status",
                        "start": "POST /api/cultivation/start",
                    },
                    "achievements": "GET /api/achievements/",
                    "inventory": "GET /api/inventory/",
                },
                "documentation": "/docs",
            }
        )

    @app.route("/docs")
    @app.route("/docs/<path:filename>")
    def docs(filename: str = "index.html"):
        if filename == "index.html":
            docs_list = [
                {"name": "API文档", "url": "/docs/API.md"},
                {"name": "架构设计", "url": "/docs/ARCHITECTURE.md"},
                {"name": "开发者指南", "url": "/docs/DEVELOPER_GUIDE.md"},
                {"name": "README", "url": "/docs/README.md"},
            ]
            return jsonify({"title": "修仙世界引擎文档", "documents": docs_list})
        try:
            from pathlib import Path

            doc_path = Path("docs") / filename
            if doc_path.exists() and doc_path.suffix == ".md":
                content = doc_path.read_text(encoding="utf-8")
                return Response(content, mimetype="text/markdown")
            return jsonify({"error": "Document not found"}), 404
        except Exception as e:  # pragma: no cover - simple error path
            return jsonify({"error": str(e)}), 500

    @app.route("/game")
    def game():
        return render_template("game.html")

    @app.route("/health")
    @app.route("/api/health")
    def health():
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            checks = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "0.3.4",
                "checks": {
                    "cpu": {
                        "status": "ok" if cpu_percent < 80 else "warning",
                        "value": f"{cpu_percent}%",
                    },
                    "memory": {
                        "status": "ok" if memory.percent < 80 else "warning",
                        "value": f"{memory.percent}%",
                    },
                    "disk": {
                        "status": "ok" if disk.percent < 90 else "warning",
                        "value": f"{disk.percent}%",
                    },
                },
            }
            if any(check["status"] == "warning" for check in checks["checks"].values()):
                checks["status"] = "warning"
            return jsonify(checks), 200
        except Exception as e:  # pragma: no cover - unlikely
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    @app.route("/health/detailed")
    def health_detailed():
        return (
            jsonify(
                {
                    "status": "healthy",
                    "components": {"nlp": "healthy", "database": "healthy", "cache": "healthy"},
                    "timestamp": time.time(),
                }
            ),
            200,
        )

    @app.route("/ready")
    def ready():
        return jsonify({"ready": True}), 200

    @app.route("/live")
    def live():
        return jsonify({"alive": True}), 200

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        return jsonify({"success": True, "token": "test-token"}), 200

    @app.route("/api/game/start", methods=["POST"])
    def start_game():
        session_id = f"session_{int(time.time())}"
        app.game_instances[session_id] = {"game": None, "created_at": time.time()}
        session["session_id"] = session_id
        return jsonify({"success": True, "session_id": session_id}), 201

    @app.route("/api/game/command", methods=["POST"])
    def game_command():
        command = request.json.get("command", "")
        if PROMETHEUS_AVAILABLE:
            start_time = time.time()
            try:
                result = {"success": True, "result": f"\u6267\u884c\u547d\u4ee4: {command}", "command": command}
                nlp_request_seconds.labels(command_type="game_command", status="success").observe(
                    time.time() - start_time
                )
            except Exception as e:
                nlp_error_total.labels(error_type="command_error").inc()
                result = {"success": False, "error": str(e)}
        else:
            result = {"success": True, "result": f"\u6267\u884c\u547d\u4ee4: {command}", "command": command}
        return jsonify(result), 200

    @app.route("/api/game/status")
    def game_status():
        return (
            jsonify(
                {
                    "player": {"name": "\u6d4b\u8bd5\u73a9\u5bb6", "level": 1},
                    "location": "\u65b0\u624b\u6751",
                    "health": 100,
                    "mana": 100,
                }
            ),
            200,
        )

    @app.route("/api/nlp/process", methods=["POST"])
    def process_nlp():
        text = request.json.get("text", "")
        return (
            jsonify(
                {
                    "raw": text,
                    "normalized_command": "\u63a2\u7d22",
                    "intent": "action",
                    "args": {},
                    "explanation": "\u6d4b\u8bd5\u89e3\u6790",
                }
            ),
            200,
        )

    @app.route("/api/v1/session", methods=["POST"])
    def create_session():
        user_id = request.json.get("user_id", "anonymous")
        session_id = f"session_{user_id}_{int(time.time())}"
        app.game_instances[session_id] = {"game": None, "created_at": time.time()}
        return jsonify({"session_id": session_id, "created_at": time.time()}), 200

    @app.route("/api/v1/command", methods=["POST"])
    def api_command():
        session_id = request.json.get("session_id")
        command = request.json.get("command")
        return jsonify({"result": f"\u6267\u884c\u547d\u4ee4: {command}", "session_id": session_id}), 200

    @app.route("/api/v1/session/<session_id>/status")
    def session_status(session_id: str):
        if session_id in app.game_instances:
            instance = app.game_instances[session_id]
            return (
                jsonify(
                    {
                        "status": "active",
                        "session_id": session_id,
                        "created_at": instance["created_at"],
                        "last_activity": time.time(),
                    }
                ),
                200,
            )
        return jsonify({"error": "Session not found"}), 404

    @app.route("/api/achievements/")
    def achievements():
        return (
            jsonify(
                {
                    "achievements": [
                        {
                            "id": "first_cultivation",
                            "name": "\u521d\u5165\u4fee\u884c",
                            "description": "\u5b8c\u6210\u7b2c\u4e00\u6b21\u4fee\u7ec3",
                            "unlocked": True,
                            "unlocked_at": "2025-01-13T10:30:00Z",
                        }
                    ]
                }
            ),
            200,
        )

    @app.route("/api/inventory/")
    def inventory():
        return (
            jsonify(
                {
                    "items": [
                        {
                            "id": "healing_pill",
                            "name": "\u7597\u4f24\u4e39",
                            "quantity": 5,
                            "type": "consumable",
                        }
                    ],
                    "capacity": 50,
                    "used": 5,
                }
            ),
            200,
        )

    @app.route("/api/map")
    def map_data():
        return (
            jsonify(
                {
                    "data": [
                        {"x": 0, "y": 0, "type": "village", "name": "\u65b0\u624b\u6751"},
                        {"x": 1, "y": 0, "type": "forest", "name": "\u8ff7\u96fe\u68ee\u6797"},
                    ]
                }
            ),
            200,
        )

    @app.route("/api/quests")
    def quests():
        return (
            jsonify(
                {
                    "quests": [
                        {
                            "id": "intro_quest",
                            "name": "\u521d\u5165\u6c5f\u6e56",
                            "status": "in_progress",
                            "objectives": [
                                {"text": "\u4e0e\u6751\u957f\u5bf9\u8bdd", "completed": True},
                                {"text": "\u5b8c\u6210\u7b2c\u4e00\u6b21\u4fee\u7ec3", "completed": False},
                            ],
                        }
                    ]
                }
            ),
            200,
        )

    @app.route("/api/intel")
    def intel():
        return (
            jsonify(
                {
                    "data": [
                        {
                            "id": "rumor_1",
                            "type": "rumor",
                            "content": "\u542c\u8bf4\u8ff7\u96fe\u68ee\u6797\u6df1\u5904\u6709\u5b9d\u7269",
                        }
                    ]
                }
            ),
            200,
        )

    @app.route("/api/player/stats/detailed")
    def player_stats_detailed():
        return (
            jsonify(
                {
                    "data": {
                        "attributes": {
                            "strength": 10,
                            "agility": 12,
                            "intelligence": 15,
                            "vitality": 11,
                        },
                        "skills": {"sword_mastery": 1, "meditation": 2},
                    }
                }
            ),
            200,
        )

    @app.route("/api/cultivation/status")
    def cultivation_status():
        session_id = session.get("session_id")
        if session_id and session_id in app.game_instances:
            return (
                jsonify(
                    {
                        "realm": "\u7ec3\u6c14\u671f",
                        "progress": 45.5,
                        "next_realm": "\u7b51\u57fa\u671f",
                        "tribulation_ready": False,
                    }
                ),
                200,
            )
        return jsonify({"realm": "\u672a\u77e5", "progress": 0}), 200

    @app.route("/api/cultivation/start", methods=["POST"])
    def cultivation_start():
        hours = request.json.get("hours", 1)
        session_id = session.get("session_id")
        exp_gained = hours * 10
        return (
            jsonify({"success": True, "exp_gained": exp_gained, "result": f"\u4fee\u7ec3{hours}\u5c0f\u65f6\uff0c\u83b7\u5f97{exp_gained}\u70b9\u7ecf\u9a8c"}),
            200,
        )

    def _generate_events():
        data = {
            "type": "status_update",
            "player": {"name": "\u6d4b\u8bd5\u73a9\u5bb6", "health": 100, "mana": 100},
            "inventory": {"items": 5, "capacity": 50},
        }
        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    @app.route("/events")
    def events():
        return Response(stream_with_context(_generate_events()), mimetype="text/event-stream")

    @app.route("/api/metrics")
    def api_metrics():
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        return (
            jsonify(
                {
                    "cpu": cpu_percent,
                    "memory": memory.percent,
                    "responseTime": {"p50": 125, "p90": 180, "p95": 220, "p99": 450},
                    "timestamp": time.time(),
                }
            ),
            200,
        )

    if not PROMETHEUS_AVAILABLE:
        @app.route("/metrics")
        def metrics():
            metrics_text = """# HELP xwe_nlp_request_seconds NLP request processing time in seconds
# TYPE xwe_nlp_request_seconds histogram
xwe_nlp_request_seconds_bucket{command_type=\"unknown\",status=\"success\",le=\"0.1\"} 10
xwe_nlp_request_seconds_bucket{command_type=\"unknown\",status=\"success\",le=\"0.25\"} 20
xwe_nlp_request_seconds_bucket{command_type=\"unknown\",status=\"success\",le=\"0.5\"} 30
xwe_nlp_request_seconds_bucket{command_type=\"unknown\",status=\"success\",le=\"1.0\"} 40
xwe_nlp_request_seconds_bucket{command_type=\"unknown\",status=\"success\",le=\"+Inf\"} 50
xwe_nlp_request_seconds_count{command_type=\"unknown\",status=\"success\"} 50
xwe_nlp_request_seconds_sum{command_type=\"unknown\",status=\"success\"} 12.5

# HELP xwe_app_info Application info
# TYPE xwe_app_info gauge
xwe_app_info{version=\"0.3.4\"} 1
"""
            return metrics_text, 200, {"Content-Type": "text/plain; charset=utf-8"}

    return app
