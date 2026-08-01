# Customers API Reference

The `CustomersResource` provides methods for managing customer organizations in the MOSS Partner system.

## Overview

The customers resource is accessed via `moss.customers` and provides lifecycle management for customer organizations, including:

- Creating and managing customer accounts
- Promoting customers from sandbox to production
- Generating compliance reports with ML-DSA-44 signatures
- Managing customer sessions
- Suspending and reactivating customers

## Methods

### create()

Create a new customer organization.

```python
async def create(
    self,
    external_id: str,
    name: str,
    email: str | None = None,
    governance: dict[str, Any] | None = None,
) -> Customer
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `external_id` | `str` | Yes | Partner's unique identifier for this customer |
| `name` | `str` | Yes | Customer organization name |
| `email` | `str` | No | Customer admin email address |
| `governance` | `dict[str, Any]` | No | Governance configuration (jurisdictions, frameworks) |

#### Returns

`Customer` - The created customer with a sandbox token for testing.

#### Exceptions

- `MossAPIError` - If the API returns an error (e.g., duplicate external_id)
- `MossNetworkError` - If the network request fails
- `MossValidationError` - If input validation fails

#### Example: Basic Customer Creation

```python
from moss_partner_sdk import MossClient

async with MossClient(api_key="your_partner_key") as moss:
    customer = await moss.customers.create(
        external_id="acme_123",
        name="Acme Corp",
        email="admin@acme.com"
    )

    print(f"Customer created: {customer.id}")
    print(f"Sandbox token: {customer.sandbox_token}")
