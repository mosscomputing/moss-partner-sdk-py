# Production Examples

Production-ready patterns, deployment strategies, and best practices for running the MOSS Partner SDK in production environments.

## Environment Configuration

### Secure Secret Management

Never hardcode API keys - use environment variables or secrets managers:

```python
import os
from moss_partner_sdk import MossPartner

# ✓ GOOD: Load from environment
API_KEY = os.getenv("MOSS_PARTNER_API_KEY")

if not API_KEY:
    raise ValueError("MOSS_PARTNER_API_KEY environment variable is required")

async with MossPartner(api_key=API_KEY) as moss:
    customer = await moss.customers.get("customer-uuid")


# ✗ BAD: Hardcoded API key
# async with MossPartner(api_key="prt_hardcoded_key") as moss:
#     ...
```

### AWS Secrets Manager

Load secrets from AWS Secrets Manager:

```python
import boto3
import json
from moss_partner_sdk import MossPartner

def get_moss_api_key() -> str:
    """Load MOSS API key from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name="us-east-1")

    response = client.get_secret_value(SecretId="moss/partner/api-key")
    secret = json.loads(response["SecretString"])

    return secret["api_key"]


# Usage
async def get_moss_client():
    """Get MOSS client with secret from AWS."""
    api_key = get_moss_api_key()

    return MossPartner(api_key=api_key)
```

### Google Cloud Secret Manager

Load secrets from Google Cloud:

```python
from google.cloud import secretmanager
from moss_partner_sdk import MossPartner

def get_moss_api_key_gcp() -> str:
    """Load MOSS API key from Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()

    name = "projects/PROJECT_ID/secrets/moss-partner-api-key/versions/latest"
    response = client.access_secret_version(request={"name": name})

    return response.payload.data.decode("UTF-8")


async with MossPartner(api_key=get_moss_api_key_gcp()) as moss:
    customer = await moss.customers.get("customer-uuid")
```

## Logging and Monitoring

### Structured Logging with JSON

Production-grade structured logging:

```python
import logging
import json
from datetime import datetime
from moss_partner_sdk import MossPartner
from moss_partner_sdk.exceptions import MossError

# Configure JSON logging
class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "customer_id"):
            log_data["customer_id"] = record.customer_id

        if hasattr(record, "operation"):
            log_data["operation"] = record.operation

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


# Setup logging
logger = logging.getLogger("moss_partner")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Usage
async def logged_operation(customer_id: str):
    """Operation with structured logging."""
    logger.info(
        "Starting customer fetch",
        extra={
            "customer_id": customer_id,
            "operation": "get_customer"
        }
    )

    async with MossPartner(api_key=os.getenv("MOSS_PARTNER_API_KEY")) as moss:
        try:
            customer = await moss.customers.get(customer_id)

            logger.info(
                "Customer fetch successful",
                extra={
                    "customer_id": customer_id,
                    "customer_name": customer.name,
                    "status": customer.status
                }
            )

            return customer

        except MossError as e:
            logger.error(
                "Customer fetch failed",
                extra={
                    "customer_id": customer_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                },
                exc_info=True
            )
            raise
```

### Sentry Integration

Error tracking with Sentry:

```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from moss_partner_sdk import MossPartner
from moss_partner_sdk.exceptions import MossError

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENV", "production"),
    traces_sample_rate=0.1,
    integrations=[
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
    ]
)


async def operation_with_sentry(customer_id: str):
    """Operation with Sentry error tracking."""
    with sentry_sdk.configure_scope() as scope:
        # Add context
        scope.set_context("moss_operation", {
            "customer_id": customer_id,
            "operation": "get_customer",
            "sdk_version": "1.0.0"
        })

        # Set user context
        scope.set_user({"id": customer_id})

        # Set tags
        scope.set_tag("component", "moss_partner_sdk")

        try:
            async with MossPartner(api_key=os.getenv("MOSS_PARTNER_API_KEY")) as moss:
                customer = await moss.customers.get(customer_id)
                return customer

        except MossError as e:
            # Capture exception with context
            sentry_sdk.capture_exception(e)
            raise
```

### Health Checks

Implement health check endpoint:

