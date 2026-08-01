# Authentication

## Overview

The MOSS Partner SDK uses **API key authentication** with Bearer tokens. All requests to the Partner API must include a valid partner API key.

---

## Getting Your API Key

### 1. Request Partner Access

Contact MOSS to request partner access:
- **Email**: partners@mosscomputing.com
- **Requirements**: Business use case, estimated customer volume

### 2. Partner Creation

MOSS admins will create your partner account via the admin endpoint:

```bash
curl -X POST https://api.mosscomputing.com/v1/admin/partners \
  -H "ADMIN_SECRET: $ADMIN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "your_company_id",
    "name": "Your Company Name",
    "email": "partners@yourcompany.com",
    "tier": "platform"
  }'
```

### 3. Receive API Key

You'll receive a response with your API key:

```json
{
  "partner_id": "uuid-here",
  "api_key": "prt_abc123...",
  "created_at": "2026-07-31T00:00:00Z"
}
```

⚠️ **Important**: The API key is shown only once. Save it securely immediately.

---

## API Key Format

Partner API keys have a specific format:

```
prt_<random_string>
```

**Example**: `prt_abc123def456ghi789jkl012mno345pqr678stu901`

- **Prefix**: Always starts with `prt_`
- **Length**: Typically 40-60 characters
- **Characters**: Alphanumeric (a-z, A-Z, 0-9)

---

## Using Your API Key

### Option 1: Environment Variable (Recommended)

Set the API key as an environment variable:

```bash
export MOSS_API_KEY="prt_abc123..."
```

Then use in your code:

```python
import os
from moss_partner_sdk import MossPartner

api_key = os.environ.get("MOSS_API_KEY")
moss = MossPartner(api_key=api_key)
```

### Option 2: Direct Initialization

```python
from moss_partner_sdk import MossPartner

moss = MossPartner(api_key="prt_abc123...")
```

### Option 3: Configuration File

Create a config file (e.g., `.env`):

```bash
# .env
MOSS_API_KEY=prt_abc123...
MOSS_BASE_URL=https://api.mosscomputing.com
```

Load with `python-dotenv`:

```python
from dotenv import load_dotenv
import os
from moss_partner_sdk import MossPartner

load_dotenv()

moss = MossPartner(
    api_key=os.environ["MOSS_API_KEY"],
    base_url=os.environ.get("MOSS_BASE_URL", "https://api.mosscomputing.com")
)
```

---

## Security Best Practices

### ✅ DO

1. **Store in environment variables**:
   ```bash
   export MOSS_API_KEY="prt_xxx"
   ```

2. **Use secrets management**:
   - AWS Secrets Manager
   - Google Secret Manager
   - HashiCorp Vault
   - Azure Key Vault

3. **Rotate keys regularly**:
   - Request new API key
   - Update configuration
   - Revoke old key

4. **Use different keys per environment**:
   - Development: `prt_dev_xxx`
   - Staging: `prt_staging_xxx`
   - Production: `prt_prod_xxx`

5. **Restrict access**:
   - Limit who has access to API keys
   - Use role-based access control (RBAC)

### ❌ DON'T

1. **Don't commit to version control**:
   ```python
   # ❌ BAD
   api_key = "prt_abc123..."  # Hardcoded secret
   ```

2. **Don't log API keys**:
   ```python
   # ❌ BAD
   print(f"Using API key: {api_key}")
   logger.info(f"API key: {api_key}")
   ```

3. **Don't share via insecure channels**:
   - ❌ Email
   - ❌ Slack messages
   - ❌ Text messages
   - ✅ Use encrypted password managers

4. **Don't expose in client-side code**:
   - Never use partner API keys in browser JavaScript
   - Partner keys are server-side only

---

## API Key Validation

The SDK validates API keys on initialization:

```python
from moss_partner_sdk import MossPartner

# ✅ Valid format
moss = MossPartner(api_key="prt_abc123...")

# ❌ Invalid - no prefix
moss = MossPartner(api_key="abc123...")
# Raises: ValueError: api_key must start with "prt_"

# ❌ Invalid - empty
moss = MossPartner(api_key="")
# Raises: ValueError: api_key is required
```

---

## Testing Authentication

### Test API Connection

```python
import asyncio
from moss_partner_sdk import MossPartner, MossAPIError

async def test_auth():
    try:
        async with MossPartner(api_key="prt_xxx") as moss:
            # Ping endpoint to verify authentication
            is_connected = await moss.ping()

            if is_connected:
                print("✅ Authentication successful!")
            else:
                print("❌ Authentication failed")

    except MossAPIError as e:
        if e.status_code == 401:
            print("❌ Invalid API key")
        else:
            print(f"❌ API error: {e}")

asyncio.run(test_auth())
```

### Common Authentication Errors

| Status Code | Error | Cause |
|-------------|-------|-------|
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Valid key, but insufficient permissions |
| 429 | Too Many Requests | Rate limit exceeded |

---

## Multiple API Keys

If you manage multiple partners:

```python
from moss_partner_sdk import MossPartner

# Partner A
moss_a = MossPartner(api_key=os.environ["MOSS_API_KEY_PARTNER_A"])

# Partner B
moss_b = MossPartner(api_key=os.environ["MOSS_API_KEY_PARTNER_B"])

# Use separately
async with moss_a as client_a:
    customers_a = await client_a.customers.list()

async with moss_b as client_b:
    customers_b = await client_b.customers.list()
```

---

## Environment-Specific Configuration

### Development

```python
# .env.development
MOSS_API_KEY=prt_dev_xxx
MOSS_BASE_URL=https://moss-api-staging.example.com
```

### Production

```python
# .env.production
MOSS_API_KEY=prt_prod_xxx
MOSS_BASE_URL=https://api.mosscomputing.com
```

### Load Based on Environment

```python
import os
from dotenv import load_dotenv
from moss_partner_sdk import MossPartner

# Load environment-specific config
env = os.environ.get("ENV", "development")
load_dotenv(f".env.{env}")

moss = MossPartner(
    api_key=os.environ["MOSS_API_KEY"],
    base_url=os.environ.get("MOSS_BASE_URL", "https://api.mosscomputing.com")
)
```

---

## API Key Rotation

### Step 1: Request New Key

Contact MOSS support to request a new API key for your partner account.

### Step 2: Update Configuration

```bash
# Update environment variable
export MOSS_API_KEY="prt_new_key_here"

# Or update secrets manager
aws secretsmanager update-secret \
  --secret-id moss-api-key \
  --secret-string "prt_new_key_here"
```

### Step 3: Verify New Key

```python
# Test new key works
async with MossPartner(api_key="prt_new_key_here") as moss:
    await moss.ping()
```

### Step 4: Revoke Old Key

Contact MOSS support to revoke the old API key.

---

## Troubleshooting

### "Invalid API key" Error

```python
MossAPIError: API Error 401 (unauthorized): Invalid API key
```

**Solutions**:
1. Verify API key format starts with `prt_`
2. Check for extra whitespace: `api_key.strip()`
3. Ensure environment variable is loaded correctly
4. Contact support if key was recently rotated

### "API key is required" Error

```python
ValueError: api_key is required
```

**Solution**: Ensure you're passing the API key:

```python
# Check environment variable is set
import os
print(os.environ.get("MOSS_API_KEY"))  # Should not be None

# Pass explicitly
moss = MossPartner(api_key=os.environ["MOSS_API_KEY"])
```

---

## Next Steps

Now that you have authentication set up:

1. [Follow the quick start guide](getting-started.md)
2. [Create your first customer](guides/customer-lifecycle.md)
3. [Explore the API reference](api-reference/client.md)

---

## Support

For authentication issues:

- Email: support@mosscomputing.com
- Partner onboarding: partners@mosscomputing.com
