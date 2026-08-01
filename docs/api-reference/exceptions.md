# Exceptions API Reference

Exception classes for error handling in the MOSS Partner SDK.

## Overview

The SDK defines a hierarchy of exceptions for different error scenarios. All exceptions inherit from `MossError`, making it easy to catch all SDK-related errors.

```python
from moss_partner_sdk.exceptions import (
    MossError,
    MossAPIError,
    MossNetworkError,
    MossValidationError,
    MossParseError,
)
```

## Exception Hierarchy

```
MossError (base)
├── MossAPIError (API returned error response)
├── MossNetworkError (network/connection failure)
├── MossValidationError (input validation failure)
└── MossParseError (response parsing failure)
```

---

## MossError

Base exception for all MOSS SDK errors.

```python
class MossError(Exception)
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Error message |

**Usage:**

Catch this to handle any SDK error:

```python
from moss_partner_sdk import MossClient
from moss_partner_sdk.exceptions import MossError

async with MossClient(api_key="your_key") as moss:
    try:
        customer = await moss.customers.get("invalid_id")
    except MossError as e:
        print(f"SDK error: {e.message}")
```

---

## MossAPIError

Exception raised when the API returns an error response (e.g., 400, 404, 500).

```python
class MossAPIError(MossError)
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Error message from API |
| `status_code` | `int` | HTTP status code (e.g., 404, 500) |
| `code` | `str` | Error code from API (e.g., "customer_not_found") |
| `response_body` | `str \| None` | Raw response body (for debugging) |

**Common Status Codes:**

| Code | Description | Example |
|------|-------------|---------|
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Customer/resource not found |
| 409 | Conflict | Duplicate external_id |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary outage |

**String Representation:**

```python
str(error)  # "API Error 404 (customer_not_found): Customer not found"
```

### Example: Handle Specific Status Codes

```python
from moss_partner_sdk.exceptions import MossAPIError

try:
    customer = await moss.customers.get(customer_id)
except MossAPIError as e:
    if e.status_code == 404:
        print(f"Customer not found: {customer_id}")
    elif e.status_code == 401:
        print("Invalid API key - check your credentials")
    elif e.status_code == 429:
        print("Rate limit exceeded - retry after backoff")
    else:
        print(f"API error {e.status_code}: {e.message}")
```

### Example: Handle Specific Error Codes

```python
try:
    customer = await moss.customers.create(
        external_id="duplicate_id",
        name="Test Customer"
    )
except MossAPIError as e:
    if e.code == "duplicate_external_id":
        print("Customer with this external_id already exists")
        # Fetch existing customer instead
        existing = await moss.customers.list()
        # ... find by external_id ...
    elif e.code == "invalid_email":
        print("Invalid email format")
    else:
        print(f"Creation failed: {e.message}")
```

### Example: Log Full Error Details

```python
import logging

try:
    customer = await moss.customers.promote(
        customer_id=customer_id,
        attestation={},
        billing={}
    )
except MossAPIError as e:
    logging.error(
        f"API error: {e.message}",
        extra={
            "status_code": e.status_code,
            "error_code": e.code,
            "response_body": e.response_body,
            "customer_id": customer_id
        }
    )
```

---

## MossNetworkError

Exception raised when a network request fails (connection error, timeout, DNS failure).

```python
class MossNetworkError(MossError)
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Error message describing the network failure |

**Common Causes:**

- No internet connection
- DNS resolution failure
- Connection timeout
- SSL/TLS handshake failure
- Firewall blocking request

### Example: Handle Network Errors with Retry

```python
from moss_partner_sdk.exceptions import MossNetworkError
import asyncio

