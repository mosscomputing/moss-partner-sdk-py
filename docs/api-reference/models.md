# Models API Reference

Pydantic models used throughout the MOSS Partner SDK for type-safe data representation.

## Overview

All models are defined in `moss_partner_sdk.models` and use Pydantic for validation and serialization. Models provide:

- Type validation
- JSON serialization/deserialization
- IDE autocomplete support
- Clear field documentation

## Enums

### CustomerStatus

Status of a customer account.

```python
from moss_partner_sdk.models import CustomerStatus
```

**Values:**

| Value | Description |
|-------|-------------|
| `PENDING` | Customer created but not yet activated |
| `SANDBOX_ACTIVE` | Customer in sandbox/testing mode |
| `PRODUCTION_ACTIVE` | Customer promoted to production |
| `SUSPENDED` | Customer temporarily suspended |
| `DEACTIVATED` | Customer permanently deactivated |

**Example:**

```python
from moss_partner_sdk.models import CustomerStatus

# Check customer status
if customer.status == CustomerStatus.PRODUCTION_ACTIVE:
    print("Customer is in production")

# Filter by status
response = await moss.customers.list(status=CustomerStatus.SANDBOX_ACTIVE.value)
```

---

## Customer Models

### Customer

Represents a customer organization in the MOSS Partner system.

```python
from moss_partner_sdk.models import Customer
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Customer UUID (mapped from API's `customerId`) |
| `external_id` | `str` | Partner's unique identifier for this customer |
| `name` | `str` | Customer organization name |
| `email` | `str` | Customer admin email |
| `status` | `CustomerStatus` | Current account status |
| `sandbox_token` | `str \| None` | Sandbox API token (mapped from `credentials.customerToken.token`) |
| `production_token` | `str \| None` | Production API token (mapped from `credentials.productionToken.token`) |
| `governance` | `Governance` | Governance configuration |
| `limits` | `ResourceLimits` | Resource limits and quotas |
| `compliance` | `ComplianceInfo` | Compliance assessment information |
| `billing` | `BillingInfo \| None` | Billing information (if promoted) |
| `created_at` | `datetime` | Account creation timestamp |
| `updated_at` | `datetime` | Last update timestamp |
| `promoted_at` | `datetime \| None` | Production promotion timestamp |
| `suspended_at` | `datetime \| None` | Suspension timestamp |

**Example:**

```python
customer = await moss.customers.get("550e8400-e29b-41d4-a716-446655440000")

print(f"ID: {customer.id}")
print(f"External ID: {customer.external_id}")
print(f"Name: {customer.name}")
print(f"Status: {customer.status.value}")

# Access nested models
print(f"Agent limit: {customer.limits.agents}")
print(f"Compliance score: {customer.compliance.score}")

# Serialize to dict
customer_dict = customer.model_dump()

# Serialize to JSON
customer_json = customer.model_dump_json()
```

---

### Governance

Governance configuration for a customer.

```python
from moss_partner_sdk.models import Governance
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `jurisdictions` | `list[str]` | `[]` | Regulatory jurisdictions (e.g., "EU", "US") |
| `frameworks` | `list[str]` | `[]` | Compliance frameworks (e.g., "eu_ai_act") |
| `settings` | `dict[str, Any] \| None` | `None` | Additional governance settings |

**Example:**

```python
from moss_partner_sdk.models import Governance

# Create governance config
governance = Governance(
    jurisdictions=["EU", "UK", "US"],
    frameworks=["eu_ai_act", "nist_ai_rmf", "iso_42001"],
    settings={
        "data_residency": "eu-west-1",
        "retention_days": 365,
        "encryption_at_rest": True
    }
)

# Use in customer creation
customer = await moss.customers.create(
    external_id="eu_customer",
    name="European Customer",
    governance=governance.model_dump()
)
```

---

### ResourceLimits

Resource limits and quotas for a customer.

```python
from moss_partner_sdk.models import ResourceLimits
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agents` | `int` | Yes | Maximum number of AI agents |
| `envelopes_per_month` | `int \| None` | No | Monthly signature envelope limit |
| `policies` | `int \| None` | No | Maximum number of governance policies |

**Example:**

```python
from moss_partner_sdk.models import ResourceLimits

# Check current limits
if customer.limits.agents < 100:
    # Upgrade customer limits
    updated = await moss.customers.update(
        customer_id=customer.id,
        limits={
            "agents": 100,
            "envelopes_per_month": 50000,
            "policies": 50
        }
    )
    print(f"New agent limit: {updated.limits.agents}")
```

---

### ComplianceInfo

Compliance assessment information for a customer.

```python
from moss_partner_sdk.models import ComplianceInfo
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `score` | `int` | Compliance score (typically 0-1000) |
| `status` | `str` | Status (e.g., "compliant", "at_risk", "non_compliant") |
| `issues` | `list[ComplianceIssue]` | List of compliance issues found |
| `last_assessment` | `datetime` | Timestamp of last assessment |

**Example:**

```python
if customer.compliance.score < 600:
    print(f"⚠️  Low compliance score: {customer.compliance.score}")
    print(f"Issues found: {len(customer.compliance.issues)}")

    for issue in customer.compliance.issues:
        print(f"- [{issue.severity}] {issue.description}")
        if issue.remediation_url:
            print(f"  Remediation: {issue.remediation_url}")
