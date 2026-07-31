#!/usr/bin/env python3
"""
Create a test partner for Python SDK CI integration tests.

Usage:
    python scripts/create_test_partner.py

Requirements:
    - ADMIN_SECRET environment variable must be set
    - API must be accessible at https://api.mosscomputing.com

This script creates a partner with:
    - external_id: python_sdk_ci
    - name: Python SDK CI Tests
    - tier: platform

The returned API key should be set as the MOSS_PARTNER_KEY GitHub secret.
"""

import os
import sys
from typing import Any, Dict

import httpx


def create_partner(admin_secret: str, base_url: str = "https://api.mosscomputing.com") -> Dict[str, Any]:
    """
    Create a partner via the admin endpoint.

    Args:
        admin_secret: Admin authorization secret
        base_url: API base URL

    Returns:
        Partner creation response with api_key

    Raises:
        httpx.HTTPStatusError: If API returns error
    """
    url = f"{base_url}/v1/admin/partners"
    headers = {
        "Authorization": f"Bearer {admin_secret}",
        "Content-Type": "application/json",
    }
    data = {
        "external_id": "python_sdk_ci",
        "name": "Python SDK CI Tests",
        "settings": {
            "tier": "platform",
            "description": "Partner for Python SDK integration tests",
        },
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()


def main() -> None:
    """Main entry point."""
    # Get admin secret from environment
    admin_secret = os.environ.get("ADMIN_SECRET")
    if not admin_secret:
        print("❌ Error: ADMIN_SECRET environment variable not set", file=sys.stderr)
        print("\nUsage:", file=sys.stderr)
        print("  export ADMIN_SECRET=your_admin_secret", file=sys.stderr)
        print("  python scripts/create_test_partner.py", file=sys.stderr)
        sys.exit(1)

    # Get optional base URL override
    base_url = os.environ.get("MOSS_BASE_URL", "https://api.mosscomputing.com")

    print(f"🔧 Creating test partner at {base_url}...")
    print("   external_id: python_sdk_ci")
    print("   name: Python SDK CI Tests")
    print()

    try:
        result = create_partner(admin_secret, base_url)

        partner_id = result.get("id") or result.get("partner_id")
        api_key = result.get("api_key") or result.get("partner_key")
        created_at = result.get("created_at")

        print("✅ Partner created successfully!")
        print()
        print(f"   Partner ID: {partner_id}")
        print(f"   API Key: {api_key}")
        print(f"   Created: {created_at}")
        print()
        print("📋 Next steps:")
        print()
        print("1. Set GitHub secret MOSS_PARTNER_KEY:")
        print(f"   gh secret set MOSS_PARTNER_KEY --body '{api_key}' --repo mosscomputing/moss-partner-sdk-py")
        print()
        print("2. Trigger CI to run integration tests:")
        print("   git commit --allow-empty -m 'test: Trigger CI with partner key'")
        print("   git push")
        print()
        print("3. Verify integration tests pass:")
        print("   gh run list --workflow=ci.yml --limit 1")
        print()

    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