async def get_customer_with_retry(moss, customer_id, max_retries=3):
    """Get customer with exponential backoff retry on network errors."""
    for attempt in range(max_retries):
        try:
            return await moss.customers.get(customer_id)
        except MossNetworkError as e:
            if attempt == max_retries - 1:
                raise  # Last attempt failed

            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            print(f"Network error: {e.message}. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
```

### Example: Graceful Degradation

```python
from moss_partner_sdk.exceptions import MossNetworkError

try:
    analytics = await moss.analytics.get(period="30d")
except MossNetworkError as e:
    print(f"Network error: {e.message}")
    # Use cached data or default values
    analytics = load_cached_analytics()
```

---

## MossValidationError

Exception raised when input validation fails before making an API request.

```python
class MossValidationError(MossError)
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Validation error message |

**Common Validation Failures:**

- Missing required fields
- Invalid field types
- Field value out of range
- Invalid format (e.g., email, URL)

### Example: Handle Validation Errors

```python
from moss_partner_sdk.exceptions import MossValidationError

def validate_external_id(external_id: str) -> str:
    """Validate external_id before creating customer."""
    if not external_id:
        raise MossValidationError("external_id cannot be empty")

    if len(external_id) > 255:
        raise MossValidationError("external_id too long (max 255 chars)")

    # Check for invalid characters
    if not external_id.replace("_", "").replace("-", "").isalnum():
        raise MossValidationError("external_id can only contain letters, numbers, _, -")

    return external_id

try:
    external_id = validate_external_id(user_input)
    customer = await moss.customers.create(
        external_id=external_id,
        name="Customer Name"
    )
except MossValidationError as e:
    print(f"Invalid input: {e.message}")
```

---

## MossParseError

Exception raised when response parsing fails (e.g., invalid JSON, malformed PDF signature).

```python
class MossParseError(MossError)
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Parsing error message |

**Common Causes:**

- Malformed JSON response
- Invalid PDF signature trailer
- Unexpected response format
- Encoding errors

### Example: Handle Parse Errors in Compliance Reports

```python
from moss_partner_sdk.exceptions import MossParseError

try:
    report = await moss.customers.compliance_report(
        customer_id=customer_id,
        format="pdf"
    )
    print(f"Report signed with key: {report.key_id}")
except MossParseError as e:
    print(f"Failed to parse PDF signature: {e.message}")

    # Try JSON format instead
    try:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="json"
        )
    except MossParseError as e2:
        print(f"JSON parsing also failed: {e2.message}")
```

### Example: Debug Parse Errors

```python
from moss_partner_sdk.exceptions import MossParseError
import logging

try:
    report = await moss.customers.compliance_report(
        customer_id=customer_id,
        format="pdf"
    )
except MossParseError as e:
    logging.error(
        f"PDF parse error: {e.message}",
        extra={
            "customer_id": customer_id,
            "format": "pdf"
        }
    )

    # Could indicate:
    # - PDF does not contain MOSS signature trailer
    # - Invalid JSON in trailer
    # - Malformed signature format
```

---

## Error Handling Patterns

### Comprehensive Error Handling

```python
from moss_partner_sdk import MossClient
from moss_partner_sdk.exceptions import (
    MossAPIError,
    MossNetworkError,
    MossValidationError,
    MossParseError,
    MossError,
)

async def safe_get_customer(moss: MossClient, customer_id: str):
    """Get customer with comprehensive error handling."""
    try:
        return await moss.customers.get(customer_id)

    except MossAPIError as e:
        if e.status_code == 404:
            print(f"Customer {customer_id} not found")
            return None
        elif e.status_code == 401:
            print("Authentication failed - check API key")
            raise
        elif e.status_code >= 500:
            print(f"Server error: {e.message}")
            # Could retry after delay
            raise
        else:
            print(f"API error {e.status_code}: {e.message}")
            raise

    except MossNetworkError as e:
        print(f"Network error: {e.message}")
        print("Check internet connection and try again")
        return None

    except MossParseError as e:
        print(f"Response parsing failed: {e.message}")
        print("This may indicate a server issue")
        raise

    except MossValidationError as e:
        print(f"Invalid input: {e.message}")
        raise

    except MossError as e:
        # Catch any other SDK errors
        print(f"SDK error: {e.message}")
        raise
```

### Retry with Exponential Backoff

```python
import asyncio
from moss_partner_sdk.exceptions import MossNetworkError, MossAPIError

