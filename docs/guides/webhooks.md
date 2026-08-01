# Webhooks Guide

Set up real-time event notifications from MOSS to your application using webhooks with HMAC-SHA256 signature verification.

## Overview

Webhooks enable your application to receive real-time notifications when events occur in your customers' MOSS accounts.

**Key Features:**
- Event pattern matching with wildcards
- HMAC-SHA256 signature verification
- Automatic retries from MOSS
- Idempotency support

## Quick Start

### 1. Create Webhook Endpoint

```python
from fastapi import FastAPI, Request, HTTPException, Header
from moss_partner_sdk import verify_webhook_signature
import os

app = FastAPI()

WEBHOOK_SECRET = os.getenv("MOSS_WEBHOOK_SECRET")

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

    print(f"Received event: {event_type}")

    return {"status": "success"}
```

### 2. Register Webhook with MOSS

```python
import asyncio
from moss_partner_sdk import MossPartner

async def register_webhook():
    async with MossPartner(api_key="prt_xxx") as moss:
        webhook = await moss.webhooks.create(
            url="https://partner.com/webhooks/moss",
            events=["customer.*", "agent.anomaly_detected"]
        )

        print(f"Webhook ID: {webhook.id}")
        print(f"Secret: {webhook.secret}")  # Store securely!

        # Save secret to environment
        # os.environ["MOSS_WEBHOOK_SECRET"] = webhook.secret

        return webhook

if __name__ == "__main__":
    asyncio.run(register_webhook())
```

## Event Patterns

### Wildcard Patterns

Use wildcards to subscribe to multiple related events:

```python
events = [
    "customer.*",            # All customer events
    "agent.*",               # All agent events
    "compliance.*",          # All compliance events
    "billing.*",             # All billing events
]
```

### Specific Events

Subscribe to specific events only:

```python
events = [
    "customer.created",
    "customer.promoted",
    "customer.suspended",
    "agent.anomaly_detected",
    "compliance.score_updated",
    "billing.payment_failed"
]
```

### Combined Patterns

Mix wildcards and specific events:

```python
events = [
    "customer.*",             # All customer events
    "agent.anomaly_detected", # Only anomaly detections
    "billing.payment_failed"  # Only failed payments
]
```

## Signature Verification

### HMAC-SHA256 Verification

MOSS signs all webhook requests using HMAC-SHA256:

```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify HMAC-SHA256 signature from X-Moss-Signature header.

    Args:
        payload: Raw request body (bytes)
        signature: X-Moss-Signature header value
        secret: Webhook secret from creation

    Returns:
        True if valid, False otherwise
    """
    expected = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

### Security Best Practices

1. **Always verify signatures** before processing
2. **Use raw body bytes** not parsed JSON
3. **Use constant-time comparison** (hmac.compare_digest)
4. **Reject invalid signatures** with 401 status
5. **Store secrets securely** (environment variables, secrets manager)

## Framework Examples

### FastAPI

Complete webhook handler with routing:

```python
from fastapi import FastAPI, Request, HTTPException, Header
from moss_partner_sdk import verify_webhook_signature
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

WEBHOOK_SECRET = "your_webhook_secret"

@app.post("/webhooks/moss")
async def moss_webhook_handler(
    request: Request,
    x_moss_signature: str = Header(...)
):
    # Verify signature
    body = await request.body()
    is_valid = verify_webhook_signature(
        payload=body,
        signature=x_moss_signature,
        secret=WEBHOOK_SECRET
    )

    if not is_valid:
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse event
    payload = await request.json()
    event_type = payload.get("event")
    data = payload.get("data")

    # Route to handler
    try:
        await route_event(event_type, data)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Event processing failed: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")


async def route_event(event_type: str, data: dict):
    """Route events to specific handlers."""
    handlers = {
        "customer.created": handle_customer_created,
        "customer.promoted": handle_customer_promoted,
        "customer.suspended": handle_customer_suspended,
        "agent.anomaly_detected": handle_anomaly_detected,
        "compliance.score_updated": handle_compliance_updated,
        "billing.payment_failed": handle_payment_failed,
    }

    handler = handlers.get(event_type)
    if handler:
        await handler(data)
    else:
        logger.warning(f"No handler for event: {event_type}")


async def handle_customer_created(data: dict):
    """Handle customer.created event."""
    customer_id = data.get("customer_id")
    logger.info(f"New customer created: {customer_id}")
    # Your business logic here


async def handle_customer_promoted(data: dict):
    """Handle customer.promoted event."""
    customer_id = data.get("customer_id")
    logger.info(f"Customer promoted: {customer_id}")
    # Your business logic here


