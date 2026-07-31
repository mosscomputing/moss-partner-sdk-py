# Python Partner SDK - Admin Scripts

This directory contains administrative scripts for managing the Python Partner SDK deployment.

## create_test_partner.py

Creates a test partner for CI integration tests via the admin endpoint.

### Prerequisites

- Python 3.9+ with `httpx` installed
- `ADMIN_SECRET` environment variable set (requires admin access)
- Access to MOSS Partner API

### Usage

```bash
# Set admin secret (obtain from admin team)
export ADMIN_SECRET=your_admin_secret_here

# Create test partner
python scripts/create_test_partner.py
```

### What it does

1. Creates a partner with:
   - `external_id`: `python_sdk_ci`
   - `name`: `Python SDK CI Tests`
   - `tier`: `platform`

2. Returns the partner API key (shown only once)

3. Provides instructions for setting GitHub secret

### Output Example

```
🔧 Creating test partner at https://api.mosscomputing.com...
   external_id: python_sdk_ci
   name: Python SDK CI Tests

✅ Partner created successfully!

   Partner ID: 123e4567-e89b-12d3-a456-426614174000
   API Key: prt_abc123def456...
   Created: 2026-07-31T18:00:00Z

📋 Next steps:

1. Set GitHub secret MOSS_PARTNER_KEY:
   gh secret set MOSS_PARTNER_KEY --body 'prt_abc123...' --repo mosscomputing/moss-partner-sdk-py

2. Trigger CI to run integration tests:
   git commit --allow-empty -m 'test: Trigger CI with partner key'
   git push

3. Verify integration tests pass:
   gh run list --workflow=ci.yml --limit 1
```

### Testing Against Different Environments

```bash
# Test against staging
export MOSS_BASE_URL=https://moss-api-staging-837703369688.us-central1.run.app
python scripts/create_test_partner.py

# Test against local dev
export MOSS_BASE_URL=http://localhost:8000
python scripts/create_test_partner.py
```

### Error Handling

**Missing ADMIN_SECRET:**
```
❌ Error: ADMIN_SECRET environment variable not set
```

**Invalid credentials:**
```
❌ HTTP Error 401: Invalid admin authorization
```

**Partner already exists:**
```
❌ HTTP Error 409: Partner with external_id 'python_sdk_ci' already exists
```

### After Partner Creation

1. **Set GitHub Secret:**
   ```bash
   gh secret set MOSS_PARTNER_KEY \
     --body 'prt_your_api_key_here' \
     --repo mosscomputing/moss-partner-sdk-py
   ```

2. **Verify Secret:**
   ```bash
   gh secret list --repo mosscomputing/moss-partner-sdk-py
   ```

3. **Trigger CI:**
   - Push any commit to main
   - Or create a PR to test

4. **Check Integration Tests:**
   ```bash
   gh run list --workflow=ci.yml --limit 3
   gh run view <run_id> --log
   ```

## Security Notes

- **Never commit ADMIN_SECRET** to version control
- **API keys are shown only once** - save them immediately
- **GitHub secrets are encrypted** - they cannot be retrieved after being set
- **Partner API keys start with `prt_`** - validate format before using

## Troubleshooting

### Script fails with import error

```bash
# Install dependencies
pip install httpx
```

### Can't access admin endpoint

Ensure you have:
1. Valid `ADMIN_SECRET` from admin team
2. Network access to the API endpoint
3. Correct API URL (production vs staging)

### Partner already exists

If you need to recreate:
1. Contact admin team to delete existing partner
2. Or use a different `external_id` in the script

## Related Documentation

- [DEPLOYMENT_STATUS.md](../DEPLOYMENT_STATUS.md) - Full deployment guide
- [PARTNER_CREATION.md](../docs/PARTNER_CREATION.md) - Partner creation reference (LC006)
- [README.md](../README.md) - SDK usage documentation
