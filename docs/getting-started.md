# Getting Started

Get up and running with the MOSS Partner SDK in 5 minutes.

---

## Prerequisites

- Python 3.9 or higher installed
- Partner API key from MOSS (see [Authentication](authentication.md))
- Basic understanding of async/await in Python

---

## Step 1: Install the SDK

```bash
pip install moss-partner-sdk
```

Verify installation:

```python
import moss_partner_sdk
print(moss_partner_sdk.__version__)  # 0.1.0
```

---

## Step 2: Set Your API Key

```bash
export MOSS_API_KEY="prt_your_api_key_here"
```

---

## Step 3: Your First Request

Create a file `quick_start.py`:

```python
import asyncio
import os
from moss_partner_sdk import MossPartner

async def main():
    # Initialize the SDK
    moss = MossPartner(api_key=os.environ["MOSS_API_KEY"])

    # Test connection
    is_connected = await moss.ping()
    print(f"Connected: {is_connected}")

    # Create a customer
    customer = await moss.customers.create(
        external_id="demo_customer_001",
        name="Demo Customer",
        email="demo@example.com"
    )

    print(f"✅ Customer created!")
    print(f"  ID: {customer.id}")
    print(f"  Status: {customer.status}")
    print(f"  Sandbox Token: {customer.sandbox_token}")

    # Close the client
    await moss.close()

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python quick_start.py
```

Expected output:

```
Connected: True
✅ Customer created!
  ID: cust_abc123...
  Status: pending
  Sandbox Token: ctok_xyz789...
```

---

## Step 4: Using Context Managers (Recommended)

Python's context managers automatically handle cleanup:

```python
import asyncio
import os
from moss_partner_sdk import MossPartner

async def main():
    # Automatically closes when exiting the 'async with' block
    async with MossPartner(api_key=os.environ["MOSS_API_KEY"]) as moss:
        customer = await moss.customers.create(
            external_id="demo_002",
            name="Another Customer"
        )
        print(f"Created: {customer.name}")

asyncio.run(main())
```

---

## Step 5: Handling Errors

```python
import asyncio
import os
from moss_partner_sdk import MossPartner, MossAPIError, MossNetworkError

async def main():
    try:
        async with MossPartner(api_key=os.environ["MOSS_API_KEY"]) as moss:
            customer = await moss.customers.create(
                external_id="demo_003",
                name="Safe Customer"
            )
            print(f"✅ Success: {customer.id}")

    except MossAPIError as e:
        print(f"❌ API Error {e.status_code}: {e.message}")

    except MossNetworkError as e:
        print(f"❌ Network Error: {e.message}")

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

asyncio.run(main())
```

---

## Common Workflows

### List All Customers

```python
async with MossPartner(api_key=os.environ["MOSS_API_KEY"]) as moss:
    result = await moss.customers.list(limit=10)

    print(f"Total customers: {result.total}")
    for customer in result.data:
        print(f"  - {customer.name} ({customer.status})")
```

### Get Customer by ID

```python
async with MossPartner(api_key=os.environ["MOSS_API_KEY"]) as moss:
    customer = await moss.customers.get("cust_abc123...")
    print(f"Customer: {customer.name}")
    print(f"Email: {customer.email}")
    print(f"Status: {customer.status}")
```

### Update Customer

```python
async with MossPartner(api_key=os.environ["MOSS_API_KEY"]) as moss:
    updated = await moss.customers.update(
        "cust_abc123...",
        limits={"agents": 50, "requests_per_day": 10000}
    )
    print(f"Updated limits: {updated.limits}")
```

### Promote to Production

```python
async with MossPartner(api_key=os.environ["MOSS_API_KEY"]) as moss:
    promoted = await moss.customers.promote(
        "cust_abc123...",
        attestation={
            "kyc_completed": True,
            "terms_accepted": True,
            "compliance_reviewed": True,
            "attested_by": "compliance@partner.com"
        },
        billing={
            "tier": "platform",
            "billing_email": "billing@customer.com"
        }
    )
    print(f"Production Token: {promoted.production_token}")
```

---

## Configuration Options

