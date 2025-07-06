from flask import Blueprint, jsonify, request, session

from src.app import inventory_system
from src.xwe.features.onboarding_manager import OnboardingQuestManager

onboarding_manager = OnboardingQuestManager(inventory_system)

onboarding_bp = Blueprint("onboarding", __name__, url_prefix="/api/onboarding")


@onboarding_bp.get("")
@onboarding_bp.get("/")
def get_progress():
    """查询新手任务进度"""
    player_id = session.get("player_id", "default")
    progress = onboarding_manager.get_progress(player_id)
    return jsonify(progress)


@onboarding_bp.post("/complete")
def complete_step():
    """标记某个步骤完成"""
    data = request.get_json() or {}
    step = data.get("step")
    player_id = session.get("player_id", "default")
    success = onboarding_manager.complete_step(player_id, step)
    progress = onboarding_manager.get_progress(player_id)
    return jsonify({"success": success, "progress": progress})