```python
from fastapi import FastAPI, Response
from moss_partner_sdk import MossPartner
import os

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health = {
        "status": "healthy",
        "checks": {
            "moss_api": "unknown"
        }
    }

    # Check MOSS API connectivity
    try:
        async with MossPartner(api_key=os.getenv("MOSS_PARTNER_API_KEY")) as moss:
            is_reachable = await moss.ping()

            if is_reachable:
                health["checks"]["moss_api"] = "healthy"
            else:
                health["checks"]["moss_api"] = "unhealthy"
                health["status"] = "degraded"

    except Exception as e:
        health["checks"]["moss_api"] = f"unhealthy: {str(e)}"
        health["status"] = "unhealthy"

    # Return appropriate status code
    status_code = 200 if health["status"] == "healthy" else 503

    return Response(
        content=json.dumps(health),
        media_type="application/json",
        status_code=status_code
    )
```

## Rate Limiting

### Client-Side Rate Limiting

Implement rate limiting to avoid API limits:

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate: int, per: float):
        """
        Initialize rate limiter.

        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.updated_at = datetime.now()

    async def acquire(self):
        """Acquire token, waiting if necessary."""
        while self.tokens < 1:
            # Calculate tokens to add
            now = datetime.now()
            elapsed = (now - self.updated_at).total_seconds()
            tokens_to_add = elapsed * (self.rate / self.per)

            self.tokens = min(self.rate, self.tokens + tokens_to_add)
            self.updated_at = now

            if self.tokens < 1:
                # Wait a bit before trying again
                await asyncio.sleep(0.1)

        # Consume token
        self.tokens -= 1


# Usage
rate_limiter = RateLimiter(rate=100, per=60)  # 100 requests per minute

async def rate_limited_request(moss, customer_id: str):
    """Make rate-limited request."""
    await rate_limiter.acquire()
    return await moss.customers.get(customer_id)
```

## Connection Pooling

### Singleton Pattern for Client

Reuse MOSS client across application:

```python
from typing import Optional

class MOSSClientManager:
    """Singleton manager for MOSS client."""

    _instance: Optional[MossPartner] = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_client(cls) -> MossPartner:
        """Get or create MOSS client."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = MossPartner(
                        api_key=os.getenv("MOSS_PARTNER_API_KEY"),
                        timeout=30.0
                    )

        return cls._instance

    @classmethod
    async def close(cls):
        """Close MOSS client."""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


# Usage in FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup():
    """Initialize MOSS client on startup."""
    await MOSSClientManager.get_client()

@app.on_event("shutdown")
async def shutdown():
    """Close MOSS client on shutdown."""
    await MOSSClientManager.close()

