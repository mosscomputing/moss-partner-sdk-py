# Basic Usage Examples

Common patterns and quick-start code snippets for the MOSS Partner SDK.

## Installation and Setup

```bash
pip install moss-partner-sdk
```

```python
import asyncio
from moss_partner_sdk import MossPartner

# Initialize client
moss = MossPartner(api_key="prt_xxx")

# Or use context manager (recommended)
async with MossPartner(api_key="prt_xxx") as moss:
    # Your code here
    pass
```

## Example 1: Create a Customer

Create a new customer in sandbox mode:

```python
import asyncio
from moss_partner_sdk import MossPartner

async def create_customer():
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.create(
            external_id="acme_corp_123",
            name="Acme Corporation",
            email="admin@acmecorp.com"
        )

        print(f"Customer ID: {customer.id}")
        print(f"Sandbox Token: {customer.sandbox_token}")
        print(f"Status: {customer.status}")

        return customer

if __name__ == "__main__":
    asyncio.run(create_customer())
```

**Output:**
```
Customer ID: 550e8400-e29b-41d4-a716-446655440000
Sandbox Token: cust_sand_abc123xyz...
Status: sandbox_active
```

## Example 2: List All Customers

Retrieve all customers with pagination:

```python
async def list_all_customers():
    async with MossPartner(api_key="prt_xxx") as moss:
        result = await moss.customers.list(limit=50)

        print(f"Total: {result.pagination.total}")
        print(f"Showing: {len(result.data)}\n")

        for customer in result.data:
            print(f"- {customer.name} ({customer.status})")

        # Check if more pages exist
        if result.pagination.has_more:
            print(f"\nMore customers available (use offset={result.pagination.offset + result.pagination.limit})")

asyncio.run(list_all_customers())
```

**Output:**
```
Total: 125
Showing: 50

- Acme Corp (production_active)
- TechStart Inc (sandbox_active)
- Global Analytics (production_active)
...

More customers available (use offset=50)
```

## Example 3: Filter Customers by Status

Get only production customers:

```python
async def get_production_customers():
    async with MossPartner(api_key="prt_xxx") as moss:
        result = await moss.customers.list(
            status="production_active",
            limit=100
        )

        print(f"Production customers: {len(result.data)}")

        for customer in result.data:
            print(f"  {customer.name} - Score: {customer.compliance.score}")

asyncio.run(get_production_customers())
```

## Example 4: Get Customer by ID

Retrieve specific customer details:

```python
async def get_customer_details(customer_id: str):
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.get(customer_id)

        print(f"Name: {customer.name}")
        print(f"Status: {customer.status}")
        print(f"Compliance Score: {customer.compliance.score}")
        print(f"Agent Limit: {customer.limits.agents}")
        print(f"Created: {customer.created_at}")

asyncio.run(get_customer_details("550e8400-e29b-41d4-a716-446655440000"))
```

**Output:**
```
Name: Acme Corporation
Status: production_active
Compliance Score: 850
Agent Limit: 100
Created: 2026-01-15T10:30:00Z
```

## Example 5: Update Customer Limits

Increase resource limits for a customer:

```python
async def increase_limits(customer_id: str):
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.update(
            customer_id,
            limits={
                "agents": 200,
                "envelopes_per_month": 100000,
                "policies": 50
            }
        )

        print(f"Updated {customer.name}")
        print(f"New agent limit: {customer.limits.agents}")
        print(f"New envelope limit: {customer.limits.envelopes_per_month}")

asyncio.run(increase_limits("customer-uuid"))
```

## Example 6: Update Governance Configuration

Add frameworks to customer governance:

```python
async def update_governance(customer_id: str):
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.update(
            customer_id,
            governance={
                "jurisdictions": ["EU", "US", "UK"],
                "frameworks": [
                    "eu_ai_act",
                    "nist_ai_rmf",
                    "iso_42001",
                    "gdpr"
                ]
            }
        )

        print(f"Updated governance for {customer.name}")
        print(f"Jurisdictions: {', '.join(customer.governance.jurisdictions)}")
        print(f"Frameworks: {len(customer.governance.frameworks)}")

asyncio.run(update_governance("customer-uuid"))
```

## Example 7: Create Session Token

Generate temporary dashboard access:

```python
async def create_dashboard_session(customer_id: str):
    async with MossPartner(api_key="prt_xxx") as moss:
        session = await moss.customers.create_session(
            customer_id=customer_id,
            purpose="Support dashboard access",
            ttl_seconds=300  # API will use 900s (15 min)
        )

        # Generate login URL
        login_url = f"https://app.mosscomputing.com/login?session={session.session_token}"

        print(f"Login URL: {login_url}")
        print(f"Expires: {session.expires_at}")

        return login_url

asyncio.run(create_dashboard_session("customer-uuid"))
```

## Example 8: Revoke Session Token

Revoke a session immediately:

```python
async def revoke_session(customer_id: str, session_token: str):
    async with MossPartner(api_key="prt_xxx") as moss:
        await moss.customers.revoke_session(
            customer_id=customer_id,
            session_token=session_token
        )

        print("Session revoked successfully")

asyncio.run(revoke_session("customer-uuid", "session_abc123"))
```

## Example 9: Generate PDF Compliance Report

Generate a signed compliance report:

```python
async def generate_compliance_report(customer_id: str):
    async with MossPartner(api_key="prt_xxx") as moss:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf",
            frameworks=["eu_ai_act", "nist_ai_rmf"]
        )

        print(f"Report ID: {report.report_id}")
        print(f"Generated: {report.generated_at}")
        print(f"Signature: {report.signature[:50]}...")  # First 50 chars
        print(f"Key ID: {report.key_id}")

        if report.download_url:
            print(f"Download: {report.download_url}")

        return report

asyncio.run(generate_compliance_report("customer-uuid"))
```

## Example 10: Generate JSON Compliance Report

Get structured compliance data:

```python
async def get_compliance_data(customer_id: str):
    async with MossPartner(api_key="prt_xxx") as moss:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="json"
        )

        if report.data:
            print(f"Customer: {report.data.get('customer_name')}")
            print(f"Score: {report.data.get('compliance_score')}")
            print(f"Frameworks: {report.data.get('frameworks')}")

        return report.data

asyncio.run(get_compliance_data("customer-uuid"))
```

## Example 11: Create Webhook

Subscribe to customer events:

```python
async def setup_webhook():
    async with MossPartner(api_key="prt_xxx") as moss:
        webhook = await moss.webhooks.create(
            url="https://partner.com/webhooks/moss",
            events=[
                "customer.created",
                "customer.promoted",
                "agent.anomaly_detected"
            ]
        )

        print(f"Webhook ID: {webhook.id}")
        print(f"URL: {webhook.url}")
        print(f"Secret: {webhook.secret}")  # Store securely!
        print(f"Events: {', '.join(webhook.events)}")

        # Save secret for signature verification
        # save_webhook_secret(webhook.id, webhook.secret)

        return webhook

asyncio.run(setup_webhook())
```

## Example 12: List Webhooks

Get all active webhooks:

```python
async def list_webhooks():
    async with MossPartner(api_key="prt_xxx") as moss:
        result = await moss.webhooks.list()

        print(f"Active webhooks: {len(result.data)}\n")

        for webhook in result.data:
            print(f"ID: {webhook.id}")
            print(f"URL: {webhook.url}")
            print(f"Events: {', '.join(webhook.events)}")
            print(f"Active: {webhook.active}\n")

asyncio.run(list_webhooks())
```

## Example 13: Delete Webhook

Remove a webhook subscription:

```python
async def delete_webhook(webhook_id: str):
    async with MossPartner(api_key="prt_xxx") as moss:
        await moss.webhooks.delete(webhook_id)
        print(f"Webhook {webhook_id} deleted")

asyncio.run(delete_webhook("webhook-uuid"))
```

## Example 14: Get Analytics

Retrieve partner-level analytics:

```python
async def get_analytics():
    async with MossPartner(api_key="prt_xxx") as moss:
        analytics = await moss.analytics.get(period="30d")

        print(f"Period: {analytics.period}\n")

        print("Customers:")
        print(f"  Total: {analytics.customers.total}")
        print(f"  Production: {analytics.customers.production}")
        print(f"  Sandbox: {analytics.customers.sandbox}")
        print(f"  Suspended: {analytics.customers.suspended}\n")

        print("Compliance:")
        print(f"  Average Score: {analytics.compliance.average_score:.1f}")
        print(f"  At Risk: {analytics.compliance.at_risk_count}")
        print(f"  Non-Compliant: {analytics.compliance.non_compliant_count}\n")

        print("Billing:")
        print(f"  MRR: ${analytics.billing.current_mrr:,.2f}")
        print(f"  Paying Customers: {analytics.billing.total_customers_billed}")

        return analytics

asyncio.run(get_analytics())
```

