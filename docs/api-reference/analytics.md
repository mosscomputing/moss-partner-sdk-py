# Analytics API Reference

The `AnalyticsResource` provides methods for accessing partner-level analytics and metrics.

## Overview

The analytics resource is accessed via `moss.analytics` and provides aggregated metrics across all your customers:

- Customer counts by status
- Compliance metrics and risk levels
- Billing and revenue metrics

## Methods

### get()

Get analytics data for a specified time period.

```python
async def get(self, period: str = "30d") -> AnalyticsResponse
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `period` | `str` | No | `"30d"` | Time period for analytics |

#### Valid Period Values

| Value | Description |
|-------|-------------|
| `"7d"` | Last 7 days |
| `"30d"` | Last 30 days (default) |
| `"90d"` | Last 90 days |
| `"1y"` | Last year |
| `"all"` | All time |

#### Returns

`AnalyticsResponse` - Contains customer, compliance, and billing metrics.

#### Exceptions

- `MossAPIError` - If the API returns an error
- `MossNetworkError` - If the network request fails

#### Example: Basic Analytics

```python
from moss_partner_sdk import MossClient

async with MossClient(api_key="your_partner_key") as moss:
    analytics = await moss.analytics.get(period="30d")

    print(f"Period: {analytics.period}")
    print(f"\nCustomer Metrics:")
    print(f"  Total: {analytics.customers.total}")
    print(f"  Production: {analytics.customers.production}")
    print(f"  Sandbox: {analytics.customers.sandbox}")
    print(f"  Suspended: {analytics.customers.suspended}")

    print(f"\nCompliance Metrics:")
    print(f"  Average Score: {analytics.compliance.average_score:.1f}")
    print(f"  At Risk: {analytics.compliance.at_risk_count}")
    print(f"  Non-Compliant: {analytics.compliance.non_compliant_count}")

    print(f"\nBilling Metrics:")
    print(f"  Current MRR: ${analytics.billing.current_mrr:,.2f}")
    print(f"  Paying Customers: {analytics.billing.total_customers_billed}")
```

#### Example: Compare Time Periods

```python
# Get current and previous period
current = await moss.analytics.get(period="30d")
previous = await moss.analytics.get(period="90d")

# Calculate growth metrics
customer_growth = current.customers.production - previous.customers.production
mrr_growth = current.billing.current_mrr - previous.billing.current_mrr

print(f"Customer Growth (30d vs 90d): {customer_growth:+d}")
print(f"MRR Growth: ${mrr_growth:+,.2f}")

# Calculate conversion rate
if current.customers.total > 0:
    conversion_rate = current.customers.production / current.customers.total * 100
    print(f"Sandbox → Production: {conversion_rate:.1f}%")
```

#### Example: Generate Dashboard Metrics

```python
async def get_dashboard_metrics(moss: MossClient) -> dict:
    """Get metrics for partner dashboard."""
    analytics = await moss.analytics.get(period="30d")

    # Customer metrics
    total_customers = analytics.customers.total
    production_rate = (
        analytics.customers.production / total_customers * 100
        if total_customers > 0
        else 0
    )

    # Compliance metrics
    avg_score = analytics.compliance.average_score
    at_risk_percent = (
        analytics.compliance.at_risk_count / total_customers * 100
        if total_customers > 0
        else 0
    )

    # Billing metrics
    mrr = analytics.billing.current_mrr
    arpu = (
        mrr / analytics.billing.total_customers_billed
        if analytics.billing.total_customers_billed > 0
        else 0
    )

    return {
        "customers": {
            "total": total_customers,
            "production": analytics.customers.production,
            "production_rate": production_rate,
            "sandbox": analytics.customers.sandbox,
            "suspended": analytics.customers.suspended,
        },
        "compliance": {
            "average_score": avg_score,
            "at_risk_count": analytics.compliance.at_risk_count,
            "at_risk_percent": at_risk_percent,
            "non_compliant": analytics.compliance.non_compliant_count,
        },
        "billing": {
            "mrr": mrr,
            "paying_customers": analytics.billing.total_customers_billed,
            "arpu": arpu,
        },
    }
