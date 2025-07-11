#!/usr/bin/env python3
"""Run async unit tests for DeepSeek client."""

import subprocess
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_tests():
    """Run the async unit tests."""
    print("Running DeepSeek async unit tests...")
    print("=" * 60)
    
    # Run pytest for async tests
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/test_deepseek_async.py",
        "-v",
        "--tb=short",
        "-k", "not real_api"  # Skip tests requiring real API key
    ]
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
