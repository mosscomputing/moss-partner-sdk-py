# Webhooks API Reference

The `WebhooksResource` provides methods for managing webhook subscriptions and verifying webhook signatures.

## Overview

Webhooks allow you to receive real-time notifications when events occur in your customers' MOSS accounts. The webhooks resource is accessed via `moss.webhooks` and provides:

- Creating webhook subscriptions
- Listing active webhooks
- Deleting webhooks
- Signature verification for security

## Methods

### create()

Create a new webhook subscription.

```python
async def create(self, url: str, events: list[str]) -> Webhook
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | `str` | Yes | Webhook endpoint URL (must be HTTPS in production) |
| `events` | `list[str]` | Yes | Event patterns to subscribe to |

#### Event Patterns

Event patterns support wildcards (`*`) for subscribing to multiple related events:

| Pattern | Description | Example Events |
|---------|-------------|----------------|
| `customer.*` | All customer events | `customer.created`, `customer.promoted`, `customer.suspended` |
| `customer.created` | Specific event only | `customer.created` |
| `agent.*` | All agent events | `agent.registered`, `agent.anomaly_detected`, `agent.deactivated` |
| `agent.anomaly_detected` | Anomaly detections only | `agent.anomaly_detected` |
| `compliance.*` | All compliance events | `compliance.score_updated`, `compliance.issue_detected` |
| `billing.*` | All billing events | `billing.invoice_created`, `billing.payment_failed` |
| `*` | All events (not recommended) | All events from all customers |

#### Common Event Types

**Customer Events:**
- `customer.created` - New customer created
- `customer.promoted` - Customer promoted to production
- `customer.suspended` - Customer suspended
- `customer.reactivated` - Customer reactivated
- `customer.updated` - Customer configuration updated

**Agent Events:**
- `agent.registered` - New agent registered
- `agent.anomaly_detected` - Anomalous behavior detected
- `agent.policy_violation` - Policy violation occurred
- `agent.deactivated` - Agent deactivated

**Compliance Events:**
- `compliance.score_updated` - Compliance score changed
- `compliance.issue_detected` - New compliance issue found
- `compliance.report_generated` - Compliance report generated

**Billing Events:**
- `billing.invoice_created` - New invoice created
- `billing.payment_succeeded` - Payment successful
- `billing.payment_failed` - Payment failed
- `billing.subscription_updated` - Subscription changed

#### Returns

`Webhook` - The created webhook with a secret for signature verification.

#### Exceptions

- `MossAPIError` - If webhook creation fails (e.g., invalid URL)
- `MossNetworkError` - If the network request fails
- `MossValidationError` - If input validation fails

#### Example: Subscribe to Customer Events

```python
from moss_partner_sdk import MossClient

async with MossClient(api_key="your_partner_key") as moss:
    webhook = await moss.webhooks.create(
        url="https://partner.com/webhooks/moss",
        events=["customer.*"]  # All customer events
    )

    print(f"Webhook created: {webhook.id}")
    print(f"Secret: {webhook.secret}")  # Store securely!
```

#### Example: Subscribe to Multiple Event Types

```python
webhook = await moss.webhooks.create(
    url="https://partner.com/webhooks/moss",
    events=[
        "customer.created",
        "customer.promoted",
        "customer.suspended",
        "agent.anomaly_detected",
        "compliance.score_updated"
    ]
)

# Store webhook secret for signature verification
await store_webhook_secret(webhook.id, webhook.secret)
```

#### Example: Development vs Production URLs

```python
import os

webhook_url = (
    "https://partner.com/webhooks/moss"
    if os.getenv("ENV") == "production"
    else "https://dev.partner.com/webhooks/moss"
)

webhook = await moss.webhooks.create(
    url=webhook_url,
    events=["customer.*", "agent.anomaly_detected"]
)
```

---

### list()

List all webhook subscriptions.

```python
async def list(self) -> WebhookListResponse
```

#### Parameters

None

#### Returns

`WebhookListResponse` - Contains a list of all webhook subscriptions.

#### Exceptions

- `MossAPIError` - If the API returns an error
- `MossNetworkError` - If the network request fails

#### Example: List Active Webhooks

```python
response = await moss.webhooks.list()

print(f"Active webhooks: {len(response.data)}")
for webhook in response.data:
    print(f"- {webhook.url}")
    print(f"  Events: {', '.join(webhook.events)}")
    print(f"  Active: {webhook.active}")
    print(f"  Created: {webhook.created_at}")
```

#### Example: Find Webhook by URL

```python
response = await moss.webhooks.list()

target_url = "https://partner.com/webhooks/moss"
webhook = next(
    (w for w in response.data if w.url == target_url),
    None
)

if webhook:
    print(f"Found webhook: {webhook.id}")
else:
    print(f"No webhook found for {target_url}")
```

---

### delete()

Delete a webhook subscription.

```python
async def delete(self, webhook_id: str) -> None
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `webhook_id` | `str` | Yes | Webhook UUID |

#### Returns

`None`

#### Exceptions