```

#### Example: Customer with Governance Configuration

```python
customer = await moss.customers.create(
    external_id="eu_customer_456",
    name="European Analytics Ltd",
    email="compliance@analytics.eu",
    governance={
        "jurisdictions": ["EU", "UK"],
        "frameworks": ["eu_ai_act", "gdpr", "nist_ai_rmf"],
        "settings": {
            "data_residency": "eu-west-1",
            "retention_days": 365
        }
    }
)
```

---

### list()

List customers with optional filtering and pagination.

```python
async def list(
    self,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> CustomerListResponse
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | `str` | No | None | Filter by status (see CustomerStatus enum) |
| `limit` | `int` | No | 100 | Maximum number of customers to return |
| `offset` | `int` | No | 0 | Pagination offset |

#### Valid Status Values

- `"pending"` - Customer created but not yet activated
- `"sandbox_active"` - Customer in sandbox mode
- `"production_active"` - Customer promoted to production
- `"suspended"` - Customer temporarily suspended
- `"deactivated"` - Customer permanently deactivated

#### Returns

`CustomerListResponse` - Contains a list of customers and pagination info.

#### Exceptions

- `MossAPIError` - If the API returns an error
- `MossNetworkError` - If the network request fails

#### Example: List All Active Customers

```python
response = await moss.customers.list(
    status="production_active",
    limit=50
)

print(f"Found {response.pagination.total} production customers")
for customer in response.data:
    print(f"- {customer.name} ({customer.id})")

# Handle pagination
if response.pagination.has_more:
    next_page = await moss.customers.list(
        status="production_active",
        offset=response.pagination.offset + response.pagination.limit
    )
```

#### Example: Iterate Through All Customers

```python
async def get_all_customers(moss: MossClient):
    """Fetch all customers using pagination."""
    all_customers = []
    offset = 0
    limit = 100

    while True:
        response = await moss.customers.list(limit=limit, offset=offset)
        all_customers.extend(response.data)

        if not response.pagination.has_more:
            break

        offset += limit

    return all_customers
```

---

### get()

Retrieve a specific customer by ID.

```python
async def get(self, customer_id: str) -> Customer
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | `str` | Yes | Customer UUID |

#### Returns

`Customer` - The customer details.

#### Exceptions

- `MossAPIError` - If customer not found (404) or other API error
- `MossNetworkError` - If the network request fails

#### Example

```python
customer = await moss.customers.get("550e8400-e29b-41d4-a716-446655440000")

print(f"Customer: {customer.name}")
print(f"Status: {customer.status}")
print(f"Compliance Score: {customer.compliance.score}")
print(f"Agent Limit: {customer.limits.agents}")
```

---

### update()

Update a customer's configuration.

```python
async def update(
    self,
    customer_id: str,
    limits: dict[str, Any] | None = None,
    governance: dict[str, Any] | None = None,
) -> Customer
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | `str` | Yes | Customer UUID |
| `limits` | `dict[str, Any]` | No | Resource limits to update |
| `governance` | `dict[str, Any]` | No | Governance configuration to update |

#### Returns

`Customer` - The updated customer.

#### Exceptions

- `MossAPIError` - If customer not found or update fails
- `MossNetworkError` - If the network request fails

#### Example: Update Resource Limits

```python
customer = await moss.customers.update(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    limits={
        "agents": 100,
        "envelopes_per_month": 50000,
        "policies": 50
    }
)

print(f"Updated agent limit: {customer.limits.agents}")
```

#### Example: Update Governance Settings

```python
customer = await moss.customers.update(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    governance={
        "jurisdictions": ["EU", "US", "CA"],
        "frameworks": ["eu_ai_act", "nist_ai_rmf", "iso_42001"]
    }
)
```

---

### promote()

Promote a customer from sandbox to production.

```python
async def promote(
    self,
    customer_id: str,
    attestation: dict[str, Any],
    billing: dict[str, Any],
) -> Customer
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | `str` | Yes | Customer UUID |
| `attestation` | `dict[str, Any]` | Yes | KYC attestation data |
| `billing` | `dict[str, Any]` | Yes | Billing configuration |

#### Attestation Structure

```python
{
    "kyc_completed": True,
    "verified_by": "partner_system_id",
    "verification_date": "2026-07-31T00:00:00Z",
    "risk_level": "low"
}
```

#### Billing Structure

```python
{
    "tier": "professional",  # Tier name from your pricing
    "billing_email": "billing@customer.com",
    "stripe_customer_id": "cus_xxx"  # Optional
}
```

#### Returns

`Customer` - The promoted customer with a production token.

#### Exceptions

- `MossAPIError` - If customer not eligible for promotion or promotion fails
- `MossNetworkError` - If the network request fails

#### Example

```python
customer = await moss.customers.promote(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    attestation={
        "kyc_completed": True,
        "verified_by": "partner_kyc_system",
        "verification_date": "2026-07-31T10:30:00Z",
        "risk_level": "low",
        "documents_verified": ["business_license", "tax_id"]
    },
    billing={
        "tier": "professional",
        "billing_email": "billing@acme.com",
        "stripe_customer_id": "cus_acme123"
    }
)

print(f"Production token: {customer.production_token}")
print(f"Promoted at: {customer.promoted_at}")
```

---

### suspend()

Suspend a customer temporarily.

```python
async def suspend(
    self,
    customer_id: str,
    reason: str,
    grace_period_hours: int | None = None,
) -> Customer
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | `str` | Yes | Customer UUID |
| `reason` | `str` | Yes | Suspension reason |
| `grace_period_hours` | `int` | No | Hours before full suspension takes effect |

#### Returns

`Customer` - The suspended customer.

#### Exceptions

- `MossAPIError` - If customer not found or suspension fails
- `MossNetworkError` - If the network request fails

#### Example: Immediate Suspension

```python
customer = await moss.customers.suspend(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    reason="Payment failure - card declined"
)

print(f"Customer suspended at: {customer.suspended_at}")
```

#### Example: Suspension with Grace Period

```python
customer = await moss.customers.suspend(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    reason="Payment overdue - invoice #12345",
    grace_period_hours=48
)

# Customer has 48 hours to resolve before full suspension
```

---

### reactivate()

Reactivate a suspended customer.

```python
async def reactivate(
    self,
    customer_id: str,
    resolution: dict[str, Any],
) -> Customer
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | `str` | Yes | Customer UUID |
| `resolution` | `dict[str, Any]` | Yes | Resolution information |

#### Resolution Structure

```python
{
    "resolved_by": "support_agent_id",
    "resolution_date": "2026-07-31T00:00:00Z",
    "notes": "Payment received, account reactivated"
}
```

#### Returns

`Customer` - The reactivated customer.

#### Exceptions

- `MossAPIError` - If customer not found or reactivation fails
- `MossNetworkError` - If the network request fails

#### Example

```python
customer = await moss.customers.reactivate(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    resolution={
        "resolved_by": "support_team",
        "resolution_date": "2026-07-31T14:30:00Z",
        "notes": "Payment received via wire transfer",
        "payment_id": "wire_abc123"
    }
)

print(f"Customer reactivated: {customer.status}")
```

---

### create_session()

Create a temporary session token for a customer.

```python
async def create_session(
    self,
    customer_id: str,
    purpose: str,
    ttl_seconds: int = 300,
) -> SessionResponse
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `customer_id` | `str` | Yes | - | Customer UUID |
| `purpose` | `str` | Yes | - | Purpose description for audit logs |
| `ttl_seconds` | `int` | No | 300 | Requested TTL (API may override to 900s) |

#### Returns

`SessionResponse` - Contains the session token and expiration time.

#### Exceptions

- `MossAPIError` - If customer not found or session creation fails
- `MossNetworkError` - If the network request fails

#### Note

According to learning LC018, the API always uses a 900-second (15-minute) TTL regardless of the requested TTL. This is a known limitation.

#### Example: Support Dashboard Access

```python
session = await moss.customers.create_session(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    purpose="Support dashboard access",
    ttl_seconds=300  # Note: API may use 900s instead
)

# Generate a one-time login link
login_url = f"https://app.mosscomputing.com/login?session={session.session_token}"
print(f"Session expires at: {session.expires_at}")
```

#### Example: Embedded Dashboard

```python
# Create session for embedding dashboard in partner app
session = await moss.customers.create_session(
    customer_id=customer_id,
    purpose="Embedded dashboard widget"
)

# Use session token in iframe
iframe_url = f"https://app.mosscomputing.com/embed?token={session.session_token}"
```

---

### revoke_session()

Revoke a session token immediately.

```python
async def revoke_session(self, customer_id: str, session_token: str) -> None
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | `str` | Yes | Customer UUID |
| `session_token` | `str` | Yes | Session token to revoke |

#### Returns

`None`

#### Exceptions

- `MossAPIError` - If session not found or revocation fails
- `MossNetworkError` - If the network request fails

#### Example

```python
# Revoke session when user logs out
await moss.customers.revoke_session(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    session_token="session_abc123xyz"
)

print("Session revoked successfully")
```

---

### compliance_report()

Generate an ML-DSA-44 signed compliance report.

```python
async def compliance_report(
    self,
    customer_id: str,
    format: str = "pdf",
    frameworks: Sequence[str] | None = None,
) -> ComplianceReportResponse
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `customer_id` | `str` | Yes | - | Customer UUID |
| `format` | `str` | No | "pdf" | Report format ("pdf" or "json") |
| `frameworks` | `Sequence[str]` | No | None | Frameworks to include in report |

#### Valid Framework Values

- `"eu_ai_act"` - EU AI Act compliance
- `"nist_ai_rmf"` - NIST AI Risk Management Framework
- `"iso_42001"` - ISO 42001 AI Management System
- `"gdpr"` - GDPR data protection
- `"ccpa"` - California Consumer Privacy Act

#### Returns

`ComplianceReportResponse` - Contains the report with ML-DSA-44 signature.

#### Exceptions

- `MossAPIError` - If customer not found or report generation fails
- `MossNetworkError` - If the network request fails
- `MossParseError` - If PDF signature trailer parsing fails

#### Notes

- ML-DSA-44 signatures are approximately 3000-5000 characters (from LC018)
- PDF format extracts signature from PDF trailer (%%MOSS-SIGNATURE-V1 block)
- JSON format includes signature in response body
- Reports are cryptographically signed for non-repudiation

#### Example: PDF Report

```python
report = await moss.customers.compliance_report(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    format="pdf",
    frameworks=["eu_ai_act", "nist_ai_rmf"]
)

print(f"Report ID: {report.report_id}")
print(f"Signed with key: {report.key_id}")
print(f"Generated at: {report.generated_at}")
print(f"Signature (first 100 chars): {report.signature[:100]}...")

# Download URL for PDF
if report.download_url:
    print(f"Download at: {report.download_url}")
```

#### Example: JSON Report

```python
report = await moss.customers.compliance_report(
    customer_id="550e8400-e29b-41d4-a716-446655440000",
    format="json",
    frameworks=["iso_42001", "gdpr"]
)

# JSON format includes structured data
print(f"Report data: {report.data}")
```

#### Example: Verify Signature

```python
# The signature can be verified using MOSS public key
from moss_partner_sdk import verify_ml_dsa_signature

is_valid = verify_ml_dsa_signature(
    payload=report.data,
    signature=report.signature,
    key_id=report.key_id
)

if is_valid:
    print("Report signature verified - authentic and unmodified")
else:
    print("WARNING: Signature verification failed")
```

---

## Common Patterns

### Customer Onboarding Flow

```python
async def onboard_customer(moss: MossClient, external_id: str, name: str):
    """Complete customer onboarding workflow."""

    # 1. Create customer in sandbox
    customer = await moss.customers.create(
        external_id=external_id,
        name=name,
        email=f"admin@{name.lower().replace(' ', '')}.com",
        governance={
            "jurisdictions": ["US"],
            "frameworks": ["nist_ai_rmf"]
        }
    )

    print(f"Created customer {customer.id}")
    print(f"Sandbox token: {customer.sandbox_token}")

    # 2. Wait for customer testing/validation
    # ... (customer tests their integration) ...

    # 3. Promote to production after KYC
    customer = await moss.customers.promote(
        customer_id=customer.id,
        attestation={
            "kyc_completed": True,
            "verified_by": "partner_system",
            "verification_date": datetime.now(timezone.utc).isoformat()
        },
        billing={
            "tier": "professional",
            "billing_email": f"billing@{name.lower().replace(' ', '')}.com"
        }
    )

    print(f"Production token: {customer.production_token}")

    return customer
```

### Health Check and Monitoring

```python
async def monitor_customers(moss: MossClient):
    """Monitor customer health and compliance."""

    # Get all production customers
    response = await moss.customers.list(
        status="production_active",
        limit=100
    )

    at_risk = []
    for customer in response.data:
        # Check compliance score
        if customer.compliance.score < 600:
            at_risk.append(customer)

            # Generate compliance report
            report = await moss.customers.compliance_report(
                customer_id=customer.id,
                format="json"
            )

            print(f"⚠️  {customer.name} - Score: {customer.compliance.score}")
            print(f"   Issues: {len(customer.compliance.issues)}")

    return at_risk
```

### Session-Based Embedding

```python
from datetime import datetime, timedelta

async def get_embedded_url(moss: MossClient, customer_id: str) -> dict:
    """Generate embedded dashboard URL with session token."""

    session = await moss.customers.create_session(
        customer_id=customer_id,
        purpose="Partner portal embedded widget"
    )

    return {
        "iframe_url": f"https://app.mosscomputing.com/embed?token={session.session_token}",
        "expires_at": session.expires_at,
        "valid_for_minutes": 15  # API default
    }
```

---

## See Also

- [Models Reference](models.md) - Details on Customer, SessionResponse, and other models
- [Exceptions Reference](exceptions.md) - Error handling
- [Webhooks Reference](webhooks.md) - Event notifications for customer changes
- [Getting Started Guide](../getting-started.md) - End-to-end examples
