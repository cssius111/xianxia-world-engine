#!/usr/bin/env python3
"""
Test script to verify HF-002 template path fixes.
"""

import sys
import os
from pathlib import Path

# Set up proper path
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

print("🔧 Testing HF-002 template path fixes...")
print("=" * 60)

def test_template_paths():
    """Test that template and static paths are correctly configured."""
    
    try:
        from src.xwe.server.app_factory import create_app
        
        # Create Flask app
        app = create_app()
        
        print("1. Flask app configuration:")
        print(f"   Template folder: {app.template_folder}")
        print(f"   Static folder: {app.static_folder}")
        
        # Check paths exist
        template_path = Path(app.template_folder)
        static_path = Path(app.static_folder)
        
        print(f"\n2. Path existence check:")
        print(f"   Templates exist: {template_path.exists()}")
        print(f"   Static files exist: {static_path.exists()}")
        
        # Check key templates
        main_template = template_path / "game_enhanced_optimized_v2.html"
        intro_template = template_path / "intro_optimized.html"
        base_template = template_path / "base.html"
        
        print(f"\n3. Key templates check:")
        print(f"   Main game template: {main_template.exists()}")
        print(f"   Intro template: {intro_template.exists()}")
        print(f"   Base template: {base_template.exists()}")
        
        # Check key static directories
        css_dir = static_path / "css"
        js_dir = static_path / "js"
        
        print(f"\n4. Key static directories:")
        print(f"   CSS directory: {css_dir.exists()}")
        print(f"   JS directory: {js_dir.exists()}")
        
        # Test template loading
        print(f"\n5. Template loading test:")
        with app.app_context():
            try:
                template_source, template_filename = app.jinja_loader.get_source(
                    app.jinja_env, 'base.html'
                )
                print(f"   ✓ Base template loads successfully")
                print(f"   Template file: {template_filename}")
            except Exception as e:
                print(f"   ❌ Template loading failed: {e}")
                return False
        
        # Verify paths are correct
        if (template_path.exists() and static_path.exists() and 
            main_template.exists() and str(template_path).endswith("src/web/templates")):
            print(f"\n🎉 All HF-002 fixes verified successfully!")
            print(f"✅ Flask template path issue has been resolved")
            return True
        else:
            print(f"\n❌ Some checks failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_render_template():
    """Test that templates can be rendered without TemplateNotFound errors."""
    
    try:
        from flask import render_template
        from src.xwe.server.app_factory import create_app
        
        app = create_app()
        
        print(f"\n6. Template rendering test:")
        with app.app_context():
            # Test rendering a simple template
            try:
                # We'll just test template loading, not full rendering to avoid dependencies
                template = app.jinja_env.get_template('base.html')
                print(f"   ✓ Base template can be loaded and parsed")
                return True
            except Exception as e:
                print(f"   ❌ Template rendering failed: {e}")
                return False
                
    except Exception as e:
        print(f"   ❌ Template rendering test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_template_paths()
    success2 = test_render_template()
    
    if success1 and success2:
        print(f"\n🚀 HF-002 verification: ALL PASSED")
        sys.exit(0)
    else:
        print(f"\n⚠️  HF-002 verification: SOME TESTS FAILED")
        sys.exit(1)