- `MossAPIError` - If webhook not found (404) or deletion fails
- `MossNetworkError` - If the network request fails

#### Example: Delete Webhook

```python
await moss.webhooks.delete("550e8400-e29b-41d4-a716-446655440000")
print("Webhook deleted successfully")
```

#### Example: Delete All Webhooks

```python
response = await moss.webhooks.list()

for webhook in response.data:
    await moss.webhooks.delete(webhook.id)
    print(f"Deleted webhook: {webhook.url}")

print(f"Deleted {len(response.data)} webhooks")
```

#### Example: Delete Inactive Webhooks

```python
response = await moss.webhooks.list()

for webhook in response.data:
    if not webhook.active:
        await moss.webhooks.delete(webhook.id)
        print(f"Deleted inactive webhook: {webhook.url}")
```

---

## Functions

### verify_webhook_signature()

Verify the signature of an incoming webhook request.

```python
def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `payload` | `bytes` | Yes | Raw webhook request body (bytes) |
| `signature` | `str` | Yes | Value from `X-Moss-Signature` header |
| `secret` | `str` | Yes | Webhook secret from `webhook.secret` |

#### Returns

`bool` - `True` if signature is valid, `False` otherwise.

#### Security Notes

- Always verify signatures before processing webhook payloads
- Use constant-time comparison (built into `hmac.compare_digest()`)
- Reject requests with invalid signatures (return 401)
- Use raw request body bytes, not parsed JSON
- Store webhook secrets securely (environment variables, secrets manager)

#### Example: FastAPI Webhook Endpoint

```python
from fastapi import FastAPI, Request, HTTPException, Header
from moss_partner_sdk import verify_webhook_signature

app = FastAPI()

WEBHOOK_SECRET = "your_webhook_secret_from_creation"

@app.post("/webhooks/moss")
async def handle_moss_webhook(
    request: Request,
    x_moss_signature: str = Header(...)
):
    # Get raw body
    body = await request.body()

    # Verify signature
    is_valid = verify_webhook_signature(
        payload=body,
        signature=x_moss_signature,
        secret=WEBHOOK_SECRET
    )

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    payload = await request.json()

    # Process event
    event_type = payload.get("event")
    data = payload.get("data")

    if event_type == "customer.created":
        await handle_customer_created(data)
    elif event_type == "customer.promoted":
        await handle_customer_promoted(data)
    elif event_type == "agent.anomaly_detected":
        await handle_anomaly_detected(data)

    return {"status": "success"}
```

#### Example: Flask Webhook Endpoint

```python
from flask import Flask, request, jsonify
from moss_partner_sdk import verify_webhook_signature

app = Flask(__name__)

WEBHOOK_SECRET = "your_webhook_secret_from_creation"

@app.route("/webhooks/moss", methods=["POST"])
def handle_moss_webhook():
    # Get signature from header
    signature = request.headers.get("X-Moss-Signature")
    if not signature:
        return jsonify({"error": "Missing signature"}), 401

    # Get raw body
    body = request.get_data()

    # Verify signature
    is_valid = verify_webhook_signature(
        payload=body,
        signature=signature,
        secret=WEBHOOK_SECRET
    )

    if not is_valid:
        return jsonify({"error": "Invalid signature"}), 401

    # Parse payload
    payload = request.get_json()

    # Process event
    event_type = payload.get("event")
    data = payload.get("data")

    # Handle event
    print(f"Received event: {event_type}")

    return jsonify({"status": "success"})
```

#### Example: Django Webhook Endpoint

```python
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from moss_partner_sdk import verify_webhook_signature
import json

WEBHOOK_SECRET = "your_webhook_secret_from_creation"

@csrf_exempt
@require_http_methods(["POST"])
def moss_webhook(request):
    # Get signature from header
    signature = request.headers.get("X-Moss-Signature")
    if not signature:
        return JsonResponse({"error": "Missing signature"}, status=401)

    # Get raw body
    body = request.body

    # Verify signature
    is_valid = verify_webhook_signature(
        payload=body,
        signature=signature,
        secret=WEBHOOK_SECRET
    )

    if not is_valid:
        return JsonResponse({"error": "Invalid signature"}, status=401)

    # Parse payload
    payload = json.loads(body)

    # Process event
    event_type = payload.get("event")
    data = payload.get("data")

    # Handle event asynchronously
    process_webhook_event.delay(event_type, data)  # Celery task

    return JsonResponse({"status": "success"})
```

---

## Webhook Payload Format

All webhooks send POST requests with the following format:

```json
{
  "event": "customer.created",
  "timestamp": "2026-07-31T12:00:00Z",
  "data": {
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "external_id": "acme_123",
    "name": "Acme Corp",
    "status": "sandbox_active"
  },
  "partner_id": "your_partner_id"
}
```

### Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `event` | `str` | Event type (e.g., "customer.created") |
| `timestamp` | `str` | ISO 8601 timestamp of when event occurred |
| `data` | `object` | Event-specific data |
| `partner_id` | `str` | Your partner ID |

---

## Common Patterns

### Complete Webhook Setup

```python
from moss_partner_sdk import MossClient

