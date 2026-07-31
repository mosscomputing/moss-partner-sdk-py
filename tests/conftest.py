"""Pytest configuration and fixtures for MOSS Partner SDK tests."""

import os
import uuid

import pytest

# Test configuration
TEST_API_KEY = os.environ.get("MOSS_PARTNER_KEY")
TEST_BASE_URL = os.environ.get(
    "MOSS_BASE_URL",
    "https://moss-api-staging-837703369688.us-central1.run.app",  # Staging (LC014, LC010)
)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires API key)"
    )


@pytest.fixture
def skip_if_no_api_key():
    """Skip test if no API key is configured."""
    if not TEST_API_KEY:
        pytest.skip("No MOSS_PARTNER_KEY environment variable set")


@pytest.fixture
def unique_id():
    """Generate unique ID for test resources."""
    return f"pytest_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "api_key": TEST_API_KEY,
        "base_url": TEST_BASE_URL,
    }
