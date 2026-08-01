# Frequently Asked Questions

Common questions about the MOSS Partner SDK for Python.

---

## General

### What is the MOSS Partner SDK?

The MOSS Partner SDK is a Python library that provides a clean, async-first interface for managing customers through the MOSS Partner API. It enables partners to create customers, configure governance policies, generate compliance reports, and monitor compliance.

---

### Who should use this SDK?

This SDK is for **MOSS partners** who integrate MOSS into their platforms or services. If you're an end customer of MOSS, you don't need this SDK - your partner manages your MOSS integration.

---

### What Python versions are supported?

- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12

Older versions (3.8 and below) are not supported.

---

### Is the SDK production-ready?

Yes! Version 0.1.0 is production-ready and has been:
- Security audited (0 vulnerabilities)
- Tested across Python 3.9-3.12
- Published to PyPI
- Used in production deployments

---

### What license is the SDK under?

Proprietary. See the [LICENSE](../LICENSE) file for details.

---

## Installation & Setup

### How do I install the SDK?

```bash
pip install moss-partner-sdk
```

See [Installation Guide](installation.md) for detailed instructions.

---

### Do I need an API key?

Yes. You need a partner API key from MOSS. Contact partners@mosscomputing.com to request access.

---

### Where do I get my API key?

MOSS admins create partner accounts and issue API keys. Your API key will be sent to you when your partner account is created. **Save it immediately** - it's shown only once.

---

### Can I use the same API key for dev and production?

No, it's recommended to use different API keys for each environment:
- Development: `prt_dev_xxx`
- Staging: `prt_staging_xxx`
- Production: `prt_prod_xxx`

Contact MOSS support to request multiple keys.

---

## Features & Capabilities

### What can I do with this SDK?

- **Customer Management**: Create, update, promote, suspend customers
- **Session Tokens**: Generate temporary dashboard access tokens
- **Compliance Reports**: Get ML-DSA-44 signed reports (PDF/JSON)
- **Webhooks**: Subscribe to real-time event notifications
- **Analytics**: Access customer, compliance, and billing metrics

See [API Reference](api-reference/client.md) for full capabilities.

---

### Can I manage multiple customers?

Yes! The Partner API is designed for managing many customers. You can:
- Create unlimited customers
- List and filter customers
- Bulk operations with pagination
- Concurrent requests with asyncio

See [Advanced Examples](examples/advanced.md) for batch operations.

---

### What's the difference between sandbox and production?

- **Sandbox**: Testing environment with limited features
  - Customer gets a `sandbox_token`
  - Used for integration testing
  - No billing

- **Production**: Full features with billing
  - Customer gets a `production_token` after promotion
  - Requires KYC/attestation
  - Billing configured

See [Customer Lifecycle Guide](guides/customer-lifecycle.md).

---

### Can I promote a customer back to sandbox?

No. Once promoted to production, customers cannot be demoted to sandbox. You can:
- Suspend a customer (reversible)
- Create a new sandbox customer for testing

---

### How do session tokens work?

Session tokens provide temporary access to a customer's MOSS dashboard:
- Created via `moss.customers.create_session()`
- TTL is always 900 seconds (15 minutes) per API behavior (LC018)
- Can be revoked before expiration
- Used for support access or embedded dashboards

See [Session Tokens Guide](guides/session-tokens.md).

---

### What is ML-DSA-44?

ML-DSA-44 (Module-Lattice Digital Signature Algorithm) is a post-quantum cryptography signature scheme. MOSS uses it to sign compliance reports, making them:
- Tamper-evident
- Cryptographically verifiable
- Future-proof against quantum computers

Signatures are ~3000-5000 base64 characters.

---

### Can I verify ML-DSA-44 signatures?

Yes. Compliance reports include signature metadata:
```python
report = await moss.customers.compliance_report("cust_xxx", format="pdf")
print(f"Signature: {report.signature}")
print(f"Key ID: {report.key_id}")
# Verify using MOSS public key
```

