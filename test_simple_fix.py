#!/usr/bin/env python3
"""
Simple verification script to test the path fix.
"""

import sys
import os
from pathlib import Path

# Set up proper path
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

print("🔧 Testing HF-002 path fix...")
print("=" * 50)

try:
    from src.xwe.server.app_factory import create_app
    
    # Create Flask app
    app = create_app()
    
    print("✅ Flask app created successfully")
    print(f"📁 Template folder: {app.template_folder}")
    print(f"📁 Static folder: {app.static_folder}")
    
    # Check if paths exist
    template_path = Path(app.template_folder)
    static_path = Path(app.static_folder)
    
    print(f"\n📋 Path validation:")
    print(f"   Templates exist: {'✅' if template_path.exists() else '❌'} {template_path}")
    print(f"   Static exist: {'✅' if static_path.exists() else '❌'} {static_path}")
    
    # Check for the main template
    main_template = template_path / "game_enhanced_optimized_v2.html"
    base_template = template_path / "base.html"
    
    print(f"\n🎯 Key templates:")
    print(f"   Main template: {'✅' if main_template.exists() else '❌'} {main_template.name}")
    print(f"   Base template: {'✅' if base_template.exists() else '❌'} {base_template.name}")
    
    # Test template loading
    with app.app_context():
        try:
            template_source, template_filename = app.jinja_loader.get_source(
                app.jinja_env, 'base.html'
            )
            print(f"\n🎉 Template loading: ✅ SUCCESS")
            print(f"   Loaded from: {template_filename}")
        except Exception as e:
            print(f"\n❌ Template loading: FAILED - {e}")
            sys.exit(1)
    
    print(f"\n🚀 HF-002 fix verified successfully!")
    print(f"   Template path issue has been resolved!")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