```

---

## Response Structure

### AnalyticsResponse

Top-level analytics response.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `customers` | `AnalyticsCustomers` | Customer metrics |
| `compliance` | `AnalyticsCompliance` | Compliance metrics |
| `billing` | `AnalyticsBilling` | Billing metrics |
| `period` | `str` | Time period (e.g., "30d") |

### AnalyticsCustomers

Customer metrics broken down by status.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | `int` | Total number of customers |
| `sandbox` | `int` | Customers in sandbox mode |
| `production` | `int` | Customers in production |
| `suspended` | `int` | Suspended customers |

### AnalyticsCompliance

Compliance metrics across all customers.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `average_score` | `float` | Average compliance score (0-1000) |
| `at_risk_count` | `int` | Customers with score < 600 |
| `non_compliant_count` | `int` | Customers with critical issues |

### AnalyticsBilling

Billing and revenue metrics.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `current_mrr` | `float` | Current monthly recurring revenue |
| `total_customers_billed` | `int` | Number of paying customers |

---

## Use Cases

### Partner Dashboard

```python
from moss_partner_sdk import MossClient

async def build_partner_dashboard(moss: MossClient):
    """Build metrics for partner admin dashboard."""
    analytics = await moss.analytics.get(period="30d")

    dashboard = {
        "summary": {
            "total_customers": analytics.customers.total,
            "active_customers": (
                analytics.customers.sandbox + analytics.customers.production
            ),
            "monthly_revenue": analytics.billing.current_mrr,
        },
        "customer_breakdown": {
            "production": analytics.customers.production,
            "sandbox": analytics.customers.sandbox,
            "suspended": analytics.customers.suspended,
        },
        "health": {
            "avg_compliance_score": analytics.compliance.average_score,
            "customers_at_risk": analytics.compliance.at_risk_count,
            "customers_non_compliant": analytics.compliance.non_compliant_count,
        },
        "revenue": {
            "mrr": analytics.billing.current_mrr,
            "paying_customers": analytics.billing.total_customers_billed,
            "arpu": (
                analytics.billing.current_mrr / analytics.billing.total_customers_billed
                if analytics.billing.total_customers_billed > 0
                else 0
            ),
        },
    }

    return dashboard
```

### Automated Alerting

```python
async def check_analytics_alerts(moss: MossClient):
    """Check analytics for alert conditions."""
    analytics = await moss.analytics.get(period="30d")

    alerts = []

    # Alert: Low compliance score
    if analytics.compliance.average_score < 700:
        alerts.append({
            "severity": "warning",
            "message": f"Average compliance score is low: {analytics.compliance.average_score:.1f}",
            "action": "Review customer compliance status"
        })

    # Alert: High at-risk count
    if analytics.compliance.at_risk_count > 0:
        at_risk_percent = (
            analytics.compliance.at_risk_count / analytics.customers.total * 100
        )
        if at_risk_percent > 20:
            alerts.append({
                "severity": "high",
                "message": f"{analytics.compliance.at_risk_count} customers at risk ({at_risk_percent:.1f}%)",
                "action": "Contact at-risk customers proactively"
            })

    # Alert: High suspension rate
    if analytics.customers.suspended > 0:
        suspension_rate = (
            analytics.customers.suspended / analytics.customers.total * 100
        )
        if suspension_rate > 10:
            alerts.append({
                "severity": "high",
                "message": f"High suspension rate: {suspension_rate:.1f}%",
                "action": "Review suspension reasons"
            })

    # Alert: Low conversion rate
    if analytics.customers.total > 10:
        conversion_rate = (
            analytics.customers.production / analytics.customers.total * 100
        )
        if conversion_rate < 30:
            alerts.append({
                "severity": "info",
                "message": f"Low conversion rate: {conversion_rate:.1f}%",
                "action": "Review onboarding process"
            })

    return alerts