async def retry_with_backoff(func, max_retries=3, initial_delay=1):
    """Retry function with exponential backoff on transient errors."""
    for attempt in range(max_retries):
        try:
            return await func()

        except MossNetworkError as e:
            # Always retry network errors
            should_retry = True
            error_msg = f"Network error: {e.message}"

        except MossAPIError as e:
            # Retry on 5xx server errors and 429 rate limits
            should_retry = e.status_code >= 500 or e.status_code == 429
            error_msg = f"API error {e.status_code}: {e.message}"

        except Exception as e:
            # Don't retry other exceptions
            raise

        if not should_retry or attempt == max_retries - 1:
            raise

        delay = initial_delay * (2 ** attempt)
        print(f"{error_msg}. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
        await asyncio.sleep(delay)

# Usage
customer = await retry_with_backoff(
    lambda: moss.customers.get(customer_id)
)
```

### Context Manager for Error Logging

```python
from contextlib import asynccontextmanager
from moss_partner_sdk.exceptions import MossError
import logging

@asynccontextmanager
async def moss_error_context(operation: str):
    """Context manager for logging MOSS operations."""
    try:
        logging.info(f"Starting: {operation}")
        yield
        logging.info(f"Success: {operation}")

    except MossError as e:
        logging.error(
            f"Failed: {operation}",
            extra={
                "error_type": type(e).__name__,
                "error_message": e.message,
            }
        )
        raise

# Usage
async with moss_error_context("create customer"):
    customer = await moss.customers.create(
        external_id="acme_123",
        name="Acme Corp"
    )
```

### Validation Before API Calls

```python
from moss_partner_sdk.exceptions import MossValidationError

def validate_customer_create(external_id: str, name: str, email: str | None):
    """Validate inputs before creating customer."""
    errors = []

    if not external_id or not external_id.strip():
        errors.append("external_id is required")
    elif len(external_id) > 255:
        errors.append("external_id too long (max 255 characters)")

    if not name or not name.strip():
        errors.append("name is required")
    elif len(name) > 255:
        errors.append("name too long (max 255 characters)")

    if email:
        if "@" not in email or "." not in email:
            errors.append("invalid email format")
        elif len(email) > 255:
            errors.append("email too long (max 255 characters)")

    if errors:
        raise MossValidationError("; ".join(errors))

# Usage
try:
    validate_customer_create(
        external_id=user_input["external_id"],
        name=user_input["name"],
        email=user_input.get("email")
    )

    customer = await moss.customers.create(
        external_id=user_input["external_id"],
        name=user_input["name"],
        email=user_input.get("email")
    )
except MossValidationError as e:
    return {"error": e.message}, 400
```

### Circuit Breaker Pattern

```python
from datetime import datetime, timedelta
from moss_partner_sdk.exceptions import MossNetworkError, MossAPIError

class CircuitBreaker:
    """Circuit breaker for MOSS API calls."""

    def __init__(self, failure_threshold=5, timeout_seconds=60):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def is_open(self):
        """Check if circuit is open."""
        if self.state == "open":
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = "half_open"
                return False
            return True
        return False

    def record_success(self):
        """Record successful call."""
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        """Record failed call."""
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = "open"

    async def call(self, func):
        """Execute function with circuit breaker."""
        if self.is_open():
            raise MossNetworkError("Circuit breaker is open - too many failures")

        try:
            result = await func()
            self.record_success()
            return result

        except (MossNetworkError, MossAPIError) as e:
            self.record_failure()
            raise

# Usage
breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

try:
    customer = await breaker.call(
        lambda: moss.customers.get(customer_id)
    )
except MossNetworkError as e:
    if "Circuit breaker is open" in e.message:
        print("Service temporarily unavailable - circuit breaker triggered")
    else:
        print(f"Network error: {e.message}")
```

---

## See Also

- [Customers API Reference](customers.md) - Methods that may raise these exceptions
- [Webhooks API Reference](webhooks.md) - Webhook-specific errors
- [Analytics API Reference](analytics.md) - Analytics-specific errors
- [Getting Started Guide](../getting-started.md) - Error handling examples
