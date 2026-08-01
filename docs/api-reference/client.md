# MossPartner Client

The main SDK client for interacting with the MOSS Partner API.

---

## Class: `MossPartner`

```python
from moss_partner_sdk import MossPartner
```

The primary interface for all Partner API operations. Provides access to customer management, webhooks, and analytics.

---

## Constructor

### `MossPartner(api_key, base_url=None, timeout=None, retries=None)`

Initialize a new MOSS Partner API client.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | `str` | Yes | - | Partner API key (must start with `prt_`) |
| `base_url` | `str` | No | `https://api.mosscomputing.com` | Base URL for MOSS API |
| `timeout` | `float` | No | `30.0` | Request timeout in seconds |
| `retries` | `int` | No | `3` | Number of retries for failed requests |

**Returns**: `MossPartner` instance

**Raises**:
- `ValueError`: If `api_key` is invalid or missing

**Example**:

```python
from moss_partner_sdk import MossPartner

# Basic initialization
moss = MossPartner(api_key="prt_abc123...")

# With custom configuration
moss = MossPartner(
    api_key="prt_abc123...",
    base_url="https://moss-api-staging.example.com",
    timeout=60.0,
    retries=5
)
```

---

## Properties

### `customers`

Access to customer management methods.

**Type**: `CustomerResource`

**Example**:

```python
moss = MossPartner(api_key="prt_xxx")
await moss.customers.create(...)
await moss.customers.list()
```

See [Customer Methods](customers.md) for full API.

---

### `webhooks`

Access to webhook subscription methods.

**Type**: `WebhookResource`

**Example**:

```python
moss = MossPartner(api_key="prt_xxx")
await moss.webhooks.create(...)
await moss.webhooks.list()
```

See [Webhook Methods](webhooks.md) for full API.

---

### `analytics`

Access to analytics methods.

**Type**: `AnalyticsResource`

**Example**:

```python
moss = MossPartner(api_key="prt_xxx")
analytics = await moss.analytics.get(period="30d")
```

See [Analytics Methods](analytics.md) for full API.

---

## Methods

### `ping()`

**Async**. Test API connection and authentication.

**Parameters**: None

**Returns**: `bool` - `True` if API is reachable and authenticated

**Raises**:
- `MossAPIError`: If API returns an error
- `MossNetworkError`: If network request fails

**Example**:

```python
async with MossPartner(api_key="prt_xxx") as moss:
    is_connected = await moss.ping()

    if is_connected:
        print("✅ Connected to MOSS API")
    else:
        print("❌ Connection failed")
```

---

### `close()`

**Async**. Close the HTTP client and release resources.

**Parameters**: None

**Returns**: `None`

**Example**:

```python
moss = MossPartner(api_key="prt_xxx")

try:
    # Use the client
    await moss.customers.list()
finally:
    # Always close when done
    await moss.close()
```

**Note**: When using context managers (`async with`), `close()` is called automatically.

---

## Context Manager Support

The `MossPartner` client supports Python's `async with` syntax for automatic resource management.

### `async with MossPartner(...) as moss:`

**Example**:

```python
# Recommended: Automatic cleanup
async with MossPartner(api_key="prt_xxx") as moss:
    customers = await moss.customers.list()
    # Client automatically closed when exiting this block
```

**Equivalent to**:

```python
# Manual cleanup
moss = MossPartner(api_key="prt_xxx")
try:
    customers = await moss.customers.list()
finally:
    await moss.close()
```

---

## Usage Patterns

### Basic Usage

```python
import asyncio
from moss_partner_sdk import MossPartner

async def main():
    async with MossPartner(api_key="prt_xxx") as moss:
        # Your code here
        customers = await moss.customers.list()

asyncio.run(main())
```

---

### Error Handling

```python
from moss_partner_sdk import MossPartner, MossAPIError, MossNetworkError

async def safe_operation():
    try:
        async with MossPartner(api_key="prt_xxx") as moss:
            customer = await moss.customers.get("cust_123")
            return customer

    except MossAPIError as e:
        print(f"API Error {e.status_code}: {e.message}")
    except MossNetworkError as e:
        print(f"Network Error: {e.message}")
```

---

### Multiple Clients

