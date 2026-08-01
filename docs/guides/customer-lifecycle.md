# Customer Lifecycle Management

Complete guide to managing customers from creation through production promotion, suspension, and reactivation.

## Overview

The customer lifecycle in MOSS Partner follows a clear progression:

```
Creation → Sandbox Testing → KYC/Attestation → Production → [Suspension/Reactivation]
```

Each stage has specific requirements and produces different credentials and capabilities.

## Customer Lifecycle States

### Status Progression

| Status | Description | Token Available | Billing Active |
|--------|-------------|-----------------|----------------|
| `pending` | Just created, awaiting activation | Sandbox | No |
| `sandbox_active` | Active sandbox environment | Sandbox | No |
| `production_active` | Promoted to production | Production | Yes |
| `suspended` | Temporarily suspended | None | Paused |
| `deactivated` | Permanently deactivated | None | No |

## Stage 1: Customer Creation

Create a new customer in sandbox mode for testing and integration development.

### Basic Creation

```python
import asyncio
from moss_partner_sdk import MossPartner

async def create_customer():
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.create(
            external_id="acme_corp_123",
            name="Acme Corporation",
            email="admin@acmecorp.com",
        )

        print(f"Customer ID: {customer.id}")
        print(f"Status: {customer.status}")  # sandbox_active
        print(f"Sandbox Token: {customer.sandbox_token}")

        return customer

if __name__ == "__main__":
    asyncio.run(create_customer())
```

### Creation with Governance Configuration

```python
async def create_customer_with_governance():
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.create(
            external_id="eu_analytics_456",
            name="European Analytics Ltd",
            email="compliance@euanalytics.com",
            governance={
                "jurisdictions": ["EU", "UK"],
                "frameworks": [
                    "eu_ai_act",
                    "gdpr",
                    "nist_ai_rmf",
                    "iso_42001"
                ],
                "settings": {
                    "data_residency": "eu-west-1",
                    "retention_days": 365,
                    "require_human_review": True
                }
            }
        )

        print(f"Customer created with {len(customer.governance.frameworks)} frameworks")
        print(f"Jurisdictions: {', '.join(customer.governance.jurisdictions)}")

        return customer
```

### Best Practices for Creation

1. **Unique External IDs**: Use your internal customer ID to ensure idempotency
2. **Email Validation**: Validate email format before creating
3. **Framework Selection**: Choose frameworks based on customer's jurisdiction
4. **Error Handling**: Handle duplicate external_id errors gracefully

```python
from moss_partner_sdk.exceptions import MossAPIError

async def safe_create_customer(external_id: str, name: str):
    """Create customer with duplicate handling."""
    async with MossPartner(api_key="prt_xxx") as moss:
        try:
            customer = await moss.customers.create(
                external_id=external_id,
                name=name
            )
            print(f"Created new customer: {customer.id}")
            return customer

        except MossAPIError as e:
            if e.code == "duplicate_external_id":
                # Customer already exists, fetch instead
                print(f"Customer with external_id={external_id} already exists")

                # Find existing customer
                result = await moss.customers.list()
                for c in result.data:
                    if c.external_id == external_id:
                        print(f"Found existing customer: {c.id}")
                        return c

            raise  # Re-raise other errors
```

## Stage 2: Sandbox Testing Phase

After creation, customers use their sandbox token to test the MOSS integration.

### Sandbox Environment Characteristics

- **No billing**: Free testing environment
- **Limited resources**: Default limits (10 agents, 1000 envelopes/month)
- **Full features**: All MOSS features available for testing
- **Production-like**: Behavior matches production environment

### Monitoring Sandbox Usage

```python
async def monitor_sandbox_customer(customer_id: str):
    """Monitor sandbox customer progress."""
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.get(customer_id)

        print(f"Status: {customer.status}")
        print(f"Agent Limit: {customer.limits.agents}")
        print(f"Envelope Limit: {customer.limits.envelopes_per_month}")
        print(f"Compliance Score: {customer.compliance.score}")

        # Check if ready for production
        if customer.compliance.score >= 700:
            print("✓ Customer ready for production promotion")
        else:
            print(f"✗ Compliance score too low ({customer.compliance.score})")
            print(f"  Issues found: {len(customer.compliance.issues)}")

            for issue in customer.compliance.issues:
                print(f"  - {issue.severity}: {issue.description}")
```

### Updating Sandbox Limits

You can adjust resource limits during the sandbox phase:

```python
async def increase_sandbox_limits(customer_id: str):
    """Increase limits for large sandbox testing."""
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.update(
            customer_id,
            limits={
                "agents": 50,  # Increase from 10 to 50
                "envelopes_per_month": 10000,  # Increase from 1000
                "policies": 25
            }
        )

        print(f"Updated limits for {customer.name}")
        print(f"New agent limit: {customer.limits.agents}")
```