@app.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer endpoint."""
    moss = await MOSSClientManager.get_client()
    customer = await moss.customers.get(customer_id)
    return customer
```

## Docker Deployment

### Dockerfile

Production-ready Dockerfile:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from moss_partner_sdk import MossPartner; import os; asyncio.run(MossPartner(api_key=os.getenv('MOSS_PARTNER_API_KEY')).ping())"

# Run application
CMD ["python", "app.py"]
```

### docker-compose.yml

Complete docker-compose setup:

```yaml
version: '3.8'

services:
  app:
    build: .
    environment:
      - MOSS_PARTNER_API_KEY=${MOSS_PARTNER_API_KEY}
      - ENV=production
      - LOG_LEVEL=INFO
      - SENTRY_DSN=${SENTRY_DSN}
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Kubernetes Deployment

### Deployment YAML

Kubernetes deployment configuration:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: moss-partner-app
  labels:
    app: moss-partner
spec:
  replicas: 3
  selector:
    matchLabels:
      app: moss-partner
  template:
    metadata:
      labels:
        app: moss-partner
    spec:
      containers:
      - name: app
        image: your-registry/moss-partner-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: MOSS_PARTNER_API_KEY
          valueFrom:
            secretKeyRef:
              name: moss-secrets
              key: api-key
        - name: ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: moss-partner-service
spec:
  selector:
    app: moss-partner
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: moss-secrets
type: Opaque
data:
  api-key: <base64-encoded-api-key>
```

## Error Tracking and Alerting

### CloudWatch Metrics

Send custom metrics to AWS CloudWatch:

```python
import boto3
from datetime import datetime
from moss_partner_sdk.exceptions import MossError

cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")

def send_metric(metric_name: str, value: float, unit: str = "Count"):
    """Send metric to CloudWatch."""
    cloudwatch.put_metric_data(
        Namespace="MOSSPartner",
        MetricData=[
            {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.utcnow()
            }
        ]
    )


async def monitored_operation(moss, customer_id: str):
    """Operation with CloudWatch metrics."""
    start_time = datetime.now()

    try:
        customer = await moss.customers.get(customer_id)

        # Record success
        send_metric("CustomerFetchSuccess", 1)

        # Record latency
        latency = (datetime.now() - start_time).total_seconds()
        send_metric("CustomerFetchLatency", latency, "Seconds")

        return customer

    except MossError as e:
        # Record failure
        send_metric("CustomerFetchError", 1)
        send_metric(f"CustomerFetchError_{type(e).__name__}", 1)
        raise
```

### Prometheus Metrics

Export metrics for Prometheus:

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import FastAPI, Response

app = FastAPI()

# Define metrics
requests_total = Counter(
    "moss_requests_total",
    "Total MOSS API requests",
    ["operation", "status"]
)

request_duration = Histogram(
    "moss_request_duration_seconds",
    "MOSS API request duration",
    ["operation"]
)


async def monitored_get_customer(moss, customer_id: str):
    """Get customer with Prometheus metrics."""
    with request_duration.labels(operation="get_customer").time():
        try:
            customer = await moss.customers.get(customer_id)
            requests_total.labels(operation="get_customer", status="success").inc()
            return customer

        except Exception as e:
            requests_total.labels(operation="get_customer", status="error").inc()
            raise


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

## Backup and Disaster Recovery

### Regular Data Exports

Export customer data for backup:

```python
import json
from datetime import datetime

async def backup_customers(moss):
    """Export all customer data for backup."""
    all_customers = []
    offset = 0
    limit = 100

    while True:
        result = await moss.customers.list(limit=limit, offset=offset)
        all_customers.extend(result.data)

        if not result.pagination.has_more:
            break

        offset += limit

    # Convert to JSON
    backup_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_customers": len(all_customers),
        "customers": [c.model_dump() for c in all_customers]
    }

    # Save to file
    filename = f"moss_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(backup_data, f, indent=2, default=str)

    print(f"Backed up {len(all_customers)} customers to {filename}")

    return filename
```

## Performance Optimization

### Query Optimization

Optimize data fetching patterns:

```python
async def get_customer_dashboard_data(moss, customer_id: str):
    """Fetch all needed data in parallel."""
    # Fetch multiple data points concurrently
    customer_task = moss.customers.get(customer_id)
    analytics_task = moss.analytics.get(period="30d")

    # Wait for all requests
    customer, analytics = await asyncio.gather(
        customer_task,
        analytics_task
    )

    return {
        "customer": customer,
        "analytics": analytics
    }
```

### Response Caching

Cache responses for frequently accessed data:

```python
from functools import lru_cache
import hashlib

class ResponseCache:
    """Cache for API responses."""

    def __init__(self):
        self.cache = {}

    def cache_key(self, operation: str, **kwargs) -> str:
        """Generate cache key."""
        key_data = f"{operation}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get_or_fetch(self, key: str, fetch_func, ttl: int = 300):
        """Get from cache or fetch."""
        if key in self.cache:
            cached_value, cached_at = self.cache[key]
            if (datetime.now() - cached_at).total_seconds() < ttl:
                return cached_value

        # Fetch fresh data
        value = await fetch_func()
        self.cache[key] = (value, datetime.now())

        return value


cache = ResponseCache()

async def get_customer_cached(moss, customer_id: str):
    """Get customer with caching."""
    key = cache.cache_key("get_customer", customer_id=customer_id)

    return await cache.get_or_fetch(
        key,
        lambda: moss.customers.get(customer_id),
        ttl=300  # 5 minutes
    )
```

## See Also

- [Basic Usage Examples](basic-usage.md) - Getting started patterns
- [Advanced Examples](advanced.md) - Advanced techniques
- [Error Handling Guide](../guides/error-handling.md) - Production error handling
- [API Reference](../api-reference/) - Full API documentation