```python
# Managing multiple partners
async with MossPartner(api_key=partner_a_key) as moss_a, \
           MossPartner(api_key=partner_b_key) as moss_b:

    customers_a = await moss_a.customers.list()
    customers_b = await moss_b.customers.list()
```

---

### Custom Configuration

```python
# Development environment
dev_client = MossPartner(
    api_key=os.environ["MOSS_DEV_KEY"],
    base_url="https://moss-api-dev.example.com",
    timeout=60.0,
    retries=5
)

# Production environment
prod_client = MossPartner(
    api_key=os.environ["MOSS_PROD_KEY"],
    base_url="https://api.mosscomputing.com",
    timeout=30.0,
    retries=3
)
```

---

### Environment-Based Configuration

```python
import os
from moss_partner_sdk import MossPartner

def create_client(environment="production"):
    """Create environment-specific client."""

    config = {
        "development": {
            "api_key": os.environ["MOSS_DEV_KEY"],
            "base_url": "https://moss-api-dev.example.com",
            "timeout": 60.0,
            "retries": 5
        },
        "production": {
            "api_key": os.environ["MOSS_PROD_KEY"],
            "base_url": "https://api.mosscomputing.com",
            "timeout": 30.0,
            "retries": 3
        }
    }

    return MossPartner(**config[environment])

# Usage
moss = create_client(environment=os.environ.get("ENV", "production"))
```

---

## Configuration Reference

### API Key Validation

The client validates API keys on initialization:

```python
# ✅ Valid
MossPartner(api_key="prt_abc123...")

# ❌ Invalid - no prefix
MossPartner(api_key="abc123...")
# Raises: ValueError: api_key must start with "prt_"

# ❌ Invalid - empty
MossPartner(api_key="")
# Raises: ValueError: api_key is required

# ❌ Invalid - None
MossPartner(api_key=None)
# Raises: ValueError: api_key is required
```

---

### Base URL

The base URL is where the SDK sends API requests.

**Default**: `https://api.mosscomputing.com`

**Custom**:

```python
# Staging environment
MossPartner(
    api_key="prt_xxx",
    base_url="https://moss-api-staging.example.com"
)

# Local development
MossPartner(
    api_key="prt_xxx",
    base_url="http://localhost:8000"
)
```

**Note**: The SDK automatically strips trailing slashes from `base_url`.

---

### Timeout

Request timeout in seconds.

**Default**: `30.0` (30 seconds)

**Custom**:

```python
# Long-running operations
MossPartner(api_key="prt_xxx", timeout=120.0)

# Fast timeout for low-latency requirements
MossPartner(api_key="prt_xxx", timeout=10.0)
```

**Note**: Applies to all HTTP requests (connect + read).

---

### Retries

Number of retries for failed requests.

**Default**: `3`

**Retry Behavior**:
- Only 5xx errors are retried (server errors)
- 4xx errors are NOT retried (client errors)
- Exponential backoff: 1s, 2s, 4s, 8s, ...

**Custom**:

```python
# More aggressive retries
MossPartner(api_key="prt_xxx", retries=5)

# No retries
MossPartner(api_key="prt_xxx", retries=0)
```

---

## Thread Safety

⚠️ **Not Thread-Safe**: The `MossPartner` client is **not thread-safe**. Each thread should have its own client instance.

**Don't do this**:

```python
# ❌ BAD: Shared across threads
moss = MossPartner(api_key="prt_xxx")

def worker():
    asyncio.run(moss.customers.list())  # Race condition!

threading.Thread(target=worker).start()
threading.Thread(target=worker).start()
```

**Do this instead**:

```python
# ✅ GOOD: One client per thread
def worker():
    moss = MossPartner(api_key="prt_xxx")
    asyncio.run(moss.customers.list())

threading.Thread(target=worker).start()
threading.Thread(target=worker).start()
```

---

## See Also

- [Customer Methods](customers.md) - Customer management API
- [Webhook Methods](webhooks.md) - Webhook subscriptions
- [Analytics Methods](analytics.md) - Analytics and metrics
- [Error Handling](../guides/error-handling.md) - Exception handling
- [Getting Started](../getting-started.md) - Quick start guide
