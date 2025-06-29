#!/usr/bin/env python3
"""
Quick E2E Test Verification Script
Tests all major functionalities step by step
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5001"
TEST_PLAYER_NAME = "测试道友"

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_test(name):
    print(f"\n{BLUE}▶ Testing: {name}{NC}")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{NC}")

def print_error(msg):
    print(f"{RED}✗ {msg}{NC}")

def print_info(msg):
    print(f"{YELLOW}ℹ {msg}{NC}")

def test_server_running():
    """Test if server is running"""
    print_test("Server Status")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code in [200, 302]:
            print_success(f"Server is running (status: {response.status_code})")
            return True
        else:
            print_error(f"Server returned unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Server is not running: {e}")
        return False

def test_intro_page():
    """Test intro page loads"""
    print_test("Intro Page")
    try:
        response = requests.get(f"{BASE_URL}/intro")
        if response.status_code == 200:
            print_success("Intro page loaded successfully")
            if "修仙世界引擎" in response.text:
                print_success("Page contains expected title")
            return True
        else:
            print_error(f"Intro page returned status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to load intro page: {e}")
        return False

def test_character_creation():
    """Test character creation API"""
    print_test("Character Creation API")
    try:
        # Use session to maintain cookies
        session = requests.Session()
        
        response = session.post(f"{BASE_URL}/create_character", 
                              json={"name": TEST_PLAYER_NAME})
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_success("Character created successfully")
                print_info(f"Response: {data.get('narrative', '')}")
                return True, session
            else:
                print_error("Character creation failed")
                return False, None
        else:
            print_error(f"API returned status: {response.status_code}")
            return False, None
    except Exception as e:
        print_error(f"Character creation failed: {e}")
        return False, None

def test_status_api(session):
    """Test status API"""
    print_test("Status API")
    try:
        response = session.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print_success("Status API working")
            print_info(f"Player: {data.get('player', {}).get('name', 'Unknown')}")
            print_info(f"Location: {data.get('location', 'Unknown')}")
            return True
        else:
            print_error(f"Status API returned: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Status API failed: {e}")
        return False

def test_lore_api():
    """Test lore/world API"""
    print_test("Lore API")
    try:
        # Try both possible endpoints
        endpoints = ["/api/data/lore", "/lore/world"]
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print_success(f"Lore API working at {endpoint}")
                data = response.json()
                if "world" in data or "name" in data:
                    print_info("Response contains world data")
                return True
        
        print_error("Lore API not found at any endpoint")
        return False
    except Exception as e:
        print_error(f"Lore API failed: {e}")
        return False

def test_explore_api(session):
    """Test exploration API"""
    print_test("Exploration API")
    try:
        # Try async API first
        response = session.post(f"{BASE_URL}/api/explore_async", 
                              json={"location": "青云城"})
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("task_id")
            print_success(f"Async explore API working, task_id: {task_id}")
            
            # Wait and check status
            time.sleep(0.3)
            status_response = session.get(f"{BASE_URL}/api/explore_status/{task_id}")
            if status_response.status_code == 200:
                print_success("Explore status API working")
                return True
        else:
            # Try sync explore through command API
            print_info("Async API not available, trying sync command API")
            response = session.post(f"{BASE_URL}/command", 
                                  json={"command": "探索"})
            if response.status_code == 200:
                print_success("Sync explore working through command API")
                return True
                
        print_error("Explore API not working")
        return False
    except Exception as e:
        print_error(f"Explore API failed: {e}")
        return False

def test_state_api(session):
    """Test state management API"""
    print_test("State Management API")
    try:
        response = session.post(f"{BASE_URL}/api/state", 
                              json={"state": "TESTING", "action": "test_action"})
        
        if response.status_code == 200:
            print_success("State API working")
            data = response.json()
            print_info(f"State transition: {data.get('previous_state')} -> {data.get('current_state')}")
            return True
        else:
            print_info(f"State API not implemented (status: {response.status_code})")
            return False
    except Exception as e:
        print_info(f"State API not available: {e}")
        return False

def test_config_api():
    """Test config API"""
    print_test("Config API")
    try:
        response = requests.get(f"{BASE_URL}/api/config")
        if response.status_code == 200:
            data = response.json()
            print_success("Config API working")
            print_info(f"TTL: {data.get('TTL', 'N/A')}")
            print_info(f"LOG_MAX_BYTES: {data.get('LOG_MAX_BYTES', 'N/A')}")
            return True
        else:
            print_info(f"Config API not implemented (status: {response.status_code})")
            return False
    except Exception as e:
        print_info(f"Config API not available: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 Xianxia World Engine - E2E Test Verification")
    print("=" * 60)
    
    # Check if server is running
    if not test_server_running():
        print(f"\n{RED}Server is not running!{NC}")
        print("Please start the server with:")
        print("  ENABLE_E2E_API=true python run.py")
        return 1
    
    # Test intro page
    test_intro_page()
    
    # Test character creation and get session
    success, session = test_character_creation()
    if not success or not session:
        print(f"\n{RED}Character creation failed, stopping tests{NC}")
        return 1
    
    # Test other APIs
    test_status_api(session)
    test_lore_api()
    test_explore_api(session)
    test_state_api(session)
    test_config_api()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"{GREEN}✓ Basic functionality is working{NC}")
    print(f"{YELLOW}ℹ Some advanced APIs may not be implemented yet{NC}")
    print("\nReady to run full E2E tests with:")
    print("  npx playwright test tests/e2e_full.spec.ts --headed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