async def handle_customer_suspended(data: dict):
    """Handle customer.suspended event."""
    customer_id = data.get("customer_id")
    reason = data.get("reason")
    logger.warning(f"Customer suspended: {customer_id} ({reason})")
    # Your business logic here


async def handle_anomaly_detected(data: dict):
    """Handle agent.anomaly_detected event."""
    agent_id = data.get("agent_id")
    anomaly_type = data.get("anomaly_type")
    logger.warning(f"Anomaly detected: {agent_id} - {anomaly_type}")
    # Your business logic here


async def handle_compliance_updated(data: dict):
    """Handle compliance.score_updated event."""
    customer_id = data.get("customer_id")
    new_score = data.get("new_score")
    logger.info(f"Compliance score updated: {customer_id} -> {new_score}")
    # Your business logic here


async def handle_payment_failed(data: dict):
    """Handle billing.payment_failed event."""
    customer_id = data.get("customer_id")
    invoice_id = data.get("invoice_id")
    logger.error(f"Payment failed: {customer_id} - {invoice_id}")
    # Your business logic here
```

### Flask

Flask webhook handler:

```python
from flask import Flask, request, jsonify
from moss_partner_sdk import verify_webhook_signature
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

WEBHOOK_SECRET = "your_webhook_secret"

@app.route("/webhooks/moss", methods=["POST"])
def moss_webhook():
    # Verify signature
    signature = request.headers.get("X-Moss-Signature")
    if not signature:
        return jsonify({"error": "Missing signature"}), 401

    body = request.get_data()
    is_valid = verify_webhook_signature(
        payload=body,
        signature=signature,
        secret=WEBHOOK_SECRET
    )

    if not is_valid:
        logger.warning("Invalid webhook signature")
        return jsonify({"error": "Invalid signature"}), 401

    # Process event
    payload = request.get_json()
    event_type = payload.get("event")
    data = payload.get("data")

    logger.info(f"Received event: {event_type}")

    # Handle event (async processing recommended)
    process_event.delay(event_type, data)  # Celery task

    return jsonify({"status": "success"})


# Celery task for async processing
from celery import Celery
celery = Celery("tasks", broker="redis://localhost:6379/0")

@celery.task
def process_event(event_type: str, data: dict):
    """Process webhook event asynchronously."""
    logger.info(f"Processing {event_type}")
    # Your business logic here
```

### Django

Django webhook view:

```python
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from moss_partner_sdk import verify_webhook_signature
import json
import logging

logger = logging.getLogger(__name__)

WEBHOOK_SECRET = "your_webhook_secret"

@csrf_exempt
@require_http_methods(["POST"])
def moss_webhook(request):
    # Verify signature
    signature = request.headers.get("X-Moss-Signature")
    if not signature:
        return JsonResponse({"error": "Missing signature"}, status=401)

    body = request.body
    is_valid = verify_webhook_signature(
        payload=body,
        signature=signature,
        secret=WEBHOOK_SECRET
    )

    if not is_valid:
        logger.warning("Invalid webhook signature")
        return JsonResponse({"error": "Invalid signature"}, status=401)

    # Parse payload
    payload = json.loads(body)
    event_type = payload.get("event")
    data = payload.get("data")

    logger.info(f"Received event: {event_type}")

    # Queue for async processing
    from .tasks import process_webhook_event
    process_webhook_event.delay(event_type, data)

    return JsonResponse({"status": "success"})
```

## Retry and Idempotency

### Handling Retries

MOSS will retry failed webhooks. Implement idempotency to handle duplicate deliveries:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/webhooks/moss")
async def moss_webhook_idempotent(
    request: Request,
    x_moss_signature: str = Header(...)
):
    # Verify signature
    body = await request.body()
    is_valid = verify_webhook_signature(body, x_moss_signature, WEBHOOK_SECRET)

    if not is_valid:
        raise HTTPException(status_code=401)

    payload = await request.json()
    event_id = payload.get("event_id")  # Unique event ID

    # Check if already processed
    if redis_client.exists(f"webhook:processed:{event_id}"):
        logger.info(f"Event {event_id} already processed, skipping")
        return {"status": "success", "processed": False}

    # Process event
    await process_event(payload)

    # Mark as processed (expire after 7 days)
    redis_client.setex(
        f"webhook:processed:{event_id}",
        60 * 60 * 24 * 7,  # 7 days
        "1"
    )

    return {"status": "success", "processed": True}
```

### Exponential Backoff (Application-Level)

Handle transient failures with retry logic:

```python
import asyncio

async def process_event_with_retry(event_type: str, data: dict, max_retries: int = 3):
    """Process event with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            await process_event(event_type, data)
            return  # Success

        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, log and alert
                logger.error(f"Event processing failed after {max_retries} attempts: {e}")
                await alert_team(f"Webhook processing failed: {event_type}")
                raise

            # Exponential backoff
            delay = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            await asyncio.sleep(delay)
```

## Testing Webhooks

### Local Testing with ngrok

```bash
# Start ngrok tunnel
ngrok http 8000

# Use ngrok URL for webhook
# https://abc123.ngrok.io/webhooks/moss
```

### Test Event Simulation

```python
import httpx
import hmac
import hashlib
import json

async def send_test_webhook(
    url: str,
    secret: str,
    event_type: str,
    data: dict
):
    """Simulate webhook delivery for testing."""
    payload = {
        "event": event_type,
        "timestamp": "2026-07-31T12:00:00Z",
        "data": data,
        "partner_id": "test_partner"
    }

    body = json.dumps(payload).encode("utf-8")

    # Generate signature
    signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()

    # Send request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Moss-Signature": signature
            }
        )

    print(f"Response: {response.status_code}")
    return response


# Test customer.created event
await send_test_webhook(
    url="http://localhost:8000/webhooks/moss",
    secret="test_secret",
    event_type="customer.created",
    data={
        "customer_id": "test-uuid",
        "external_id": "test_123",
        "name": "Test Customer",
        "status": "sandbox_active"
    }
)
```

## Monitoring and Debugging

### Webhook Health Monitoring

```python
from datetime import datetime, timedelta
from collections import defaultdict

class WebhookMonitor:
    """Monitor webhook delivery and processing."""

    def __init__(self):
        self.stats = defaultdict(lambda: {"success": 0, "failure": 0})
        self.last_received = {}

    def record_success(self, event_type: str):
        """Record successful webhook."""
        self.stats[event_type]["success"] += 1
        self.last_received[event_type] = datetime.now()

    def record_failure(self, event_type: str):
        """Record failed webhook."""
        self.stats[event_type]["failure"] += 1

    def get_health_report(self):
        """Generate health report."""
        report = []

        for event_type, counts in self.stats.items():
            total = counts["success"] + counts["failure"]
            success_rate = counts["success"] / total if total > 0 else 0

            last = self.last_received.get(event_type)
            time_since = (datetime.now() - last) if last else None

            report.append({
                "event_type": event_type,
                "total": total,
                "success_rate": success_rate,
                "last_received": last,
                "time_since_last": time_since
            })

        return report


# Usage in webhook handler
monitor = WebhookMonitor()

@app.post("/webhooks/moss")
async def webhook_with_monitoring(request: Request, x_moss_signature: str = Header(...)):
    # ... signature verification ...

    payload = await request.json()
    event_type = payload.get("event")

    try:
        await process_event(event_type, payload.get("data"))
        monitor.record_success(event_type)
        return {"status": "success"}
    except Exception as e:
        monitor.record_failure(event_type)
        raise
```

### Logging Best Practices

```python
import logging
import json

logger = logging.getLogger(__name__)

@app.post("/webhooks/moss")
async def webhook_with_logging(request: Request, x_moss_signature: str = Header(...)):
    request_id = request.headers.get("X-Request-ID", "unknown")

    # Log incoming request
    logger.info(
        "Webhook received",
        extra={
            "request_id": request_id,
            "signature_present": bool(x_moss_signature)
        }
    )

    # Verify signature
    body = await request.body()
    is_valid = verify_webhook_signature(body, x_moss_signature, WEBHOOK_SECRET)

    if not is_valid:
        logger.warning(
            "Invalid signature",
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=401)

    # Parse and process
    payload = await request.json()
    event_type = payload.get("event")

    logger.info(
        "Processing event",
        extra={
            "request_id": request_id,
            "event_type": event_type,
            "customer_id": payload.get("data", {}).get("customer_id")
        }
    )

    try:
        await process_event(event_type, payload.get("data"))

        logger.info(
            "Event processed successfully",
            extra={
                "request_id": request_id,
                "event_type": event_type
            }
        )

        return {"status": "success"}

    except Exception as e:
        logger.error(
            "Event processing failed",
            extra={
                "request_id": request_id,
                "event_type": event_type,
                "error": str(e)
            },
            exc_info=True
        )
        raise
```

## See Also

- [Customer Lifecycle Guide](customer-lifecycle.md) - Events triggered by lifecycle changes
- [Error Handling Guide](error-handling.md) - Handling webhook errors
- [Webhooks API Reference](../api-reference/webhooks.md) - Full API documentation and patterns
