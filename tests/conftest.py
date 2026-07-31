"""Pytest configuration and fixtures for MOSS Partner SDK tests."""

import os
import uuid
import warnings

import pytest

# Test configuration (matches TypeScript SDK setup.ts pattern)
TEST_API_KEY = os.environ.get("MOSS_PARTNER_KEY", "")
TEST_BASE_URL = os.environ.get(
    "MOSS_BASE_URL",
    "https://api.mosscomputing.com",  # Production API (matches TypeScript)
)

# Test prefix to avoid collisions
TEST_PREFIX = f"test_sdk_{int(os.environ.get('GITHUB_RUN_ID', '0')) or uuid.uuid4().hex[:8]}"


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires API key)"
    )

    # Warn if no API key (matches TypeScript beforeAll pattern)
    if not TEST_API_KEY:
        warnings.warn(
            "⚠️  MOSS_PARTNER_KEY not set. Integration tests will be skipped.",
            UserWarning,
        )


@pytest.fixture
def skip_if_no_api_key():
    """Skip test if no API key is configured."""
    if not TEST_API_KEY:
        pytest.skip("No MOSS_PARTNER_KEY environment variable set")


@pytest.fixture
def unique_id():
    """Generate unique ID for test resources."""
    return f"{TEST_PREFIX}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "api_key": TEST_API_KEY,
        "base_url": TEST_BASE_URL,
    }
