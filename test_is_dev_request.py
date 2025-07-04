#!/usr/bin/env python3
"""
Simple test script to verify is_dev_request function works.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.common.request_utils import is_dev_request

def test_is_dev_request():
    """Test the is_dev_request function."""
    app = Flask(__name__)
    
    # Test with dev=true query parameter
    with app.test_request_context('/?dev=true'):
        assert is_dev_request() is True
        print("✓ Test with dev=true query parameter passed")
    
    # Test with dev=1 query parameter
    with app.test_request_context('/?dev=1'):
        assert is_dev_request() is True
        print("✓ Test with dev=1 query parameter passed")
    
    # Test with X-Dev-Mode header
    with app.test_request_context('/', headers={'X-Dev-Mode': '1'}):
        assert is_dev_request() is True
        print("✓ Test with X-Dev-Mode header passed")
    
    # Test with dev header
    with app.test_request_context('/', headers={'dev': 'true'}):
        assert is_dev_request() is True
        print("✓ Test with dev header passed")
    
    # Test with no dev parameter
    with app.test_request_context('/'):
        assert is_dev_request() is False
        print("✓ Test with no dev parameter passed")
    
    # Test with dev=false
    with app.test_request_context('/?dev=false'):
        assert is_dev_request() is False
        print("✓ Test with dev=false parameter passed")
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_is_dev_request()