See [Compliance Reports Guide](guides/compliance-reports.md#signature-verification).

---

## Usage & Development

### Why async/await instead of sync?

The SDK uses `async`/`await` for:
- Better performance with concurrent requests
- Non-blocking I/O
- Modern Python best practices

Example:
```python
# Concurrent requests
tasks = [
    moss.customers.get("cust_1"),
    moss.customers.get("cust_2"),
    moss.customers.get("cust_3"),
]
results = await asyncio.gather(*tasks)  # Parallel execution
```

---

### Can I use the SDK in synchronous code?

Yes, use `asyncio.run()`:
```python
import asyncio
from moss_partner_sdk import MossPartner

def sync_function():
    async def async_work():
        async with MossPartner(api_key="prt_xxx") as moss:
            return await moss.customers.list()

    return asyncio.run(async_work())

customers = sync_function()
```

---

### How do I handle errors?

Use try/except with specific exception types:
```python
from moss_partner_sdk import MossAPIError, MossNetworkError

try:
    customer = await moss.customers.get("cust_xxx")
except MossAPIError as e:
    print(f"API Error {e.status_code}: {e.message}")
except MossNetworkError as e:
    print(f"Network Error: {e.message}")
```

See [Error Handling Guide](guides/error-handling.md).

---

### How do I test code that uses the SDK?

Use mocks:
```python
from unittest.mock import AsyncMock, patch

async def test_customer_creation():
    with patch('moss_partner_sdk.HTTPClient.request', new_callable=AsyncMock) as mock:
        mock.return_value = {"customerId": "cust_123", ...}

        async with MossPartner(api_key="prt_test") as moss:
            customer = await moss.customers.create(...)
            assert customer.id == "cust_123"
```

See [Advanced Examples](examples/advanced.md#testing-patterns).

---

### Is the SDK thread-safe?

No. Each thread should have its own `MossPartner` instance:
```python
# ✅ GOOD: One client per thread
def worker():
    moss = MossPartner(api_key="prt_xxx")
    asyncio.run(moss.customers.list())
```

Don't share a single client across threads.

---

## API Behavior

### What's the rate limit?

Rate limits vary by partner tier. If you hit the limit, you'll get a `429` error:
```python
MossAPIError: API Error 429 (rate_limit_exceeded): Too many requests
```

Implement exponential backoff to handle this gracefully. See [Troubleshooting](troubleshooting.md#429-rate-limit-exceeded).

---

### How long do session tokens last?

Session tokens **always expire after 900 seconds (15 minutes)**, regardless of the TTL you request. This is API-enforced behavior (LC018).

```python
# You can request any TTL, but API caps at 900s
session = await moss.customers.create_session(
    customer_id="cust_xxx",
    ttl_seconds=3600  # Request 1 hour
)
# But session.expires_at will be ~900s from now
```

---

### Can I customize the API base URL?

Yes, for testing against staging or local environments:
```python
moss = MossPartner(
    api_key="prt_xxx",
    base_url="https://moss-api-staging.example.com"
)
```

Default: `https://api.mosscomputing.com`

---

### How do I paginate through results?

Use `limit` and `page` parameters:
```python
# First page
page1 = await moss.customers.list(limit=20, page=1)
print(f"Total: {page1.total}")
print(f"Page 1: {len(page1.data)} customers")

# Second page
page2 = await moss.customers.list(limit=20, page=2)
```

Or iterate through all pages:
```python
all_customers = []
page = 1

while True:
    result = await moss.customers.list(limit=100, page=page)
    all_customers.extend(result.data)

    if not result.pagination.has_more:
        break

    page += 1
```

---

### How do webhooks work?

Webhooks notify you of events in real-time:

1. **Create subscription**:
   ```python
   webhook = await moss.webhooks.create(
       url="https://yourapp.com/webhooks/moss",
       events=["customer.*", "agent.anomaly_detected"]
   )
   ```

2. **Implement handler**:
   ```python
   @app.post("/webhooks/moss")
   async def handle_webhook(request):
       # Verify signature
       is_valid = verify_webhook_signature(
           payload=request.body,
           signature=request.headers["X-Moss-Signature"],
           secret=webhook.secret
       )

       if not is_valid:
           return Response(status=401)

       # Process event
       event = await request.json()
       print(f"Event: {event['type']}")
   ```

See [Webhooks Guide](guides/webhooks.md).

---

## Billing & Pricing

### How much does the SDK cost?

The SDK itself is free. You pay for:
- Your partner account tier
- Customer usage (billed to your customers, not to you)

Contact partners@mosscomputing.com for pricing details.

---

### Do my customers get billed?

Yes, once promoted to production:
- Customers are billed based on their usage tier
- You configure billing settings during promotion
- You receive commission/revenue share (varies by partner agreement)

---

## Security

### Is my API key secure?

Your API key is sensitive. Follow these best practices:
- ✅ Store in environment variables
- ✅ Never commit to version control
- ✅ Rotate regularly
- ❌ Don't log or print API keys
- ❌ Don't share via insecure channels

See [Authentication Guide](authentication.md#security-best-practices).

---

### How do I rotate my API key?

1. Request new API key from MOSS support
2. Update configuration with new key
3. Verify new key works
4. Contact MOSS to revoke old key

See [Authentication Guide](authentication.md#api-key-rotation).

---

### Are webhook signatures verified?

Yes, always verify webhook signatures:
```python
from moss_partner_sdk import verify_webhook_signature

is_valid = verify_webhook_signature(
    payload=request.body,
    signature=request.headers["X-Moss-Signature"],
    secret=webhook.secret
)

if not is_valid:
    return Response(status=401)  # Reject invalid signature
```

Uses HMAC-SHA256. See [Webhooks Guide](guides/webhooks.md#signature-verification).

---

## Troubleshooting

### My requests are failing with "Connection timeout"

Try increasing the timeout:
```python
moss = MossPartner(api_key="prt_xxx", timeout=60.0)
```

See [Troubleshooting Guide](troubleshooting.md#connection-timeout).

---

### I'm getting "RuntimeError: Event loop is closed"

Use `asyncio.run()` instead of manually managing event loops:
```python
# ✅ GOOD
import asyncio

async def main():
    async with MossPartner(api_key="prt_xxx") as moss:
        return await moss.customers.list()

result = asyncio.run(main())
```

See [Troubleshooting Guide](troubleshooting.md#runtimeerror-event-loop-is-closed).

---

### How do I enable debug logging?

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("httpx")
logger.setLevel(logging.DEBUG)

# Now you'll see all HTTP requests/responses
async with MossPartner(api_key="prt_xxx") as moss:
    customers = await moss.customers.list()
```

---

## Support & Community

### Where can I get help?

1. **Documentation**: Start with [Getting Started](getting-started.md)
2. **GitHub Issues**: [Search existing issues](https://github.com/mosscomputing/moss-partner-sdk-py/issues)
3. **Email Support**: support@mosscomputing.com
4. **Partner Support**: partners@mosscomputing.com (for partnership questions)

---

### How do I report a bug?

1. **Check** if it's already reported: [GitHub Issues](https://github.com/mosscomputing/moss-partner-sdk-py/issues)
2. **Create new issue** with:
   - SDK version (`moss_partner_sdk.__version__`)
   - Python version
   - Minimal reproducible example
   - Full error traceback
   - Expected vs actual behavior

---

### Can I contribute to the SDK?

Yes! Contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [Contributing Guide](contributing.md) (coming soon).

---

### Where's the source code?

GitHub: https://github.com/mosscomputing/moss-partner-sdk-py

---

### How do I stay updated?

- Watch the [GitHub repository](https://github.com/mosscomputing/moss-partner-sdk-py)
- Subscribe to release notifications
- Check the [Changelog](changelog.md)
- Follow MOSS announcements

---

## Next Steps

- [Getting Started Guide](getting-started.md) - Your first request in 5 minutes
- [Customer Lifecycle Guide](guides/customer-lifecycle.md) - Complete workflow
- [API Reference](api-reference/client.md) - Full API documentation
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
