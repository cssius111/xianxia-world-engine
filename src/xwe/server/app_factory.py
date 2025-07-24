"""Flask App 工厂"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from flask import Flask, session

from src.xwe.utils.log import configure_logging


def create_app(log_level: int = logging.INFO) -> Flask:
    """创建并配置 Flask 应用"""

    configure_logging("logs", level=log_level)

    # 获取项目根目录（修复：需要多往上一层才是真正的项目根目录）
    # __file__ = src/xwe/server/app_factory.py
    # .parent.parent.parent = src/
    # .parent.parent.parent.parent = 项目根目录/
    project_root = Path(__file__).resolve().parent.parent.parent.parent

    # 模板和静态文件路径 - 指向 src/web/ 目录
    static_folder = project_root / "src" / "web" / "static"
    template_folder = project_root / "src" / "web" / "templates"

    app = Flask(
        __name__, static_folder=str(static_folder), template_folder=str(template_folder)
    )
    app.secret_key = os.getenv(
        "FLASK_SECRET_KEY", os.getenv("SECRET_KEY", "dev_secret")
    )
    app.config["JSON_AS_ASCII"] = False

    @app.context_processor
    def inject_dev_mode() -> dict:
        """Provide developer mode state to templates."""
        return {"dev_mode": session.get("dev", False)}

    return app
