#!/usr/bin/env python3
"""
Comprehensive verification script for HF-002 template path fixes.
"""

import subprocess
import sys
import os
from pathlib import Path

# Change to project directory
os.chdir('/Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine')

print("🔧 Running HF-002 template path fix verification...")
print("=" * 60)

tests = [
    {
        "name": "1. Simple path verification test",
        "command": ["python", "test_simple_fix.py"],
        "expected": "fix verified successfully"
    },
    {
        "name": "2. Template presence unit tests",
        "command": ["python", "-m", "pytest", "tests/web/test_template_presence.py", "-v"],
        "expected": "PASSED"
    },
    {
        "name": "3. Flask app startup with correct paths",
        "command": ["python", "test_app_startup.py"],
        "expected": "Flask application can start successfully"
    }
]

success_count = 0
total_tests = len(tests)

for test in tests:
    print(f"\n{test['name']}:")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            test["command"], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0 and test["expected"] in result.stdout:
            print("✓ PASSED")
            success_count += 1
        else:
            print("❌ FAILED")
            print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)
print(f"📊 SUMMARY: {success_count}/{total_tests} tests passed")

if success_count == total_tests:
    print("🎉 All HF-002 fixes verified successfully!")
    print("✅ Flask template path issue has been completely resolved")
    print("\n📋 What was fixed:")
    print("  • Flask template_folder now points to src/web/templates")
    print("  • Flask static_folder now points to src/web/static")
    print("  • Added comprehensive unit tests for template presence")
    print("  • TemplateNotFound errors should be eliminated")
else:
    print("⚠️  Some tests failed. Please review the output above.")

print("\n🚀 You can now run 'python run.py' to test the application!")