```

### Revenue Forecasting

```python
from datetime import datetime, timedelta

async def forecast_revenue(moss: MossClient):
    """Forecast revenue based on current trends."""
    # Get different time periods
    current_month = await moss.analytics.get(period="30d")
    last_quarter = await moss.analytics.get(period="90d")

    # Current metrics
    current_mrr = current_month.billing.current_mrr
    current_customers = current_month.billing.total_customers_billed

    # Calculate growth rate (simplified)
    # In reality, you'd want to track historical data
    growth_rate = 0.15  # 15% monthly growth estimate

    # Forecast next 12 months
    forecast = []
    for month in range(1, 13):
        projected_mrr = current_mrr * ((1 + growth_rate) ** month)
        projected_customers = int(current_customers * ((1 + growth_rate) ** month))

        forecast.append({
            "month": (datetime.now() + timedelta(days=30 * month)).strftime("%Y-%m"),
            "mrr": projected_mrr,
            "customers": projected_customers,
        })

    return {
        "current_mrr": current_mrr,
        "growth_rate": growth_rate,
        "forecast": forecast,
    }
```

### Compliance Risk Report

```python
async def generate_compliance_risk_report(moss: MossClient):
    """Generate compliance risk analysis."""
    analytics = await moss.analytics.get(period="30d")

    # Calculate risk levels
    total_customers = analytics.customers.total
    avg_score = analytics.compliance.average_score

    # Risk classification
    if avg_score >= 800:
        risk_level = "low"
        risk_description = "Strong compliance posture"
    elif avg_score >= 700:
        risk_level = "medium"
        risk_description = "Acceptable compliance with room for improvement"
    elif avg_score >= 600:
        risk_level = "elevated"
        risk_description = "Some compliance concerns"
    else:
        risk_level = "high"
        risk_description = "Significant compliance issues"

    # Calculate percentages
    at_risk_percent = (
        analytics.compliance.at_risk_count / total_customers * 100
        if total_customers > 0
        else 0
    )
    non_compliant_percent = (
        analytics.compliance.non_compliant_count / total_customers * 100
        if total_customers > 0
        else 0
    )

    report = {
        "period": analytics.period,
        "overall_risk_level": risk_level,
        "risk_description": risk_description,
        "metrics": {
            "average_score": avg_score,
            "total_customers": total_customers,
            "at_risk_count": analytics.compliance.at_risk_count,
            "at_risk_percent": at_risk_percent,
            "non_compliant_count": analytics.compliance.non_compliant_count,
            "non_compliant_percent": non_compliant_percent,
        },
        "recommendations": _generate_recommendations(analytics),
    }

    return report

def _generate_recommendations(analytics: AnalyticsResponse) -> list[str]:
    """Generate compliance recommendations."""
    recommendations = []

    if analytics.compliance.at_risk_count > 0:
        recommendations.append(
            f"Contact {analytics.compliance.at_risk_count} at-risk customers "
            "to improve their compliance posture"
        )

    if analytics.compliance.non_compliant_count > 0:
        recommendations.append(
            f"Urgent: Address {analytics.compliance.non_compliant_count} "
            "non-compliant customers immediately"
        )

    if analytics.compliance.average_score < 750:
        recommendations.append(
            "Consider implementing proactive compliance monitoring and alerts"
        )

    if analytics.customers.suspended > analytics.customers.total * 0.05:
        recommendations.append(
            "Review suspension reasons to identify systemic issues"
        )

    return recommendations
