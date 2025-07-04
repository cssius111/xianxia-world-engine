#!/usr/bin/env python3
"""
Final verification of HF-002 template path fixes.
"""

import subprocess
import sys
import os

print("🔧 Final HF-002 Template Path Fix Verification")
print("=" * 55)

# Change to project directory
os.chdir('/Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine')

def run_test(name, command, expected_text):
    """Run a single test and return success status."""
    print(f"\n{name}:")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        success = result.returncode == 0 and expected_text in result.stdout
        
        if success:
            print("✅ PASSED")
            return True
        else:
            print("❌ FAILED")
            print("STDOUT:", result.stdout[:300] + "..." if len(result.stdout) > 300 else result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

# Run all tests
tests_passed = 0
total_tests = 3

# Test 1: Simple path verification
tests_passed += run_test(
    "1. Simple Path Verification",
    ["python", "test_simple_fix.py"],
    "fix verified successfully"
)

# Test 2: Unit tests
tests_passed += run_test(
    "2. Unit Tests",
    ["python", "-m", "pytest", "tests/web/test_template_presence.py", "-q"],
    "passed"
)

# Test 3: App startup
tests_passed += run_test(
    "3. Flask App Startup",
    ["python", "test_app_startup.py"],
    "Flask application can start successfully"
)

# Summary
print("\n" + "=" * 55)
print(f"📊 FINAL SUMMARY: {tests_passed}/{total_tests} tests passed")

if tests_passed == total_tests:
    print("🎉 HF-002 COMPLETELY FIXED!")
    print("✅ All template path issues resolved")
    print("🚀 Ready to run: python run.py")
else:
    print("⚠️  Some tests still failing")
    print("🔍 Please check the output above")

print("=" * 55)