```

---

### ComplianceIssue

A compliance issue found during assessment.

```python
from moss_partner_sdk.models import ComplianceIssue
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Issue UUID |
| `severity` | `str` | Severity level (e.g., "high", "medium", "low") |
| `description` | `str` | Human-readable issue description |
| `framework` | `str` | Related framework (e.g., "eu_ai_act") |
| `remediation_url` | `str \| None` | Link to remediation guidance |

**Example:**

```python
for issue in customer.compliance.issues:
    if issue.severity == "high":
        print(f"🚨 High severity issue: {issue.description}")
        print(f"   Framework: {issue.framework}")
        if issue.remediation_url:
            print(f"   Fix: {issue.remediation_url}")
```

---

### BillingInfo

Billing information for a customer (only present for production customers).

```python
from moss_partner_sdk.models import BillingInfo
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `tier` | `str` | Billing tier name |
| `billing_email` | `str` | Billing contact email |
| `stripe_customer_id` | `str \| None` | Stripe customer ID (if applicable) |
| `current_mrr` | `float \| None` | Current monthly recurring revenue |

**Example:**

```python
if customer.billing:
    print(f"Tier: {customer.billing.tier}")
    print(f"MRR: ${customer.billing.current_mrr}")
    print(f"Billing email: {customer.billing.billing_email}")
else:
    print("Customer not yet promoted to production")
```

---

### CustomerListResponse

Response from the `list()` endpoint containing customers and pagination.

```python
from moss_partner_sdk.models import CustomerListResponse
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | `list[Customer]` | List of customers |
| `pagination` | `PaginationInfo` | Pagination metadata |

**Example:**

```python
response = await moss.customers.list(limit=50)

print(f"Returned {len(response.data)} customers")
print(f"Total: {response.pagination.total}")

if response.pagination.has_more:
    print("More results available")
```

---

### PaginationInfo

Pagination metadata for list responses.

```python
from moss_partner_sdk.models import PaginationInfo
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | `int` | Total number of items available |
| `limit` | `int` | Maximum items per page |
| `offset` | `int` | Current offset |
| `has_more` | `bool` | Whether more items are available |

**Example:**

```python
async def get_all_customers(moss):
    """Iterate through all customers using pagination."""
    all_customers = []
    offset = 0

    while True:
        response = await moss.customers.list(limit=100, offset=offset)
        all_customers.extend(response.data)

        if not response.pagination.has_more:
            break

        offset += response.pagination.limit

    return all_customers