```

### Customer Segmentation

```python
async def segment_customers(moss: MossClient):
    """Segment customers based on analytics."""
    analytics = await moss.analytics.get(period="30d")

    # Calculate rates
    total = analytics.customers.total
    production_rate = analytics.customers.production / total if total > 0 else 0
    suspension_rate = analytics.customers.suspended / total if total > 0 else 0

    segments = {
        "champions": {
            "count": analytics.customers.production,
            "description": "Production customers - your success stories",
            "actions": [
                "Request case studies",
                "Encourage referrals",
                "Upsell opportunities"
            ]
        },
        "trial_users": {
            "count": analytics.customers.sandbox,
            "description": "Sandbox customers - conversion opportunities",
            "actions": [
                "Send onboarding emails",
                "Offer promotion assistance",
                "Provide success resources"
            ]
        },
        "at_risk": {
            "count": analytics.compliance.at_risk_count,
            "description": "Low compliance - risk of churn",
            "actions": [
                "Proactive support outreach",
                "Compliance improvement guide",
                "Account review calls"
            ]
        },
        "suspended": {
            "count": analytics.customers.suspended,
            "description": "Suspended accounts - reactivation targets",
            "actions": [
                "Identify suspension reasons",
                "Win-back campaigns",
                "Resolution assistance"
            ]
        },
    }

    return segments
```

### Weekly Summary Report

```python
from datetime import datetime

async def generate_weekly_summary(moss: MossClient):
    """Generate weekly summary email."""
    analytics = await moss.analytics.get(period="7d")

    # Calculate key metrics
    total = analytics.customers.total
    mrr = analytics.billing.current_mrr
    avg_score = analytics.compliance.average_score

    summary = f"""
    Weekly Partner Summary - {datetime.now().strftime('%Y-%m-%d')}

    📊 CUSTOMER METRICS
    - Total Customers: {total}
    - Production: {analytics.customers.production} ({analytics.customers.production/total*100:.1f}%)
    - Sandbox: {analytics.customers.sandbox}
    - Suspended: {analytics.customers.suspended}

    ✅ COMPLIANCE HEALTH
    - Average Score: {avg_score:.1f}/1000
    - At Risk: {analytics.compliance.at_risk_count}
    - Non-Compliant: {analytics.compliance.non_compliant_count}

    💰 REVENUE
    - Current MRR: ${mrr:,.2f}
    - Paying Customers: {analytics.billing.total_customers_billed}
    - ARPU: ${mrr/analytics.billing.total_customers_billed:.2f}

    🎯 ACTION ITEMS
    """

    # Add action items based on metrics
    if analytics.compliance.at_risk_count > 0:
        summary += f"\n- ⚠️  Review {analytics.compliance.at_risk_count} at-risk customers"

    if analytics.customers.sandbox > analytics.customers.production:
        summary += f"\n- 🚀 Focus on converting {analytics.customers.sandbox} sandbox customers"

    if analytics.customers.suspended > 0:
        summary += f"\n- 🔄 Reactivate {analytics.customers.suspended} suspended accounts"

    return summary
```

---

## Caching and Performance

### Cache Analytics Data

```python
from datetime import datetime, timedelta
import asyncio

class AnalyticsCache:
    """Cache analytics data to reduce API calls."""

    def __init__(self, ttl_seconds: int = 300):
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache = {}
        self.last_fetch = {}

    async def get(self, moss: MossClient, period: str) -> AnalyticsResponse:
        """Get analytics with caching."""
        cache_key = f"analytics:{period}"

        # Check cache
        if cache_key in self.cache:
            last_fetch = self.last_fetch.get(cache_key)
            if last_fetch and datetime.now() - last_fetch < self.ttl:
                return self.cache[cache_key]

        # Fetch fresh data
        analytics = await moss.analytics.get(period=period)

        # Update cache
        self.cache[cache_key] = analytics
        self.last_fetch[cache_key] = datetime.now()

        return analytics

# Usage
cache = AnalyticsCache(ttl_seconds=300)  # 5-minute cache

async def get_dashboard_data(moss: MossClient):
    """Get dashboard data with caching."""
    analytics = await cache.get(moss, period="30d")
    return analytics
```

---

## See Also

- [Models Reference](models.md) - Analytics model details
- [Customers API Reference](customers.md) - Customer management affecting these metrics
- [Exceptions Reference](exceptions.md) - Error handling
- [Getting Started Guide](../getting-started.md) - Usage examples
