# Troubleshooting

Common issues and solutions for the MOSS Partner SDK.

---

## Installation Issues

### SSL Certificate Errors

**Problem**:
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solution**:
```bash
# Upgrade certifi
pip install --upgrade certifi

# Or install with trusted hosts
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org moss-partner-sdk
```

---

### Permission Denied

**Problem**:
```
PermissionError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Install for current user only
pip install --user moss-partner-sdk

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install moss-partner-sdk
```

---

### Dependency Conflicts

**Problem**:
```
ERROR: pip's dependency resolver does not currently take into account...
```

**Solution**:
```bash
# Create fresh virtual environment
python -m venv fresh-env
source fresh-env/bin/activate  # or fresh-env\Scripts\activate on Windows
pip install moss-partner-sdk
```

---

## Authentication Issues

### Invalid API Key Format

**Problem**:
```python
ValueError: api_key must start with "prt_"
```

**Solution**:
```python
# ✅ Correct format
api_key = "prt_abc123..."

# ❌ Wrong - missing prefix
api_key = "abc123..."

# Check for whitespace
api_key = os.environ["MOSS_API_KEY"].strip()
```

---

### 401 Unauthorized

**Problem**:
```python
MossAPIError: API Error 401 (unauthorized): Invalid API key
```

**Solutions**:

1. **Verify API key is set**:
   ```python
   import os
   print(os.environ.get("MOSS_API_KEY"))  # Should not be None
   ```

2. **Check for typos**:
   ```python
   # Copy-paste the key directly to verify
   api_key = "prt_exact_key_from_email"
   ```

3. **Verify key hasn't been rotated**:
   - Contact MOSS support if key was recently changed
   - Request new key if needed

---

### 403 Forbidden

**Problem**:
```python
MossAPIError: API Error 403 (forbidden): Insufficient permissions
```

**Solution**:
- Your API key is valid but lacks permissions for this operation
- Contact MOSS support to verify your partner tier and permissions

---

## Network Issues

### Connection Timeout

**Problem**:
```python
MossNetworkError: Request failed: Connection timeout
```

**Solutions**:

1. **Increase timeout**:
   ```python
   moss = MossPartner(
       api_key="prt_xxx",
       timeout=60.0  # Increase from default 30s
   )
   ```

2. **Check network connectivity**:
   ```bash
   # Test API endpoint
   curl https://api.mosscomputing.com/health
   ```

3. **Retry with exponential backoff**:
   ```python
   from moss_partner_sdk import MossPartner, MossNetworkError
   import asyncio

   async def retry_operation():
       retries = 3
       for attempt in range(retries):
           try:
               async with MossPartner(api_key="prt_xxx") as moss:
                   return await moss.customers.list()
           except MossNetworkError:
               if attempt < retries - 1:
                   await asyncio.sleep(2 ** attempt)
               else:
                   raise
   ```

---

### DNS Resolution Errors

**Problem**:
```
gaierror: [Errno -2] Name or service not known
```

**Solutions**:

1. **Check DNS**:
   ```bash
   nslookup api.mosscomputing.com
   ```

2. **Try alternative DNS**:
   - Use Google DNS (8.8.8.8, 8.8.4.4)
   - Use Cloudflare DNS (1.1.1.1)

3. **Check firewall**:
   - Ensure outbound HTTPS (port 443) is allowed

---

## API Errors

### 404 Not Found

**Problem**:
```python
MossAPIError: API Error 404 (not_found): Customer not found
```

**Solutions**:

1. **Verify customer ID**:
   ```python
   # Customer IDs start with "cust_"
   customer_id = "cust_abc123..."

   # Check ID format
   if not customer_id.startswith("cust_"):
       print("❌ Invalid customer ID format")
   ```

2. **List customers to find correct ID**:
   ```python
   result = await moss.customers.list()
   for customer in result.data:
       print(f"{customer.name}: {customer.id}")
   ```

---

### 409 Conflict

**Problem**:
```python
MossAPIError: API Error 409 (conflict): Customer with external_id already exists
```

**Solution**:
```python
# Use unique external_id for each customer
import uuid

external_id = f"customer_{uuid.uuid4().hex[:8]}"

# Or check if exists first
try:
    customer = await moss.customers.create(external_id="existing_id", ...)
except MossAPIError as e:
    if e.status_code == 409:
        # Customer exists, get it instead
        result = await moss.customers.list(external_id="existing_id")
        customer = result.data[0]
```

