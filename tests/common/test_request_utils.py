"""
Tests for common request utilities.
"""

import pytest
from flask import Flask
from unittest.mock import Mock, patch

from src.common.request_utils import is_dev_request


class TestIsDevRequest:
    """Test cases for is_dev_request function."""

    def test_is_dev_request_with_dev_query_param_true(self):
        """Test is_dev_request returns True when dev query parameter is 'true'."""
        app = Flask(__name__)
        with app.test_request_context('/?dev=true'):
            assert is_dev_request() is True

    def test_is_dev_request_with_dev_query_param_1(self):
        """Test is_dev_request returns True when dev query parameter is '1'."""
        app = Flask(__name__)
        with app.test_request_context('/?dev=1'):
            assert is_dev_request() is True

    def test_is_dev_request_with_dev_header_true(self):
        """Test is_dev_request returns True when dev header is 'true'."""
        app = Flask(__name__)
        with app.test_request_context('/', headers={'dev': 'true'}):
            assert is_dev_request() is True

    def test_is_dev_request_with_x_dev_mode_header_1(self):
        """Test is_dev_request returns True when X-Dev-Mode header is '1'."""
        app = Flask(__name__)
        with app.test_request_context('/', headers={'X-Dev-Mode': '1'}):
            assert is_dev_request() is True

    def test_is_dev_request_with_dev_header_mixed_case(self):
        """Test is_dev_request returns True when dev header is 'True' (mixed case)."""
        app = Flask(__name__)
        with app.test_request_context('/', headers={'dev': 'True'}):
            assert is_dev_request() is True

    def test_is_dev_request_with_dev_header_uppercase(self):
        """Test is_dev_request returns True when dev header is 'TRUE' (uppercase)."""
        app = Flask(__name__)
        with app.test_request_context('/', headers={'dev': 'TRUE'}):
            assert is_dev_request() is True

    def test_is_dev_request_returns_false_with_dev_false(self):
        """Test is_dev_request returns False when dev parameter is 'false'."""
        app = Flask(__name__)
        with app.test_request_context('/?dev=false'):
            assert is_dev_request() is False

    def test_is_dev_request_returns_false_with_dev_0(self):
        """Test is_dev_request returns False when dev parameter is '0'."""
        app = Flask(__name__)
        with app.test_request_context('/?dev=0'):
            assert is_dev_request() is False

    def test_is_dev_request_returns_false_with_no_dev_param(self):
        """Test is_dev_request returns False when no dev parameter is present."""
        app = Flask(__name__)
        with app.test_request_context('/'):
            assert is_dev_request() is False

    def test_is_dev_request_returns_false_with_empty_dev_param(self):
        """Test is_dev_request returns False when dev parameter is empty."""
        app = Flask(__name__)
        with app.test_request_context('/?dev='):
            assert is_dev_request() is False

    def test_is_dev_request_combination_query_and_header(self):
        """Test is_dev_request returns True when both query param and header are set."""
        app = Flask(__name__)
        with app.test_request_context('/?dev=true', headers={'X-Dev-Mode': '1'}):
            assert is_dev_request() is True

    def test_is_dev_request_header_only(self):
        """Test is_dev_request returns True when only header is set."""
        app = Flask(__name__)
        with app.test_request_context('/', headers={'dev': 'true'}):
            assert is_dev_request() is True

    def test_is_dev_request_query_only(self):
        """Test is_dev_request returns True when only query parameter is set."""
        app = Flask(__name__)
        with app.test_request_context('/?dev=1'):
            assert is_dev_request() is True
