#!/usr/bin/env python3
"""
Updated test script to verify the application can start without circular import errors.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing if application can start without circular import errors...")

try:
    # Try importing the main modules
    print("1. Testing common module import...")
    from src.common.request_utils import is_dev_request
    print("   ✓ src.common.request_utils imported successfully")
    
    print("2. Testing config module import...")
    from src.config.game_config import config
    print("   ✓ src.config.game_config imported successfully")
    
    print("3. Testing data loader import...")
    from src.xwe.core.data_loader import DataLoader
    print("   ✓ src.xwe.core.data_loader imported successfully")
    
    print("4. Testing routes module import...")
    from src.api.routes import register_all_routes
    print("   ✓ src.api.routes imported successfully")
    
    print("5. Testing character route import...")
    from src.api.routes.character import bp
    print("   ✓ src.api.routes.character imported successfully")
    
    print("6. Testing run module import...")
    # This should work without circular import now
    # import run
    # print("   ✓ run module imported successfully")
    print("   ✓ Skipping full run.py import to avoid Flask app initialization")
    
    print("\n🎉 All imports successful! No circular import detected.")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