---

### 429 Rate Limit Exceeded

**Problem**:
```python
MossAPIError: API Error 429 (rate_limit_exceeded): Too many requests
```

**Solutions**:

1. **Implement exponential backoff**:
   ```python
   import asyncio
   from moss_partner_sdk import MossAPIError

   async def with_rate_limit(operation):
       max_retries = 5
       for attempt in range(max_retries):
           try:
               return await operation()
           except MossAPIError as e:
               if e.status_code == 429 and attempt < max_retries - 1:
                   wait_time = 2 ** attempt
                   print(f"Rate limited. Waiting {wait_time}s...")
                   await asyncio.sleep(wait_time)
               else:
                   raise
   ```

2. **Batch requests**:
   ```python
   # Don't do this:
   for customer_id in customer_ids:
       await moss.customers.get(customer_id)  # ❌ Many sequential requests

   # Do this instead:
   async def get_customers_batch(ids):
       # Use list with filters or pagination
       result = await moss.customers.list(limit=100)
       return {c.id: c for c in result.data}
   ```

---

### 500 Internal Server Error

**Problem**:
```python
MossAPIError: API Error 500 (internal_server_error)
```

**Solutions**:

1. **Retry the request**:
   - SDK automatically retries 5xx errors (default: 3 retries)
   - Increase retries if needed:
     ```python
     moss = MossPartner(api_key="prt_xxx", retries=5)
     ```

2. **Check MOSS status**:
   - Visit status page (if available)
   - Contact support@mosscomputing.com

---

## Data Issues

### Parsing Errors

**Problem**:
```python
MossParseError: Failed to parse response
```

**Solutions**:

1. **Check API response format**:
   ```python
   try:
       customer = await moss.customers.get("cust_xxx")
   except MossParseError as e:
       print(f"Parse error: {e.message}")
       # Contact support with error details
   ```

2. **Verify SDK version**:
   ```python
   import moss_partner_sdk
   print(moss_partner_sdk.__version__)  # Should be 0.1.0 or higher

   # Upgrade if outdated
   # pip install --upgrade moss-partner-sdk
   ```

---

### Missing Fields

**Problem**:
```python
AttributeError: 'Customer' object has no attribute 'production_token'
```

**Solution**:
```python
# Check if field is populated
customer = await moss.customers.get("cust_xxx")

if customer.production_token:
    print(f"Production token: {customer.production_token}")
else:
    print("Customer not yet promoted to production")

# Promote customer first
if customer.status == "pending":
    promoted = await moss.customers.promote(customer.id, ...)
    print(f"Production token: {promoted.production_token}")
```

---

## Async/Await Issues

### RuntimeError: Event loop is closed

**Problem**:
```python
RuntimeError: Event loop is closed
```

**Solution**:
```python
import asyncio

# ✅ Correct - Use asyncio.run()
async def main():
    async with MossPartner(api_key="prt_xxx") as moss:
        customers = await moss.customers.list()
        return customers

result = asyncio.run(main())

# ❌ Wrong - Don't reuse event loop
# loop = asyncio.get_event_loop()
# result = loop.run_until_complete(main())
```

---

### Cannot Call Async Function

**Problem**:
```python
TypeError: object Customer coroutine can't be used in 'await' expression
```

**Solution**:
```python
# ❌ Wrong - Missing await
customers = moss.customers.list()

# ✅ Correct - Use await
customers = await moss.customers.list()
```

---

### Running Async in Sync Context

**Problem**:
```
RuntimeError: asyncio.run() cannot be called from a running event loop
```

**Solution**:
```python
# In Jupyter notebooks or async contexts
async with MossPartner(api_key="prt_xxx") as moss:
    customers = await moss.customers.list()

# In sync contexts
import asyncio

def sync_function():
    async def async_work():
        async with MossPartner(api_key="prt_xxx") as moss:
            return await moss.customers.list()

    return asyncio.run(async_work())
```

---

## Environment Issues

### Environment Variable Not Found

**Problem**:
```python
KeyError: 'MOSS_API_KEY'
```

**Solutions**:

1. **Use .get() with fallback**:
   ```python
   import os

   api_key = os.environ.get("MOSS_API_KEY")
   if not api_key:
       raise ValueError("MOSS_API_KEY environment variable not set")
   ```

