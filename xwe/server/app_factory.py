"""Flask App 工厂"""

from __future__ import annotations

import os
from flask import Flask

from xwe.utils.log import configure_logging


def create_app() -> Flask:
    """创建并配置 Flask 应用"""

    configure_logging("logs")

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.getenv("FLASK_SECRET_KEY", os.getenv("SECRET_KEY", "dev_secret"))
    app.config["JSON_AS_ASCII"] = False
    return app