### Custom Base URL

For testing against staging or local environments:

```python
moss = MossPartner(
    api_key="prt_xxx",
    base_url="https://moss-api-staging.example.com"
)
```

### Custom Timeout

```python
moss = MossPartner(
    api_key="prt_xxx",
    timeout=60.0  # 60 seconds (default: 30)
)
```

### Custom Retry Logic

```python
moss = MossPartner(
    api_key="prt_xxx",
    retries=5  # Number of retries (default: 3)
)
```

### All Together

```python
moss = MossPartner(
    api_key=os.environ["MOSS_API_KEY"],
    base_url="https://api.mosscomputing.com",
    timeout=30.0,
    retries=3
)
```

---

## Complete Example

Here's a complete example showing the customer lifecycle:

```python
import asyncio
import os
from moss_partner_sdk import MossPartner, MossAPIError

async def customer_lifecycle_demo():
    """Demonstrate complete customer lifecycle."""

    async with MossPartner(api_key=os.environ["MOSS_API_KEY"]) as moss:
        try:
            # 1. Create customer
            print("1. Creating customer...")
            customer = await moss.customers.create(
                external_id="lifecycle_demo_001",
                name="Lifecycle Demo Corp",
                email="demo@lifecycle.com",
                governance={
                    "jurisdictions": ["EU", "US"],
                    "frameworks": ["eu_ai_act", "nist_ai_rmf"]
                }
            )
            print(f"   ✅ Created: {customer.id}")

            # 2. List customers
            print("\n2. Listing customers...")
            result = await moss.customers.list(status="pending", limit=5)
            print(f"   📋 Found {result.total} pending customers")

            # 3. Update limits
            print("\n3. Updating customer limits...")
            updated = await moss.customers.update(
                customer.id,
                limits={"agents": 100, "requests_per_day": 50000}
            )
            print(f"   ✅ Updated limits: {updated.limits}")

            # 4. Create session token
            print("\n4. Creating session token...")
            session = await moss.customers.create_session(
                customer.id,
                purpose="Quick demo access",
                ttl_seconds=300  # 5 minutes
            )
            print(f"   🎫 Session token: {session.session_token[:20]}...")
            print(f"   ⏰ Expires: {session.expires_at}")

            # 5. Promote to production
            print("\n5. Promoting to production...")
            promoted = await moss.customers.promote(
                customer.id,
                attestation={
                    "kyc_completed": True,
                    "terms_accepted": True,
                    "compliance_reviewed": True,
                    "attested_by": "demo@partner.com"
                },
                billing={
                    "tier": "starter",
                    "billing_email": "billing@lifecycle.com"
                }
            )
            print(f"   🚀 Production token: {promoted.production_token[:20]}...")

            # 6. Get analytics
            print("\n6. Fetching analytics...")
            analytics = await moss.analytics.get(period="30d")
            print(f"   📊 Total customers: {analytics.customers.total}")
            print(f"   💰 Current MRR: ${analytics.billing.current_mrr}")

            print("\n✅ Demo completed successfully!")

        except MossAPIError as e:
            print(f"\n❌ API Error {e.status_code}: {e.message}")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(customer_lifecycle_demo())
```

---

## Next Steps

Now that you're familiar with the basics:

1. **Learn More**:
   - [Customer Lifecycle Guide](guides/customer-lifecycle.md)
   - [Session Tokens Guide](guides/session-tokens.md)
   - [Webhooks Guide](guides/webhooks.md)

2. **API Reference**:
   - [MossPartner Client](api-reference/client.md)
   - [Customer Methods](api-reference/customers.md)
   - [Data Models](api-reference/models.md)

3. **Advanced Topics**:
   - [Error Handling](guides/error-handling.md)
   - [Production Best Practices](examples/production.md)
   - [Troubleshooting](troubleshooting.md)

---

## Getting Help

- **Documentation**: [Full docs](index.md)
- **Examples**: [Code examples](examples/basic-usage.md)
- **Issues**: [GitHub Issues](https://github.com/mosscomputing/moss-partner-sdk-py/issues)
- **Support**: support@mosscomputing.com
