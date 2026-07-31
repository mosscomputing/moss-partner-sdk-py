# MOSS Partner SDK (Python)

Python SDK for the MOSS Partner API - Manage customers, configure governance, and monitor compliance.

## Installation

```bash
pip install moss-partner-sdk
```

## Quick Start

```python
import asyncio
from moss_partner_sdk import MossPartner

async def main():
    # Initialize the SDK
    moss = MossPartner(api_key="prt_xxx")

    # Create a customer
    customer = await moss.customers.create(
        external_id="acme_123",
        name="Acme Corp",
        email="admin@acme.com",
        governance={
            "jurisdictions": ["EU", "US"],
            "frameworks": ["eu_ai_act", "nist_ai_rmf"],
        },
    )

    print(f"Customer ID: {customer.id}")
    print(f"Sandbox Token: {customer.sandbox_token}")
    print(f"Status: {customer.status}")

    # Close the client
    await moss.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- **Customer Management**: Create, list, update, promote, suspend, and reactivate customers
- **Session Tokens**: Create temporary session tokens for customer dashboard access
- **Compliance Reports**: Generate ML-DSA-44 signed compliance reports (PDF/JSON)
- **Webhooks**: Manage webhook subscriptions for real-time event notifications
- **Analytics**: Access customer, compliance, and billing analytics
- **Async/Await**: Full async/await support using `httpx`
- **Type Hints**: Comprehensive type hints with Pydantic models
- **Error Handling**: Typed exceptions for API errors, network errors, and validation errors

## Usage Examples

### Customer Lifecycle

```python
async with MossPartner(api_key="prt_xxx") as moss:
    # Create customer
    customer = await moss.customers.create(
        external_id="acme_123",
        name="Acme Corp",
    )

    # List customers
    result = await moss.customers.list(status="pending", limit=10)
    for c in result.data:
        print(f"{c.name}: {c.status}")

    # Get customer by ID
    customer = await moss.customers.get(customer.id)

    # Update customer limits
    updated = await moss.customers.update(
        customer.id,
        limits={"agents": 50},
    )

    # Promote to production
    promoted = await moss.customers.promote(
        customer.id,
        attestation={
            "kyc_completed": True,
            "terms_accepted": True,
            "compliance_reviewed": True,
            "attested_by": "compliance@partner.com",
        },
        billing={
            "tier": "platform",
            "billing_email": "billing@acme.com",
        },
    )

    print(f"Production Token: {promoted.production_token}")
```

### Session Tokens

```python
async with MossPartner(api_key="prt_xxx") as moss:
    # Create temporary session token
    session = await moss.customers.create_session(
        customer_id="customer-uuid",
        purpose="Dashboard access",
        ttl_seconds=300,  # 5 minutes (API may cap at 900s)
    )

    print(f"Session Token: {session.session_token}")
    print(f"Expires At: {session.expires_at}")

    # Revoke session
    await moss.customers.revoke_session(
        customer_id="customer-uuid",
        session_token=session.session_token,
    )
```

### Compliance Reports (ML-DSA-44 Signed)

```python
async with MossPartner(api_key="prt_xxx") as moss:
    # Generate PDF report with ML-DSA-44 signature
    report = await moss.customers.compliance_report(
        customer_id="customer-uuid",
        format="pdf",
        frameworks=["eu_ai_act"],
    )

    print(f"Report ID: {report.report_id}")
    print(f"Signature: {report.signature}")  # ML-DSA-44 signature
    print(f"Key ID: {report.key_id}")
    print(f"Generated: {report.generated_at}")
```

### Webhooks

```python
from moss_partner_sdk import verify_webhook_signature

async with MossPartner(api_key="prt_xxx") as moss:
    # Create webhook
    webhook = await moss.webhooks.create(
        url="https://partner.com/webhooks/moss",
        events=["customer.*", "agent.anomaly_detected"],
    )

    print(f"Webhook ID: {webhook.id}")
    print(f"Secret: {webhook.secret}")

    # List webhooks
    webhooks = await moss.webhooks.list()

    # Delete webhook
    await moss.webhooks.delete(webhook.id)

# Verify webhook signature (in your webhook handler)
def handle_webhook(request):
    is_valid = verify_webhook_signature(
        payload=request.body,
        signature=request.headers["X-Moss-Signature"],
        secret=webhook.secret,
    )

    if not is_valid:
        return Response(status=401)

    # Process webhook event
    event = request.json()
    print(f"Event: {event['type']}")
```

### Analytics

```python
async with MossPartner(api_key="prt_xxx") as moss:
    analytics = await moss.analytics.get(period="30d")

    print(f"Total Customers: {analytics.customers.total}")
    print(f"Sandbox: {analytics.customers.sandbox}")
    print(f"Production: {analytics.customers.production}")
    print(f"Average Compliance Score: {analytics.compliance.average_score}")
    print(f"Current MRR: ${analytics.billing.current_mrr}")
```

## API Reference

### MossPartner

Main SDK client.

**Constructor**:
- `api_key` (str): Partner API key (must start with `"prt_"`)
- `base_url` (str, optional): Base URL for MOSS API (default: production)
- `timeout` (float, optional): Request timeout in seconds (default: 30)
- `retries` (int, optional): Number of retries for failed requests (default: 3)

**Methods**:
- `ping()`: Health check - returns `True` if API is reachable
- `close()`: Close HTTP client and release resources

**Resources**:
- `customers`: Customer management methods
- `webhooks`: Webhook management methods
- `analytics`: Analytics methods

### customers

- `create()`: Create a new customer
- `list()`: List customers with optional filtering
- `get()`: Get customer by ID
- `update()`: Update customer configuration
- `promote()`: Promote customer to production
- `suspend()`: Suspend a customer
- `reactivate()`: Reactivate a suspended customer
- `create_session()`: Create temporary session token
- `revoke_session()`: Revoke a session token
- `compliance_report()`: Generate ML-DSA-44 signed compliance report

### webhooks

- `create()`: Create webhook subscription
- `list()`: List webhook subscriptions
- `delete()`: Delete webhook subscription

### analytics

- `get()`: Get analytics for specified period

## Error Handling

```python
from moss_partner_sdk import MossAPIError, MossNetworkError

try:
    customer = await moss.customers.get("invalid-id")
except MossAPIError as e:
    print(f"API Error {e.status_code} ({e.code}): {e.message}")
except MossNetworkError as e:
    print(f"Network Error: {e.message}")
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linter
ruff check src tests

# Run type checker
mypy src

# Run tests
pytest tests/ -v

# Run integration tests (requires API key)
export MOSS_PARTNER_KEY="prt_xxx"
pytest tests/ -v -m integration
```

### Deployment Workflow

The SDK follows the MOSS staged deployment pattern:

```
main → staging → production
```

**Branches:**
- `main`: Development branch (all CI checks, integration tests, PyPI publish)
- `staging`: Pre-production validation (tests only, no publish)

**CI Behavior:**

| Job | main | staging |
|-----|------|---------|
| Tests (Python 3.9-3.12) | ✅ Runs | ✅ Runs |
| Integration Tests | ✅ Runs | ❌ Skipped |
| Publish to PyPI | ✅ Runs | ❌ Skipped |

**Workflow:**
1. Develop on feature branches
2. Merge to `main` → full CI + publish
3. Merge to `staging` → test validation only
4. Production releases via PyPI

## Requirements

- Python 3.9+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## License

MIT

## Support

- Documentation: https://docs.mosscomputing.com/sdks/python
- Issues: https://github.com/mosscomputing/moss-partner-sdk-py/issues
- Email: support@mosscomputing.com
