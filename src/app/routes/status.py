"""Status routes for the main app."""

from flask import Blueprint, jsonify
from .. import build_status_data, logger

status_bp = Blueprint("status", __name__)


@status_bp.route("/status")
def get_status():
    """Get game status - root level endpoint."""
    status_dict = build_status_data()
    logger.debug("[STATUS] Root level status endpoint: %s", status_dict)
    return jsonify(status_dict)
