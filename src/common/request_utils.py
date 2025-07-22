"""
Common request utilities.
"""

from flask import request, current_app, session


def is_dev_request() -> bool:
    """检查请求是否开启开发模式"""
    if not current_app.config.get("DEV_PASSWORD"):
        return False
    if session.get("dev") is True:
        return True
    return (
        request.args.get("dev") == "true"
        or str(request.headers.get("dev", "")).lower() == "true"
        or request.args.get("dev") == "1"
        or request.headers.get("X-Dev-Mode") == "1"
    )