async def setup_webhooks(moss: MossClient):
    """Set up webhook subscriptions for production."""

    # Create webhook
    webhook = await moss.webhooks.create(
        url="https://partner.com/webhooks/moss",
        events=[
            "customer.created",
            "customer.promoted",
            "customer.suspended",
            "agent.anomaly_detected",
            "compliance.score_updated",
            "billing.payment_failed"
        ]
    )

    # Store secret securely
    await store_secret(f"moss_webhook_{webhook.id}", webhook.secret)

    print(f"Webhook created: {webhook.id}")
    return webhook
```

### Webhook Event Router

```python
from typing import Callable, Dict
import logging

class WebhookRouter:
    """Route webhook events to handlers."""

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}

    def register(self, event_type: str, handler: Callable):
        """Register event handler."""
        self.handlers[event_type] = handler

    async def route(self, event_type: str, data: dict):
        """Route event to registered handler."""
        handler = self.handlers.get(event_type)

        if handler:
            try:
                await handler(data)
            except Exception as e:
                logging.error(f"Handler failed for {event_type}: {e}")
                raise
        else:
            logging.warning(f"No handler registered for {event_type}")

# Setup router
router = WebhookRouter()

# Register handlers
router.register("customer.created", handle_customer_created)
router.register("customer.promoted", handle_customer_promoted)
router.register("agent.anomaly_detected", handle_anomaly)

# Use in webhook endpoint
@app.post("/webhooks/moss")
async def webhook_endpoint(request: Request):
    # Verify signature...
    payload = await request.json()

    await router.route(
        event_type=payload["event"],
        data=payload["data"]
    )

    return {"status": "success"}
```

### Retry Failed Webhooks

```python
import asyncio
from datetime import datetime, timedelta

class WebhookProcessor:
    """Process webhooks with retry logic."""

    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    async def process(self, event_type: str, data: dict):
        """Process webhook with retries."""
        for attempt in range(self.max_retries):
            try:
                await self._handle_event(event_type, data)
                return  # Success

            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Last attempt failed - log and alert
                    await self._log_failure(event_type, data, e)
                    raise

                # Exponential backoff
                delay = 2 ** attempt
                await asyncio.sleep(delay)

    async def _handle_event(self, event_type: str, data: dict):
        """Handle single event."""
        if event_type == "customer.created":
            await self._handle_customer_created(data)
        elif event_type == "agent.anomaly_detected":
            await self._handle_anomaly(data)
        # ... other handlers ...

    async def _log_failure(self, event_type: str, data: dict, error: Exception):
        """Log webhook processing failure."""
        logging.error(
            f"Webhook processing failed after {self.max_retries} attempts",
            extra={
                "event_type": event_type,
                "data": data,
                "error": str(error)
            }
        )
```

### Idempotent Webhook Processing

```python
import redis

class IdempotentWebhookProcessor:
    """Process webhooks idempotently using Redis."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def process(self, webhook_id: str, event_type: str, data: dict):
        """Process webhook only once."""
        key = f"webhook:processed:{webhook_id}"

        # Check if already processed
        if self.redis.exists(key):
            print(f"Webhook {webhook_id} already processed, skipping")
            return

        # Process event
        await self._handle_event(event_type, data)

        # Mark as processed (expire after 7 days)
        self.redis.setex(key, timedelta(days=7), "1")
```

### Webhook Health Monitoring

```python
from datetime import datetime, timedelta
from collections import defaultdict

class WebhookMonitor:
    """Monitor webhook health and delivery."""

    def __init__(self):
        self.stats = defaultdict(lambda: {"success": 0, "failure": 0})
        self.last_received = {}

    def record_success(self, event_type: str):
        """Record successful webhook processing."""
        self.stats[event_type]["success"] += 1
        self.last_received[event_type] = datetime.now()

    def record_failure(self, event_type: str):
        """Record failed webhook processing."""
        self.stats[event_type]["failure"] += 1

    def get_health_report(self):
        """Generate health report."""
        report = []

        for event_type, counts in self.stats.items():
            total = counts["success"] + counts["failure"]
            success_rate = counts["success"] / total if total > 0 else 0

            last_received = self.last_received.get(event_type)
            if last_received:
                time_since = datetime.now() - last_received
            else:
                time_since = None

            report.append({
                "event_type": event_type,
                "total": total,
                "success_rate": success_rate,
                "last_received": last_received,
                "time_since_last": time_since
            })

        return report

# Usage
monitor = WebhookMonitor()

@app.post("/webhooks/moss")
async def webhook_endpoint(request: Request):
    payload = await request.json()
    event_type = payload["event"]

    try:
        await process_webhook(payload)
        monitor.record_success(event_type)
    except Exception as e:
        monitor.record_failure(event_type)
        raise

    return {"status": "success"}
```

---

## See Also

- [Models Reference](models.md) - Webhook model details
- [Exceptions Reference](exceptions.md) - Error handling
- [Getting Started Guide](../getting-started.md) - Webhook setup examples
- [Customers API Reference](customers.md) - Customer events that trigger webhooks
