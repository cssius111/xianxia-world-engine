#!/usr/bin/env python3
"""Debug test failures"""

# Setup the environment just like the tests do
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dotenv import load_dotenv
load_dotenv()

# Now let's check what happens when we create the app
print("Creating app from run.py...")
try:
    from run import app
    print("✓ App created successfully")
    
    # Print all registered routes
    print("\nRegistered routes:")
    print("-" * 60)
    routes = []
    for rule in app.url_map.iter_rules():
        if 'static' not in str(rule):  # Skip static files
            routes.append(str(rule))
    
    # Sort and print routes
    for route in sorted(routes):
        print(f"  {route}")
    
    # Check specific routes that are failing in tests
    print("\nChecking test endpoints:")
    test_endpoints = [
        "/api/cultivation/status",
        "/api/achievements",
        "/api/map",
        "/api/quests", 
        "/api/intel",
        "/api/player/stats/detailed",
        "/api/v1/system/info",
        "/api/v1/game/status"
    ]
    
    for endpoint in test_endpoints:
        # Try to find matching rule
        found = False
        for rule in app.url_map.iter_rules():
            if str(rule) == endpoint:
                found = True
                break
        print(f"  {endpoint}: {'✓ Found' if found else '✗ NOT FOUND'}")
        
except Exception as e:
    print(f"✗ Error creating app: {e}")
    import traceback
    traceback.print_exc()
