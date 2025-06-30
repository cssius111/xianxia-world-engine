"""Flask App 工厂"""

from __future__ import annotations

import os
from pathlib import Path
from flask import Flask

from src.xwe.utils.log import configure_logging


def create_app() -> Flask:
    """创建并配置 Flask 应用"""

    configure_logging("logs")

    # 获取项目根目录
    project_root = Path(__file__).resolve().parent.parent.parent
    static_folder = project_root / "static"
    template_folder = project_root / "templates"

    app = Flask(__name__, 
                static_folder=str(static_folder), 
                template_folder=str(template_folder))
    app.secret_key = os.getenv("FLASK_SECRET_KEY", os.getenv("SECRET_KEY", "dev_secret"))
    app.config["JSON_AS_ASCII"] = False
    return app