**Output:**
```
Period: 30d

Customers:
  Total: 125
  Production: 87
  Sandbox: 35
  Suspended: 3

Compliance:
  Average Score: 782.5
  At Risk: 12
  Non-Compliant: 2

Billing:
  MRR: $45,750.00
  Paying Customers: 87
```

## Example 15: Health Check

Check API connectivity:

```python
async def health_check():
    async with MossPartner(api_key="prt_xxx") as moss:
        is_healthy = await moss.ping()

        if is_healthy:
            print("✓ MOSS API is reachable")
        else:
            print("✗ MOSS API is unreachable")

        return is_healthy

asyncio.run(health_check())
```

## Example 16: Iterate All Customers (Pagination)

Fetch all customers across multiple pages:

```python
async def get_all_customers():
    """Fetch all customers using pagination."""
    async with MossPartner(api_key="prt_xxx") as moss:
        all_customers = []
        offset = 0
        limit = 100

        while True:
            result = await moss.customers.list(limit=limit, offset=offset)
            all_customers.extend(result.data)

            print(f"Fetched {len(result.data)} customers (total: {len(all_customers)})")

            if not result.pagination.has_more:
                break

            offset += limit

        print(f"\nTotal customers: {len(all_customers)}")
        return all_customers

asyncio.run(get_all_customers())
```

## Example 17: Find Customer by External ID

Search for customer using your internal ID:

```python
async def find_by_external_id(external_id: str):
    """Find customer by external_id."""
    async with MossPartner(api_key="prt_xxx") as moss:
        result = await moss.customers.list()

        for customer in result.data:
            if customer.external_id == external_id:
                print(f"Found: {customer.name} ({customer.id})")
                return customer

        print(f"Customer with external_id={external_id} not found")
        return None

asyncio.run(find_by_external_id("acme_corp_123"))
```

## Example 18: Batch Customer Creation

Create multiple customers efficiently:

```python
async def create_multiple_customers(customers_data: list[dict]):
    """Create multiple customers in batch."""
    async with MossPartner(api_key="prt_xxx") as moss:
        created = []

        for data in customers_data:
            try:
                customer = await moss.customers.create(**data)
                created.append(customer)
                print(f"✓ Created: {customer.name}")

            except Exception as e:
                print(f"✗ Failed: {data['name']} - {e}")

        print(f"\nCreated {len(created)}/{len(customers_data)} customers")
        return created

# Example data
customers = [
    {"external_id": "cust_001", "name": "Customer One", "email": "one@example.com"},
    {"external_id": "cust_002", "name": "Customer Two", "email": "two@example.com"},
    {"external_id": "cust_003", "name": "Customer Three", "email": "three@example.com"},
]

asyncio.run(create_multiple_customers(customers))
```

## Example 19: Simple Error Handling

Handle common errors gracefully:

```python
from moss_partner_sdk.exceptions import MossAPIError

async def safe_get_customer(customer_id: str):
    """Get customer with error handling."""
    async with MossPartner(api_key="prt_xxx") as moss:
        try:
            customer = await moss.customers.get(customer_id)
            print(f"Found: {customer.name}")
            return customer

        except MossAPIError as e:
            if e.status_code == 404:
                print(f"Customer {customer_id} not found")
                return None
            else:
                print(f"API Error {e.status_code}: {e.message}")
                raise

asyncio.run(safe_get_customer("invalid-uuid"))
```

## Example 20: Context Manager Best Practice

Always use context manager for automatic cleanup:

```python
async def recommended_pattern():
    """Recommended usage pattern with context manager."""

    # ✓ GOOD: Context manager handles cleanup
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.get("customer-uuid")
        return customer

    # ✗ BAD: Manual cleanup required
    # moss = MossPartner(api_key="prt_xxx")
    # customer = await moss.customers.get("customer-uuid")
    # await moss.close()  # Easy to forget!
```

## See Also

- [Advanced Examples](advanced.md) - Complex patterns and optimization
- [Production Examples](production.md) - Production deployment patterns
- [Customer Lifecycle Guide](../guides/customer-lifecycle.md) - Complete lifecycle workflows
- [API Reference](../api-reference/) - Full API documentation
