# Advanced Examples

Advanced techniques, patterns, and optimizations for the MOSS Partner SDK.

## Concurrent Operations with asyncio

### Parallel Customer Creation

Create multiple customers concurrently:

```python
import asyncio
from moss_partner_sdk import MossPartner

async def create_customers_concurrently(customers_data: list[dict]):
    """Create multiple customers in parallel."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Create tasks for parallel execution
        tasks = [
            moss.customers.create(**data)
            for data in customers_data
        ]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        created = []
        failed = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append({
                    "data": customers_data[i],
                    "error": str(result)
                })
            else:
                created.append(result)

        print(f"Created: {len(created)}, Failed: {len(failed)}")

        return {"created": created, "failed": failed}


# Example usage
customers = [
    {"external_id": f"cust_{i:03d}", "name": f"Customer {i}", "email": f"customer{i}@example.com"}
    for i in range(1, 11)
]

asyncio.run(create_customers_concurrently(customers))
```

### Parallel Data Fetching

Fetch multiple customers concurrently:

```python
async def fetch_customers_parallel(customer_ids: list[str]):
    """Fetch multiple customers in parallel."""
    async with MossPartner(api_key="prt_xxx") as moss:
        tasks = [moss.customers.get(cid) for cid in customer_ids]
        customers = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors
        valid_customers = [c for c in customers if not isinstance(c, Exception)]

        print(f"Fetched {len(valid_customers)}/{len(customer_ids)} customers")

        return valid_customers


customer_ids = ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"]
asyncio.run(fetch_customers_parallel(customer_ids))
```

### Rate-Limited Concurrent Operations

Execute concurrent operations with rate limiting:

```python
import asyncio
from asyncio import Semaphore

async def create_with_rate_limit(customers_data: list[dict], max_concurrent: int = 5):
    """Create customers with concurrency limit."""
    async with MossPartner(api_key="prt_xxx") as moss:
        semaphore = Semaphore(max_concurrent)

        async def create_one(data: dict):
            async with semaphore:
                return await moss.customers.create(**data)

        tasks = [create_one(data) for data in customers_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        created = [r for r in results if not isinstance(r, Exception)]
        print(f"Created {len(created)}/{len(customers_data)} customers")

        return created


customers = [{"external_id": f"c{i}", "name": f"Customer {i}"} for i in range(20)]
asyncio.run(create_with_rate_limit(customers, max_concurrent=5))
```

## Advanced Error Recovery

### Retry with Exponential Backoff

Implement robust retry logic:

```python
import asyncio
from moss_partner_sdk.exceptions import MossAPIError, MossNetworkError

async def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0):
    """Execute function with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return await func()

        except (MossAPIError, MossNetworkError) as e:
            if isinstance(e, MossAPIError):
                # Don't retry client errors (4xx except 429)
                if 400 <= e.status_code < 500 and e.status_code != 429:
                    raise

            if attempt == max_retries - 1:
                raise

            delay = initial_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            await asyncio.sleep(delay)


async def get_customer_robust(moss, customer_id: str):
    """Get customer with retry logic."""
    return await retry_with_backoff(
        lambda: moss.customers.get(customer_id),
        max_retries=5,
        initial_delay=2.0
    )
```

### Fallback Strategy

Implement fallback when primary operation fails:

```python
async def get_customer_with_fallback(moss, customer_id: str, external_id: str):
    """Get customer with fallback to external_id lookup."""
    try:
        # Try primary lookup by ID
        return await moss.customers.get(customer_id)

    except MossAPIError as e:
        if e.status_code == 404:
            # Fallback: Search by external_id
            print(f"Customer {customer_id} not found, searching by external_id...")

            result = await moss.customers.list()
            for customer in result.data:
                if customer.external_id == external_id:
                    return customer

        raise
```

## Batch Operations

### Batch Update with Progress Tracking

Update multiple customers with progress feedback:

```python
from typing import Callable

async def batch_update_customers(
    moss,
    customer_ids: list[str],
    update_data: dict,
    progress_callback: Callable[[int, int], None] | None = None
):
    """Update multiple customers with progress tracking."""
    results = {"success": [], "failed": []}

    for i, customer_id in enumerate(customer_ids):
        try:
            customer = await moss.customers.update(customer_id, **update_data)
            results["success"].append(customer)

            if progress_callback:
                progress_callback(i + 1, len(customer_ids))

        except Exception as e:
            results["failed"].append({
                "customer_id": customer_id,
                "error": str(e)
            })

    return results


# Usage with progress callback
def print_progress(current: int, total: int):
    percent = (current / total) * 100
    print(f"Progress: {current}/{total} ({percent:.1f}%)")


async with MossPartner(api_key="prt_xxx") as moss:
    customer_ids = ["uuid1", "uuid2", "uuid3"]
    update_data = {"limits": {"agents": 200}}

    results = await batch_update_customers(
        moss,
        customer_ids,
        update_data,
        progress_callback=print_progress
    )
```

## Custom HTTP Configuration

### Custom Timeout and Retries

Configure HTTP client behavior:

```python
from moss_partner_sdk import MossPartner

# Custom timeout (60 seconds)
async with MossPartner(
    api_key="prt_xxx",
    timeout=60.0
) as moss:
    # Long-running operations
    report = await moss.customers.compliance_report("customer-uuid")


# Custom retry count
async with MossPartner(
    api_key="prt_xxx",
    retries=5  # Retry up to 5 times
) as moss:
    customer = await moss.customers.get("customer-uuid")
```

### Custom Base URL (for testing)

Use custom API endpoint:

```python
# Point to staging environment
async with MossPartner(
    api_key="prt_xxx",
    base_url="https://api.staging.mosscomputing.com"
) as moss:
    customer = await moss.customers.get("customer-uuid")
```

## Multi-Environment Configuration

### Environment-Based Configuration

Manage multiple environments:

```python
import os
from dataclasses import dataclass

@dataclass
class MossConfig:
    """Configuration for MOSS Partner SDK."""
    api_key: str
    base_url: str
    timeout: float = 30.0
    retries: int = 3


class ConfigManager:
    """Manage MOSS configurations for different environments."""

    CONFIGS = {
        "production": MossConfig(
            api_key=os.getenv("MOSS_PROD_API_KEY"),
            base_url="https://api.mosscomputing.com",
            timeout=30.0,
            retries=3
        ),
        "staging": MossConfig(
            api_key=os.getenv("MOSS_STAGING_API_KEY"),
            base_url="https://api.staging.mosscomputing.com",
            timeout=60.0,
            retries=5
        ),
        "development": MossConfig(
            api_key=os.getenv("MOSS_DEV_API_KEY"),
            base_url="http://localhost:8000",
            timeout=120.0,
            retries=1
        )
    }

    @classmethod
    def get_config(cls, env: str = None) -> MossConfig:
        """Get configuration for environment."""
        env = env or os.getenv("MOSS_ENV", "production")
        return cls.CONFIGS[env]


# Usage
async def get_client(env: str = None):
    """Get MOSS client for environment."""
    config = ConfigManager.get_config(env)

    return MossPartner(
        api_key=config.api_key,
        base_url=config.base_url,
        timeout=config.timeout,
        retries=config.retries
    )


# Use production client
async with await get_client("production") as moss:
    customer = await moss.customers.get("customer-uuid")
```

## Testing Patterns

### Mock MOSS Client

Create mock client for testing:

```python
from unittest.mock import AsyncMock, MagicMock
from moss_partner_sdk import MossPartner
from moss_partner_sdk.models import Customer, CustomerStatus

def create_mock_moss_client():
    """Create mock MOSS client for testing."""
    mock_moss = MagicMock(spec=MossPartner)

    # Mock customers resource
    mock_moss.customers = MagicMock()

    # Mock customer data
    mock_customer = Customer(
        id="test-uuid",
        external_id="test_123",
        name="Test Customer",
        email="test@example.com",
        status=CustomerStatus.SANDBOX_ACTIVE,
        sandbox_token="test_token",
        production_token=None,
        governance={"jurisdictions": [], "frameworks": []},
        limits={"agents": 10},
        compliance={"score": 800, "status": "compliant", "issues": [], "last_assessment": "2026-07-31"},
        billing=None,
        created_at="2026-07-31T00:00:00Z",
        updated_at="2026-07-31T00:00:00Z",
        promoted_at=None,
        suspended_at=None
    )

    # Mock methods
    mock_moss.customers.get = AsyncMock(return_value=mock_customer)
    mock_moss.customers.create = AsyncMock(return_value=mock_customer)
    mock_moss.customers.list = AsyncMock(return_value={
        "data": [mock_customer],
        "pagination": {"total": 1, "limit": 100, "offset": 0, "has_more": False}
    })

    return mock_moss


# Usage in tests
async def test_my_function():
    """Test function using mock MOSS client."""
    mock_moss = create_mock_moss_client()

    # Test your code
    customer = await mock_moss.customers.get("test-uuid")
    assert customer.name == "Test Customer"
```

### Integration Test Helper

Helper for integration tests:

```python
import os
import pytest

@pytest.fixture
async def moss_client():
    """Fixture providing MOSS client for integration tests."""
    api_key = os.getenv("MOSS_TEST_API_KEY")

    if not api_key:
        pytest.skip("MOSS_TEST_API_KEY not set")

    async with MossPartner(api_key=api_key) as moss:
        yield moss


@pytest.mark.asyncio
async def test_create_customer(moss_client):
    """Test customer creation."""
    customer = await moss_client.customers.create(
        external_id=f"test_{int(time.time())}",
        name="Test Customer"
    )

    assert customer.id is not None
    assert customer.status == CustomerStatus.SANDBOX_ACTIVE

    # Cleanup
    # (implement cleanup logic)
```

## Caching Strategies

### Simple In-Memory Cache

Cache customer data to reduce API calls:

```python
from datetime import datetime, timedelta
from typing import Dict, Tuple

class CustomerCache:
    """Simple in-memory cache for customer data."""

    def __init__(self, ttl_seconds: int = 300):
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache: Dict[str, Tuple[Customer, datetime]] = {}

    def get(self, customer_id: str) -> Customer | None:
        """Get customer from cache if not expired."""
        if customer_id in self.cache:
            customer, cached_at = self.cache[customer_id]

            if datetime.now() - cached_at < self.ttl:
                return customer

            # Expired, remove from cache
            del self.cache[customer_id]

        return None

    def set(self, customer_id: str, customer: Customer):
        """Add customer to cache."""
        self.cache[customer_id] = (customer, datetime.now())

    def invalidate(self, customer_id: str):
        """Remove customer from cache."""
        self.cache.pop(customer_id, None)

    def clear(self):
        """Clear entire cache."""
        self.cache.clear()


# Usage
cache = CustomerCache(ttl_seconds=300)

async def get_customer_cached(moss, customer_id: str):
    """Get customer with caching."""
    # Check cache first
    cached = cache.get(customer_id)
    if cached:
        print("Cache hit")
        return cached

    # Fetch from API
    print("Cache miss - fetching from API")
    customer = await moss.customers.get(customer_id)

    # Store in cache
    cache.set(customer_id, customer)

    return customer
```

### Redis Cache

Use Redis for distributed caching:

```python
import json
import redis.asyncio as redis
from datetime import timedelta

class RedisCustomerCache:
    """Redis-based customer cache."""

    def __init__(self, redis_url: str = "redis://localhost:6379", ttl_seconds: int = 300):
        self.redis = redis.from_url(redis_url)
        self.ttl = ttl_seconds

    async def get(self, customer_id: str) -> Customer | None:
        """Get customer from Redis cache."""
        cached = await self.redis.get(f"customer:{customer_id}")

        if cached:
            data = json.loads(cached)
            return Customer(**data)

        return None

    async def set(self, customer_id: str, customer: Customer):
        """Store customer in Redis cache."""
        key = f"customer:{customer_id}"
        value = customer.model_dump_json()

        await self.redis.setex(key, self.ttl, value)

    async def invalidate(self, customer_id: str):
        """Remove customer from cache."""
        await self.redis.delete(f"customer:{customer_id}")

    async def close(self):
        """Close Redis connection."""
        await self.redis.close()


# Usage
async def use_redis_cache():
    cache = RedisCustomerCache()

    try:
        async with MossPartner(api_key="prt_xxx") as moss:
            # Try cache first
            customer = await cache.get("customer-uuid")

            if not customer:
                # Fetch from API
                customer = await moss.customers.get("customer-uuid")
                await cache.set("customer-uuid", customer)

            return customer

    finally:
        await cache.close()
```

## Performance Optimization

### Connection Pooling

Reuse MOSS client across requests:

```python
class MossClientPool:
    """Connection pool for MOSS client."""

    def __init__(self, api_key: str, pool_size: int = 5):
        self.api_key = api_key
        self.pool_size = pool_size
        self.clients = []

    async def get_client(self) -> MossPartner:
        """Get client from pool or create new one."""
        if self.clients:
            return self.clients.pop()

        return MossPartner(api_key=self.api_key)

    async def release_client(self, client: MossPartner):
        """Return client to pool."""
        if len(self.clients) < self.pool_size:
            self.clients.append(client)
        else:
            await client.close()

    async def close_all(self):
        """Close all clients in pool."""
        for client in self.clients:
            await client.close()
        self.clients.clear()


# Usage
pool = MossClientPool(api_key="prt_xxx", pool_size=5)

try:
    # Get client from pool
    moss = await pool.get_client()

    try:
        customer = await moss.customers.get("customer-uuid")
    finally:
        # Return to pool
        await pool.release_client(moss)

finally:
    # Cleanup
    await pool.close_all()
```

### Batch Analytics Collection

Collect analytics efficiently:

```python
async def collect_customer_analytics(moss, customer_ids: list[str]):
    """Collect analytics for multiple customers efficiently."""
    # Fetch customers in parallel
    semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

    async def fetch_one(customer_id: str):
        async with semaphore:
            return await moss.customers.get(customer_id)

    tasks = [fetch_one(cid) for cid in customer_ids]
    customers = await asyncio.gather(*tasks, return_exceptions=True)

    # Aggregate analytics
    analytics = {
        "total": len(customers),
        "by_status": {},
        "avg_compliance_score": 0,
        "total_agents": 0
    }

    valid_customers = [c for c in customers if not isinstance(c, Exception)]

    for customer in valid_customers:
        # Count by status
        status = customer.status.value
        analytics["by_status"][status] = analytics["by_status"].get(status, 0) + 1

        # Sum compliance scores
        analytics["avg_compliance_score"] += customer.compliance.score

        # Sum agents
        analytics["total_agents"] += customer.limits.agents

    # Calculate averages
    if valid_customers:
        analytics["avg_compliance_score"] /= len(valid_customers)

    return analytics
```

## See Also

- [Basic Usage Examples](basic-usage.md) - Common patterns and quick starts
- [Production Examples](production.md) - Production deployment patterns
- [Error Handling Guide](../guides/error-handling.md) - Comprehensive error handling
- [API Reference](../api-reference/) - Full API documentation
