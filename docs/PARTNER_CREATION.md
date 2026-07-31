# Partner Creation Guide

**Reference**: LC006 (Admin endpoints are P0, not nice to have)

---

## Overview

Partners must be created via the admin endpoint before they can use the Partner API. This ensures proper onboarding, credential management, and billing setup.

## Admin Endpoint

### POST /v1/admin/partners

Creates a new partner with API credentials.

**Endpoint**: `https://api.mosscomputing.com/v1/admin/partners`

**Authentication**: Requires admin secret (`ADMIN_SECRET` header)

**Request**:
```json
{
  "external_id": "partner_name",
  "name": "Partner Display Name",
  "email": "contact@partner.com",
  "tier": "platform"
}
```

**Response**:
```json
{
  "partner_id": "uuid-here",
  "api_key": "prt_xxx",
  "created_at": "2026-07-31T00:00:00Z"
}
```

## Creating Test Partner for CI

### Option 1: Using curl

```bash
curl -X POST https://api.mosscomputing.com/v1/admin/partners \
  -H "ADMIN_SECRET: $ADMIN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "python_sdk_ci",
    "name": "Python SDK CI Tests",
    "email": "sdk-tests@mosscomputing.com",
    "tier": "platform"
  }'
```

### Option 2: Using Python

```python
import httpx
import os

admin_secret = os.environ["ADMIN_SECRET"]

response = httpx.post(
    "https://api.mosscomputing.com/v1/admin/partners",
    headers={
        "ADMIN_SECRET": admin_secret,
        "Content-Type": "application/json",
    },
    json={
        "external_id": "python_sdk_ci",
        "name": "Python SDK CI Tests",
        "email": "sdk-tests@mosscomputing.com",
        "tier": "platform",
    },
)

partner = response.json()
print(f"Partner API Key: {partner['api_key']}")
# Save this as MOSS_PARTNER_KEY GitHub secret
```

## Setting GitHub Secret

Once you have the partner API key:

1. **Navigate to GitHub repository settings**:
   ```
   https://github.com/mosscomputing/moss-partner-sdk-py/settings/secrets/actions
   ```

2. **Add new secret**:
   - Name: `MOSS_PARTNER_KEY`
   - Value: `prt_xxx` (from admin endpoint response)

3. **Verify secret is set**:
   - CI integration tests will now run on main pushes
   - Tests use production API: `https://api.mosscomputing.com`

## Partner Lifecycle

### States

1. **Created** - Partner created via admin endpoint
2. **Active** - Partner can make API calls
3. **Suspended** - Partner temporarily blocked
4. **Deactivated** - Partner permanently disabled

### Managing Partners

**List partners**:
```bash
GET /v1/admin/partners
```

**Get partner details**:
```bash
GET /v1/admin/partners/{partner_id}
```

**Rotate API key**:
```bash
POST /v1/admin/partners/{partner_id}/rotate-key
```

**Suspend partner**:
```bash
POST /v1/admin/partners/{partner_id}/suspend
```

## Testing Without API Key

### Local Development

Integration tests skip gracefully if no API key is set:

```bash
# No API key - integration tests skipped
pytest tests/ -v

# Output:
# tests/test_integration.py::TestHealthCheck::test_ping SKIPPED
# ⚠️  MOSS_PARTNER_KEY not set. Integration tests will be skipped.
```

Unit tests always run (no API key needed):

```bash
pytest tests/ -v -m "not integration"

# Output:
# tests/test_integration.py::TestErrorHandling::test_validate_api_key_format PASSED
# tests/test_integration.py::TestErrorHandling::test_require_api_key PASSED
```

### CI Behavior

**On PR**: Only unit tests run (no API key needed)
**On main push**: Integration tests run if `MOSS_PARTNER_KEY` secret is set
**If secret missing**: Integration job uses `continue-on-error: true` (doesn't block)

## Troubleshooting

### "No MOSS_PARTNER_KEY environment variable set"

This is expected if:
- You're developing locally without API key
- GitHub secret is not configured
- Running in CI on PR (integration tests only run on main)

**Solution**: Set up partner via admin endpoint and configure GitHub secret

### "401 Unauthorized"

- Partner API key is invalid
- Partner is suspended or deactivated
- API key was rotated

**Solution**: Check partner status via admin endpoint

### "403 Forbidden"

- Partner tier doesn't allow this operation
- Feature gating restriction

**Solution**: Check partner tier and feature flags

## Reference

- **Admin endpoint**: Implemented in `signing_api/routes/admin.py`
- **RLS policy**: `partner_isolation` (LC008)
- **Field mapping**: `partner_id` in database, `id` in SDK (LC019)
- **TypeScript pattern**: Same approach in `moss-partner-sdk-ts`

---

**Created**: 2026-07-31
**Pattern**: Matches TypeScript SDK exactly (LC019)
