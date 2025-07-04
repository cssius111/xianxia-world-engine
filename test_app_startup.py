#!/usr/bin/env python3
"""
Test script to verify Flask app can start without errors.
"""

import sys
import os
from pathlib import Path

# Set up proper path
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

print("Testing Flask application startup...")

try:
    # Import required modules
    from dotenv import load_dotenv
    load_dotenv()
    
    from flask import Flask
    from src.config.game_config import config
    from src.xwe.server.app_factory import create_app
    from src.common.request_utils import is_dev_request
    from src.api.routes import register_all_routes
    
    print("✓ All modules imported successfully")
    
    # Create test app
    log_level = 20  # INFO level
    test_app = create_app(log_level=log_level)
    
    print("✓ Flask app created successfully")
    
    # Test blueprint registration
    with test_app.app_context():
        try:
            register_all_routes(test_app)
            print("✓ All routes registered successfully")
        except Exception as e:
            print(f"❌ Route registration failed: {e}")
            raise
    
    print("\n🎉 Flask application can start successfully!")
    print("🔧 Circular import issue has been resolved!")
    
except Exception as e:
    print(f"\n❌ Application startup failed: {e}")
    import traceback
    traceback.print_exc()