2. **Load from .env file**:
   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()
   api_key = os.environ["MOSS_API_KEY"]
   ```

3. **Verify environment variable is set**:
   ```bash
   echo $MOSS_API_KEY  # Linux/Mac
   echo %MOSS_API_KEY%  # Windows
   ```

---

### Wrong Base URL

**Problem**:
```python
MossNetworkError: Connection refused
```

**Solution**:
```python
# Verify base URL
moss = MossPartner(
    api_key="prt_xxx",
    base_url="https://api.mosscomputing.com"  # Correct production URL
)

# Check if accidentally using localhost
# base_url="http://localhost:8000"  # ❌ Wrong for production
```

---

## Testing Issues

### Mock Not Working

**Problem**:
```python
# Mocks aren't being called
```

**Solution**:
```python
from unittest.mock import AsyncMock, patch

# ✅ Correct - Mock async methods
async def test_customer_creation():
    with patch('moss_partner_sdk.HTTPClient.request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {
            "customerId": "cust_123",
            "name": "Test Customer",
            ...
        }

        async with MossPartner(api_key="prt_test") as moss:
            customer = await moss.customers.create(
                external_id="test_001",
                name="Test Customer"
            )

            assert customer.id == "cust_123"
            mock_request.assert_called_once()
```

---

## Performance Issues

### Slow Requests

**Problem**: Requests taking too long

**Solutions**:

1. **Check timeout settings**:
   ```python
   moss = MossPartner(api_key="prt_xxx", timeout=30.0)
   ```

2. **Use pagination**:
   ```python
   # Don't fetch all at once
   result = await moss.customers.list(limit=20, page=1)
   ```

3. **Concurrent requests**:
   ```python
   import asyncio

   async def fetch_multiple():
       async with MossPartner(api_key="prt_xxx") as moss:
           tasks = [
               moss.customers.get("cust_1"),
               moss.customers.get("cust_2"),
               moss.customers.get("cust_3"),
           ]
           return await asyncio.gather(*tasks)
   ```

---

## Debugging Tips

### Enable Verbose Logging

```python
import logging

# Enable HTTP client logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("httpx")
logger.setLevel(logging.DEBUG)

# Now you'll see all HTTP requests/responses
async with MossPartner(api_key="prt_xxx") as moss:
    customers = await moss.customers.list()
```

---

### Inspect Request/Response

```python
from moss_partner_sdk import MossPartner

moss = MossPartner(api_key="prt_xxx")

try:
    customer = await moss.customers.get("cust_xxx")
except Exception as e:
    print(f"Error type: {type(e)}")
    print(f"Error message: {e}")
    if hasattr(e, 'response_body'):
        print(f"Response body: {e.response_body}")
    raise
```

---

### Check SDK Version

```python
import moss_partner_sdk

print(f"SDK Version: {moss_partner_sdk.__version__}")
print(f"Python Version: {sys.version}")

# Verify dependencies
import httpx
import pydantic

print(f"httpx: {httpx.__version__}")
print(f"pydantic: {pydantic.__version__}")
```

---

## Getting Help

If you can't resolve your issue:

1. **Check documentation**:
   - [API Reference](api-reference/client.md)
   - [Guides](guides/customer-lifecycle.md)
   - [FAQ](faq.md)

2. **Search existing issues**:
   - [GitHub Issues](https://github.com/mosscomputing/moss-partner-sdk-py/issues)

3. **Create new issue**:
   - Include SDK version, Python version
   - Provide minimal reproducible example
   - Include full error traceback

4. **Contact support**:
   - Email: support@mosscomputing.com
   - Include your partner ID (not your API key!)

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: api_key must start with "prt_"` | Invalid API key format | Check key starts with `prt_` |
| `401 Unauthorized` | Invalid API key | Verify key is correct |
| `403 Forbidden` | Insufficient permissions | Contact MOSS support |
| `404 Not Found` | Resource doesn't exist | Verify ID is correct |
| `409 Conflict` | Duplicate external_id | Use unique external_id |
| `429 Too Many Requests` | Rate limit exceeded | Implement exponential backoff |
| `500 Internal Server Error` | Server error | Retry request, contact support |
| `Connection timeout` | Network issue | Increase timeout, check network |
| `RuntimeError: Event loop is closed` | Async misuse | Use `asyncio.run()` |

---

## Next Steps

- [FAQ](faq.md) - Frequently asked questions
- [Error Handling Guide](guides/error-handling.md) - Comprehensive error handling
- [API Reference](api-reference/client.md) - Full API documentation