```

---

## Session Models

### SessionResponse

Response from the `create_session()` endpoint.

```python
from moss_partner_sdk.models import SessionResponse
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `session_token` | `str` | Temporary session token (mapped from API's `token` field) |
| `expires_at` | `datetime` | Token expiration timestamp |
| `metadata` | `dict[str, Any] \| None` | Optional session metadata |

**Example:**

```python
session = await moss.customers.create_session(
    customer_id=customer.id,
    purpose="Support dashboard access"
)

print(f"Session token: {session.session_token}")
print(f"Expires at: {session.expires_at}")

# Calculate remaining time
from datetime import datetime, timezone
remaining = session.expires_at - datetime.now(timezone.utc)
print(f"Valid for: {remaining.total_seconds()} seconds")
```

---

## Compliance Report Models

### ComplianceReportResponse

Response from the `compliance_report()` endpoint, containing ML-DSA-44 signature.

```python
from moss_partner_sdk.models import ComplianceReportResponse
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `report_id` | `str` | Unique report identifier |
| `signature` | `str` | ML-DSA-44 signature (hex-encoded, ~3000-5000 chars) |
| `key_id` | `str` | Signing key identifier |
| `generated_at` | `datetime` | Report generation timestamp |
| `download_url` | `str \| None` | URL to download/verify report |
| `data` | `dict[str, Any] \| None` | Report data (for JSON format) |

**Example:**

```python
report = await moss.customers.compliance_report(
    customer_id=customer.id,
    format="pdf"
)

print(f"Report ID: {report.report_id}")
print(f"Signed with key: {report.key_id}")
print(f"Generated: {report.generated_at}")
print(f"Signature length: {len(report.signature)} chars")

# Signature is extracted from PDF trailer (%%MOSS-SIGNATURE-V1 block)
# Can be verified using MOSS public key
```

---

## Webhook Models

### Webhook

A webhook subscription for receiving event notifications.

```python
from moss_partner_sdk.models import Webhook
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Webhook UUID |
| `url` | `str` | Webhook endpoint URL |
| `events` | `list[str]` | Event patterns subscribed to |
| `secret` | `str` | Shared secret for signature verification |
| `active` | `bool` | Whether webhook is active |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `datetime` | Last update timestamp |

**Example:**

```python
webhook = await moss.webhooks.create(
    url="https://partner.com/webhooks/moss",
    events=["customer.*", "agent.anomaly_detected"]
)

print(f"Webhook ID: {webhook.id}")
print(f"Secret: {webhook.secret}")  # Store securely for verification

# Use secret to verify incoming webhooks
from moss_partner_sdk import verify_webhook_signature

is_valid = verify_webhook_signature(
    payload=request.body,
    signature=request.headers["X-Moss-Signature"],
    secret=webhook.secret
)
```

---

### WebhookListResponse

Response from the `webhooks.list()` endpoint.

```python
from moss_partner_sdk.models import WebhookListResponse
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | `list[Webhook]` | List of webhook subscriptions |

**Example:**

```python
response = await moss.webhooks.list()

print(f"Active webhooks: {len(response.data)}")
for webhook in response.data:
    print(f"- {webhook.url} (events: {', '.join(webhook.events)})")
```

---

## Analytics Models

### AnalyticsResponse

Response from the `analytics.get()` endpoint.

```python
from moss_partner_sdk.models import AnalyticsResponse
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `customers` | `AnalyticsCustomers` | Customer metrics |
| `compliance` | `AnalyticsCompliance` | Compliance metrics |
| `billing` | `AnalyticsBilling` | Billing metrics |
| `period` | `str` | Time period for metrics (e.g., "30d") |

**Example:**

```python
analytics = await moss.analytics.get(period="30d")

print(f"Period: {analytics.period}")
print(f"Total customers: {analytics.customers.total}")
print(f"Average compliance: {analytics.compliance.average_score}")
print(f"Current MRR: ${analytics.billing.current_mrr}")
```

---

### AnalyticsCustomers

Customer analytics metrics.

```python
from moss_partner_sdk.models import AnalyticsCustomers
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | `int` | Total number of customers |
| `sandbox` | `int` | Customers in sandbox mode |
| `production` | `int` | Customers in production |
| `suspended` | `int` | Suspended customers |

**Example:**

```python
customers = analytics.customers

print(f"Total: {customers.total}")
print(f"Production: {customers.production} ({customers.production/customers.total*100:.1f}%)")
print(f"Sandbox: {customers.sandbox}")
print(f"Suspended: {customers.suspended}")
```

---

### AnalyticsCompliance

Compliance analytics metrics.

```python
from moss_partner_sdk.models import AnalyticsCompliance
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `average_score` | `float` | Average compliance score across all customers |
| `at_risk_count` | `int` | Number of customers at risk (score < 600) |
| `non_compliant_count` | `int` | Number of non-compliant customers |

**Example:**

```python
compliance = analytics.compliance

print(f"Average score: {compliance.average_score:.1f}")

if compliance.at_risk_count > 0:
    print(f"⚠️  {compliance.at_risk_count} customers at risk")

if compliance.non_compliant_count > 0:
    print(f"🚨 {compliance.non_compliant_count} non-compliant customers")
```

---

### AnalyticsBilling

Billing analytics metrics.

```python
from moss_partner_sdk.models import AnalyticsBilling
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `current_mrr` | `float` | Current monthly recurring revenue |
| `total_customers_billed` | `int` | Number of customers with active billing |

**Example:**

```python
billing = analytics.billing

print(f"Current MRR: ${billing.current_mrr:,.2f}")
print(f"Paying customers: {billing.total_customers_billed}")

# Calculate average revenue per customer
if billing.total_customers_billed > 0:
    arpu = billing.current_mrr / billing.total_customers_billed
    print(f"ARPU: ${arpu:.2f}/month")
```

---

## Working with Models

### Serialization

All models support Pydantic serialization methods:

```python
# To dict
customer_dict = customer.model_dump()

# To JSON string
customer_json = customer.model_dump_json()

# To dict with excluded fields
customer_dict = customer.model_dump(exclude={"sandbox_token", "production_token"})

# To dict with only specific fields
customer_dict = customer.model_dump(include={"id", "name", "status"})
```

### Deserialization

Create models from API responses or dictionaries:

```python
from moss_partner_sdk.models import Customer

# From dict
customer = Customer(**customer_dict)

# From JSON string
customer = Customer.model_validate_json(customer_json)
```

### Type Hints

Use models in type hints for better IDE support:

```python
from moss_partner_sdk.models import Customer, CustomerListResponse

async def get_production_customers(moss: MossClient) -> list[Customer]:
    """Get all production customers with type safety."""
    response: CustomerListResponse = await moss.customers.list(
        status="production_active"
    )
    return response.data
```

### Validation

Models validate data automatically:

```python
from moss_partner_sdk.models import ResourceLimits
from pydantic import ValidationError

try:
    # This will fail - agents is required
    limits = ResourceLimits(envelopes_per_month=10000)
except ValidationError as e:
    print(f"Validation error: {e}")

# Valid
limits = ResourceLimits(
    agents=50,
    envelopes_per_month=10000,
    policies=25
)
```

---

## See Also

- [Customers API Reference](customers.md) - Methods that return these models
- [Webhooks API Reference](webhooks.md) - Webhook models
- [Analytics API Reference](analytics.md) - Analytics models
- [Getting Started Guide](../getting-started.md) - Usage examples
