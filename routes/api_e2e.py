"""
Mock API endpoints for E2E testing
These endpoints provide basic implementations for features that may not be fully implemented yet
"""

from flask import Blueprint, jsonify, request, session
import time
import uuid
import json
from pathlib import Path
from datetime import datetime

bp = Blueprint('api_e2e', __name__, url_prefix='/api')

# In-memory storage for async tasks
async_tasks = {}

# In-memory state storage
current_state = {"state": "IDLE"}
state_log_file = Path("logs/state_transitions.log")

@bp.route('/config', methods=['GET'])
def get_config():
    """Return configuration for E2E tests"""
    return jsonify({
        "PORT": 5001,
        "TTL": 300,
        "LOG_MAX_BYTES": 1048576,
        "CACHE_SIZE": 1000,
        "DATA_CACHE_TTL": 300,
        "SMART_CACHE_TTL": 300
    })

@bp.route('/explore_async', methods=['POST'])
def explore_async():
    """Create an async exploration task"""
    data = request.get_json()
    location = data.get('location', '未知地点')
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Store task
    async_tasks[task_id] = {
        "id": task_id,
        "status": "pending",
        "location": location,
        "created_at": time.time(),
        "result": None
    }
    
    # Simulate async processing (in real implementation, this would be a background task)
    def complete_task():
        time.sleep(0.2)  # Simulate processing time
        async_tasks[task_id]["status"] = "done"
        async_tasks[task_id]["result"] = {
            "narration": f"你在{location}探索，发现了一些有趣的东西。",
            "reward": {
                "gold": 10,
                "exp": 50,
                "items": [{"name": "灵石", "quantity": 1}]
            }
        }
    
    # In a real implementation, this would be done in a background thread/process
    import threading
    threading.Thread(target=complete_task, daemon=True).start()
    
    return jsonify({
        "task_id": task_id,
        "status": "pending",
        "message": f"开始探索{location}..."
    })

@bp.route('/explore_status/<task_id>', methods=['GET'])
def explore_status(task_id):
    """Check the status of an async exploration task"""
    task = async_tasks.get(task_id)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    response = {
        "task_id": task_id,
        "status": task["status"]
    }
    
    if task["status"] == "done" and task["result"]:
        response.update(task["result"])
    
    return jsonify(response)

@bp.route('/state', methods=['POST'])
def update_state():
    """Update game state and log transitions"""
    global current_state
    
    data = request.get_json()
    new_state = data.get('state')
    action = data.get('action', '')
    
    if not new_state:
        return jsonify({"error": "State is required"}), 400
    
    # Log state transition
    transition = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "from": current_state["state"],
        "to": new_state,
        "state": {"current": new_state}
    }
    
    # Ensure log directory exists
    state_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to log file
    with open(state_log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(transition, ensure_ascii=False) + '\n')
    
    # Update current state
    current_state["state"] = new_state
    
    return jsonify({
        "success": True,
        "previous_state": transition["from"],
        "current_state": new_state,
        "action": action
    })

@bp.route('/data/lore', methods=['GET'])
def get_lore_data():
    """Get lore data with caching simulation"""
    # Add cache headers to simulate caching behavior
    response = jsonify({
        "world": {
            "name": "玄苍界",
            "description": "一个充满灵气的修仙世界",
            "regions": [
                {"name": "东玄州", "description": "剑修圣地"},
                {"name": "南离州", "description": "丹药之乡"},
                {"name": "西极州", "description": "体修之地"},
                {"name": "北冥州", "description": "冰雪之境"}
            ]
        },
        "timestamp": time.time()
    })
    
    # Simulate cache headers
    response.headers['Cache-Control'] = 'max-age=300'
    response.headers['X-Cache-TTL'] = '300'
    
    return response

# Register blueprint
def register_e2e_routes(app):
    """Register E2E test routes with the Flask app"""
    app.register_blueprint(bp)
    print("✅ E2E test API endpoints registered")