## Stage 3: KYC and Attestation

Before promoting to production, partners must complete KYC (Know Your Customer) verification.

### Attestation Requirements

The attestation object documents that you've verified the customer:

```python
attestation = {
    "kyc_completed": True,           # Required
    "verified_by": "partner_system",  # Required: Who verified
    "verification_date": "2026-07-31T10:00:00Z",  # Required: When verified
    "risk_level": "low",              # Required: low, medium, high

    # Optional but recommended
    "documents_verified": [
        "business_license",
        "tax_id",
        "proof_of_address"
    ],
    "verification_method": "automated_kyc",
    "verification_id": "kyc_abc123",
    "compliance_notes": "All documents verified, low-risk profile"
}
```

### KYC Verification Workflow

```python
async def verify_customer_for_promotion(
    customer_id: str,
    business_license: str,
    tax_id: str
) -> dict:
    """
    Complete KYC verification before promotion.

    Returns attestation data for promotion.
    """
    from datetime import datetime, timezone

    # 1. Verify business documents
    kyc_verified = await verify_business_documents(
        business_license=business_license,
        tax_id=tax_id
    )

    if not kyc_verified:
        raise ValueError("KYC verification failed")

    # 2. Assess risk level
    risk_level = await assess_customer_risk(customer_id)

    # 3. Build attestation
    attestation = {
        "kyc_completed": True,
        "verified_by": "partner_kyc_system",
        "verification_date": datetime.now(timezone.utc).isoformat(),
        "risk_level": risk_level,
        "documents_verified": ["business_license", "tax_id"],
        "verification_method": "automated",
    }

    return attestation


async def verify_business_documents(
    business_license: str,
    tax_id: str
) -> bool:
    """Verify business documents (implement your KYC logic)."""
    # Your KYC verification logic here
    # Could integrate with services like Stripe Identity, Persona, etc.
    return True


async def assess_customer_risk(customer_id: str) -> str:
    """Assess customer risk level."""
    # Your risk assessment logic here
    # Could consider: jurisdiction, industry, volume, compliance score
    return "low"
```

## Stage 4: Production Promotion

Promote a customer from sandbox to production after KYC completion.

### Complete Promotion Workflow

```python
async def promote_customer_to_production(customer_id: str):
    """Full promotion workflow with all validations."""
    async with MossPartner(api_key="prt_xxx") as moss:
        from datetime import datetime, timezone

        # 1. Fetch current customer
        customer = await moss.customers.get(customer_id)

        # 2. Validate eligibility
        if customer.status != "sandbox_active":
            raise ValueError(f"Cannot promote {customer.status} customer")

        if customer.compliance.score < 600:
            raise ValueError(
                f"Compliance score too low: {customer.compliance.score}"
            )

        # 3. Complete KYC (your process)
        attestation = {
            "kyc_completed": True,
            "verified_by": "partner_system",
            "verification_date": datetime.now(timezone.utc).isoformat(),
            "risk_level": "low",
            "documents_verified": ["business_license", "tax_id"]
        }

        # 4. Configure billing
        billing = {
            "tier": "professional",  # Your tier name
            "billing_email": customer.email,
            # Optional: Link to Stripe customer
            # "stripe_customer_id": "cus_xxx"
        }

        # 5. Promote to production
        promoted = await moss.customers.promote(
            customer_id=customer_id,
            attestation=attestation,
            billing=billing
        )

        # 6. Store production token securely
        print(f"✓ Customer promoted to production")
        print(f"Production Token: {promoted.production_token}")
        print(f"Promoted At: {promoted.promoted_at}")
        print(f"Billing Tier: {promoted.billing.tier}")

        # 7. Notify customer
        await notify_customer_promotion(
            customer_email=customer.email,
            production_token=promoted.production_token
        )

        return promoted


async def notify_customer_promotion(
    customer_email: str,
    production_token: str
):
    """Send production credentials to customer."""
    # Your email notification logic
    print(f"Sending production credentials to {customer_email}")
```

### Billing Configuration

The billing object configures how the customer is billed:

```python
# Basic billing configuration
billing = {
    "tier": "professional",
    "billing_email": "billing@customer.com"
}

# With Stripe integration
billing = {
    "tier": "enterprise",
    "billing_email": "billing@customer.com",
    "stripe_customer_id": "cus_abc123"  # Pre-created Stripe customer
}

# With custom pricing
billing = {
    "tier": "custom_plan_tier",
    "billing_email": "billing@customer.com",
    "billing_metadata": {
        "contract_id": "contract_2026_q3_001",
        "annual_value": 50000,
        "payment_terms": "net_30"
    }
}
```

