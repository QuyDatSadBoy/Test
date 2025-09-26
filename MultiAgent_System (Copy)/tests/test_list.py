"""
Test List by Domain

This module provides a list of all test files organized by domain.
Run specific domains using pytest -m domain_name
"""

# Core API Tests
CORE_TESTS = [
    "test_main.py",  # Basic API health and root endpoint tests
]

# Keyword Domain Tests
KEYWORD_TESTS = [
    "test_keywords/test_create_keyword.py",  # Keyword creation tests
]

# Full test suite
ALL_TESTS = CORE_TESTS + KEYWORD_TESTS

# Test markers for domains
pytest_markers = {
    "core": "Core API functionality tests",
    "keywords": "Keyword domain tests",
}
