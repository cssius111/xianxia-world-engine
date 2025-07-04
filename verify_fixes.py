#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

# Change to project directory  
os.chdir('/Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine')

print("🔧 Running HF-001 fix verification tests...")
print("=" * 60)

tests = [
    {
        "name": "1. is_dev_request function test",
        "command": ["python", "test_is_dev_request.py"],
        "expected": "All tests passed!"
    },
    {
        "name": "2. Import chain test", 
        "command": ["python", "test_imports.py"],
        "expected": "All imports successful"
    },
    {
        "name": "3. App startup test",
        "command": ["python", "test_app_startup.py"], 
        "expected": "Flask application can start successfully"
    },
    {
        "name": "4. Unit test execution",
        "command": ["python", "-m", "pytest", "tests/common/test_request_utils.py", "-v"],
        "expected": "PASSED"
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
            print("STDERR:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)
print(f"📊 SUMMARY: {success_count}/{total_tests} tests passed")

if success_count == total_tests:
    print("🎉 All HF-001 fixes verified successfully!")
    print("✅ Circular import issue has been completely resolved")
else:
    print("⚠️  Some tests failed. Please review the output above.")