## Stage 5: Production Operations

After promotion, customers operate in production with full capabilities.

### Updating Production Customers

```python
async def update_production_customer(customer_id: str):
    """Update limits and governance for production customer."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Update resource limits based on usage
        customer = await moss.customers.update(
            customer_id,
            limits={
                "agents": 200,
                "envelopes_per_month": 100000,
                "policies": 100
            },
            governance={
                "jurisdictions": ["EU", "US", "UK"],
                "frameworks": [
                    "eu_ai_act",
                    "nist_ai_rmf",
                    "iso_42001",
                    "soc2"
                ]
            }
        )

        print(f"Updated {customer.name} to {customer.limits.agents} agents")
```

### Monitoring Production Health

```python
async def check_production_health(customer_id: str):
    """Monitor production customer health."""
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.get(customer_id)

        health = {
            "status": "healthy",
            "warnings": [],
            "actions_needed": []
        }

        # Check compliance score
        if customer.compliance.score < 700:
            health["status"] = "warning"
            health["warnings"].append(
                f"Low compliance score: {customer.compliance.score}"
            )
            health["actions_needed"].append("Review compliance issues")

        # Check for critical issues
        critical_issues = [
            i for i in customer.compliance.issues
            if i.severity == "critical"
        ]
        if critical_issues:
            health["status"] = "critical"
            health["warnings"].append(
                f"{len(critical_issues)} critical compliance issues"
            )
            health["actions_needed"].append("Resolve critical issues immediately")

        return health
```

## Stage 6: Suspension and Reactivation

Temporarily suspend customers for policy violations, payment issues, or compliance problems.

### Suspension Workflow

```python
async def suspend_customer_for_payment(customer_id: str, invoice_id: str):
    """Suspend customer due to payment failure."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Suspend with 48-hour grace period
        customer = await moss.customers.suspend(
            customer_id=customer_id,
            reason=f"Payment failure - invoice {invoice_id} overdue",
            grace_period_hours=48
        )

        print(f"Customer suspended at: {customer.suspended_at}")
        print("48-hour grace period before full suspension")

        # Notify customer
        await notify_suspension(
            customer_email=customer.email,
            reason="payment_overdue",
            grace_period_hours=48,
            invoice_id=invoice_id
        )

        return customer


async def suspend_customer_for_compliance(customer_id: str):
    """Immediate suspension for compliance violation."""
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.get(customer_id)

        # Check for critical violations
        critical = [
            i for i in customer.compliance.issues
            if i.severity == "critical"
        ]

        if critical:
            # Immediate suspension (no grace period)
            customer = await moss.customers.suspend(
                customer_id=customer_id,
                reason=f"Critical compliance violations: {len(critical)} issues"
            )

            print("⚠️  Customer suspended immediately for compliance")
            return customer


async def notify_suspension(
    customer_email: str,
    reason: str,
    grace_period_hours: int,
    invoice_id: str | None = None
):
    """Notify customer of suspension."""
    # Your notification logic
    print(f"Notifying {customer_email} of suspension")
```

### Reactivation Workflow

```python
async def reactivate_customer_after_payment(
    customer_id: str,
    payment_id: str
):
    """Reactivate customer after payment received."""
    async with MossPartner(api_key="prt_xxx") as moss:
        from datetime import datetime, timezone

        customer = await moss.customers.reactivate(
            customer_id=customer_id,
            resolution={
                "resolved_by": "billing_system",
                "resolution_date": datetime.now(timezone.utc).isoformat(),
                "notes": f"Payment received - {payment_id}",
                "payment_id": payment_id
            }
        )

        print(f"✓ Customer reactivated: {customer.name}")
        print(f"Status: {customer.status}")  # production_active

        # Notify customer
        await notify_reactivation(customer.email)

        return customer


async def reactivate_customer_after_compliance_fix(
    customer_id: str,
    resolution_notes: str
):
    """Reactivate after compliance issues resolved."""
    async with MossPartner(api_key="prt_xxx") as moss:
        from datetime import datetime, timezone

        # Verify compliance is now acceptable
        customer = await moss.customers.get(customer_id)
        if customer.compliance.score < 600:
            raise ValueError("Compliance score still too low for reactivation")

        customer = await moss.customers.reactivate(
            customer_id=customer_id,
            resolution={
                "resolved_by": "compliance_team",
                "resolution_date": datetime.now(timezone.utc).isoformat(),
                "notes": resolution_notes,
                "compliance_score": customer.compliance.score
            }
        )

        return customer


async def notify_reactivation(customer_email: str):
    """Notify customer of reactivation."""
    # Your notification logic
    print(f"Notifying {customer_email} of reactivation")
```

