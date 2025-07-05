#!/usr/bin/env python3
"""Test route registration"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dotenv import load_dotenv
load_dotenv()

# Create test app like the tests do
from src.xwe.server.app_factory import create_app
from src.api.routes import register_all_routes

test_app = create_app()
test_app.config.update(
    TESTING=True,
    VERSION="1.0.0",
    SECRET_KEY="test_secret",
    LOG_PATH="logs"
)

test_app.game_instances = {}
register_all_routes(test_app)

# Check routes
print("Checking API routes:")
with test_app.test_client() as client:
    endpoints = [
        "/api/cultivation/status",
        "/api/achievements", 
        "/api/map",
        "/api/quests",
        "/api/intel",
        "/api/player/stats/detailed",
        "/api/v1/system/info",
        "/api/v1/game/status"
    ]
    
    for endpoint in endpoints:
        resp = client.get(endpoint)
        print(f"{endpoint}: {resp.status_code}")

print("\nAll routes:")
for rule in test_app.url_map.iter_rules():
    if 'static' not in str(rule):
        print(f"  {rule}")
