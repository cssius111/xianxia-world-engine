from flask import Blueprint, request, jsonify, session, current_app

from .. import logger


dev_bp = Blueprint("dev", __name__)


@dev_bp.route("/dev_login", methods=["POST"])
def dev_login():
    """Authenticate developer mode using DEV_PASSWORD."""
    dev_password = current_app.config.get("DEV_PASSWORD")
    if not dev_password:
        return (
            jsonify({"success": False, "error": "DEV_PASSWORD not configured"}),
            403,
        )
    data = request.get_json() or {}
    if data.get("password") == dev_password:
        session["dev"] = True
        logger.info("Developer mode enabled via login")
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid password"}), 401


@dev_bp.route("/dev_logout", methods=["POST"])
def dev_logout():
    """Disable developer mode by clearing the session flag."""
    if session.pop("dev", None):
        logger.info("Developer mode disabled via logout")
    return jsonify({"success": True})