## Complete Lifecycle Example

Here's a complete example showing the full customer lifecycle:

```python
import asyncio
from datetime import datetime, timezone
from moss_partner_sdk import MossPartner
from moss_partner_sdk.exceptions import MossAPIError


async def full_customer_lifecycle():
    """Demonstrate complete customer lifecycle."""
    async with MossPartner(api_key="prt_xxx") as moss:

        # 1. Create customer in sandbox
        print("1. Creating customer in sandbox...")
        customer = await moss.customers.create(
            external_id="demo_customer_001",
            name="Demo Corporation",
            email="admin@democorp.com",
            governance={
                "jurisdictions": ["US"],
                "frameworks": ["nist_ai_rmf"]
            }
        )
        print(f"   ✓ Created: {customer.id}")
        print(f"   Sandbox Token: {customer.sandbox_token}")

        # 2. Monitor sandbox testing
        print("\n2. Monitoring sandbox testing...")
        print(f"   Status: {customer.status}")
        print(f"   Compliance: {customer.compliance.score}/1000")

        # 3. Complete KYC
        print("\n3. Completing KYC verification...")
        attestation = {
            "kyc_completed": True,
            "verified_by": "partner_kyc",
            "verification_date": datetime.now(timezone.utc).isoformat(),
            "risk_level": "low"
        }
        print("   ✓ KYC completed")

        # 4. Promote to production
        print("\n4. Promoting to production...")
        customer = await moss.customers.promote(
            customer_id=customer.id,
            attestation=attestation,
            billing={
                "tier": "professional",
                "billing_email": "billing@democorp.com"
            }
        )
        print(f"   ✓ Promoted at: {customer.promoted_at}")
        print(f"   Production Token: {customer.production_token}")

        # 5. Update production limits
        print("\n5. Updating production limits...")
        customer = await moss.customers.update(
            customer.id,
            limits={"agents": 100, "envelopes_per_month": 50000}
        )
        print(f"   ✓ Increased to {customer.limits.agents} agents")

        # 6. Simulate suspension (payment issue)
        print("\n6. Suspending for payment issue...")
        customer = await moss.customers.suspend(
            customer.id,
            reason="Payment overdue - invoice INV001",
            grace_period_hours=48
        )
        print(f"   ⚠️  Suspended at: {customer.suspended_at}")

        # 7. Reactivate after payment
        print("\n7. Reactivating after payment...")
        customer = await moss.customers.reactivate(
            customer.id,
            resolution={
                "resolved_by": "billing_system",
                "resolution_date": datetime.now(timezone.utc).isoformat(),
                "notes": "Payment received"
            }
        )
        print(f"   ✓ Reactivated: {customer.status}")

        print("\n✅ Complete lifecycle demonstrated successfully")


if __name__ == "__main__":
    asyncio.run(full_customer_lifecycle())
```

## Best Practices

### 1. Status Checking Before Operations

```python
async def safe_promote(customer_id: str):
    """Promote with status validation."""
    async with MossPartner(api_key="prt_xxx") as moss:
        customer = await moss.customers.get(customer_id)

        # Validate status
        if customer.status != "sandbox_active":
            raise ValueError(
                f"Cannot promote {customer.status} customer. "
                "Only sandbox_active customers can be promoted."
            )

        # Continue with promotion...
```

### 2. Compliance Monitoring

```python
async def auto_check_compliance():
    """Automatically check compliance for all production customers."""
    async with MossPartner(api_key="prt_xxx") as moss:
        result = await moss.customers.list(status="production_active")

        at_risk = []
        for customer in result.data:
            if customer.compliance.score < 700:
                at_risk.append(customer)

                # Alert your team
                await send_alert(
                    f"Customer {customer.name} compliance low: "
                    f"{customer.compliance.score}"
                )

        return at_risk
```

### 3. Idempotent Operations

```python
async def idempotent_create(external_id: str, name: str):
    """Create customer idempotently using external_id."""
    async with MossPartner(api_key="prt_xxx") as moss:
        try:
            return await moss.customers.create(
                external_id=external_id,
                name=name
            )
        except MossAPIError as e:
            if e.code == "duplicate_external_id":
                # Find and return existing
                result = await moss.customers.list()
                for c in result.data:
                    if c.external_id == external_id:
                        return c
            raise
```

## See Also

- [Session Tokens Guide](session-tokens.md) - Temporary dashboard access
- [Compliance Reports Guide](compliance-reports.md) - Generating signed reports
- [Error Handling Guide](error-handling.md) - Handling lifecycle errors
- [Customers API Reference](../api-reference/customers.md) - Full API details
