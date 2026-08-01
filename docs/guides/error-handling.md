# Error Handling Guide

Comprehensive guide to graceful error handling, retry strategies, and production-ready error management patterns for the MOSS Partner SDK.

## Exception Hierarchy

```
MossError (base exception)
├── MossAPIError (HTTP errors from API)
├── MossNetworkError (connection/network failures)
├── MossValidationError (input validation errors)
└── MossParseError (response parsing errors)
```

All SDK exceptions inherit from `MossError`, making it easy to catch all SDK-related errors.

## Import Exceptions

```python
from moss_partner_sdk.exceptions import (
    MossError,          # Base exception
    MossAPIError,       # API errors (4xx, 5xx)
    MossNetworkError,   # Network failures
    MossValidationError,# Invalid input
    MossParseError,     # Parse failures
)
```

## Exception Details

### MossAPIError

Raised when the API returns an error response.

**Attributes:**
- `message`: Error message from API
- `status_code`: HTTP status code (400, 404, 500, etc.)
- `code`: Error code from API (e.g., "customer_not_found")
- `response_body`: Raw response body (for debugging)

**Common Status Codes:**
- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Invalid API key
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `409`: Conflict - Duplicate resource (e.g., external_id)
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error
- `503`: Service Unavailable - Temporary outage

### MossNetworkError

Raised when a network request fails.

**Common Causes:**
- No internet connection
- DNS resolution failure
- Connection timeout
- SSL/TLS handshake failure

### MossValidationError

Raised when input validation fails before making an API request.

**Common Causes:**
- Missing required fields
- Invalid field types
- Value out of range
- Invalid format (email, URL, etc.)

### MossParseError

Raised when response parsing fails.

**Common Causes:**
- Malformed JSON response
- Invalid PDF signature trailer
- Unexpected response format

## Basic Error Handling

### Catch All SDK Errors

```python
from moss_partner_sdk import MossPartner
from moss_partner_sdk.exceptions import MossError

async def safe_operation():
    async with MossPartner(api_key="prt_xxx") as moss:
        try:
            customer = await moss.customers.get("customer-id")
            return customer
        except MossError as e:
            print(f"SDK error: {e.message}")
            return None
```

### Handle Specific Exceptions

```python
from moss_partner_sdk.exceptions import (
    MossAPIError,
    MossNetworkError,
    MossValidationError,
    MossParseError
)

async def comprehensive_error_handling():
    async with MossPartner(api_key="prt_xxx") as moss:
        try:
            customer = await moss.customers.get("customer-id")
            return customer

        except MossAPIError as e:
            if e.status_code == 404:
                print(f"Customer not found")
                return None
            elif e.status_code == 401:
                print("Authentication failed - check API key")
                raise
            elif e.status_code >= 500:
                print(f"Server error: {e.message}")
                # Retry logic
                raise
            else:
                print(f"API error {e.status_code}: {e.message}")
                raise

        except MossNetworkError as e:
            print(f"Network error: {e.message}")
            print("Check internet connection")
            return None

        except MossValidationError as e:
            print(f"Invalid input: {e.message}")
            raise

        except MossParseError as e:
            print(f"Parse error: {e.message}")
            raise
```

## Retry Strategies

### Exponential Backoff

Retry with exponentially increasing delays:

```python
import asyncio
from moss_partner_sdk.exceptions import MossNetworkError, MossAPIError

async def retry_with_exponential_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0
):
    """
    Retry function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum retry attempts
        initial_delay: Initial delay in seconds

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    for attempt in range(max_retries):
        try:
            return await func()

        except MossNetworkError as e:
            # Always retry network errors
            should_retry = True
            error_msg = f"Network error: {e.message}"

        except MossAPIError as e:
            # Retry on 5xx errors and rate limits
            should_retry = e.status_code >= 500 or e.status_code == 429
            error_msg = f"API error {e.status_code}: {e.message}"

            if e.status_code == 429:
                # For rate limits, use longer delay
                initial_delay = 60.0

        except Exception as e:
            # Don't retry other exceptions
            raise

        if not should_retry or attempt == max_retries - 1:
            raise

        delay = initial_delay * (2 ** attempt)
        print(f"{error_msg}. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
        await asyncio.sleep(delay)


# Usage
async def get_customer_with_retry(moss, customer_id: str):
    return await retry_with_exponential_backoff(
        lambda: moss.customers.get(customer_id),
        max_retries=3
    )
```

### Retry Decorator

Create reusable retry decorator:

```python
import functools
import asyncio
from moss_partner_sdk.exceptions import MossNetworkError, MossAPIError

def retry_on_error(max_retries: int = 3, initial_delay: float = 1.0):
    """
    Decorator for automatic retry with exponential backoff.

    Usage:
        @retry_on_error(max_retries=5)
        async def my_function():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)

                except (MossNetworkError, MossAPIError) as e:
                    if isinstance(e, MossAPIError):
                        # Only retry 5xx and 429
                        if e.status_code < 500 and e.status_code != 429:
                            raise

                    if attempt == max_retries - 1:
                        raise

                    delay = initial_delay * (2 ** attempt)
                    await asyncio.sleep(delay)

            return await func(*args, **kwargs)

        return wrapper
    return decorator


# Usage
@retry_on_error(max_retries=5, initial_delay=2.0)
async def get_customer(moss, customer_id: str):
    """Get customer with automatic retry."""
    return await moss.customers.get(customer_id)
```

## Circuit Breaker Pattern

Prevent cascading failures with circuit breaker:

```python
from datetime import datetime, timedelta
from moss_partner_sdk.exceptions import MossNetworkError, MossAPIError

class CircuitBreaker:
    """
    Circuit breaker pattern for MOSS API calls.

    States:
    - CLOSED: Normal operation
    - OPEN: Circuit is open, reject calls
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def is_open(self) -> bool:
        """Check if circuit is open."""
        if self.state == "open":
            # Check if timeout passed
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

async def get_with_circuit_breaker(moss, customer_id: str):
    """Get customer with circuit breaker protection."""
    return await breaker.call(
        lambda: moss.customers.get(customer_id)
    )
```

## Validation Patterns

### Pre-Request Validation

Validate inputs before making API calls:

```python
from moss_partner_sdk.exceptions import MossValidationError

def validate_customer_creation(
    external_id: str,
    name: str,
    email: str | None
) -> None:
    """
    Validate customer creation inputs.

    Raises:
        MossValidationError: If validation fails
    """
    errors = []

    # Validate external_id
    if not external_id or not external_id.strip():
        errors.append("external_id is required")
    elif len(external_id) > 255:
        errors.append("external_id too long (max 255 chars)")
    elif not external_id.replace("_", "").replace("-", "").isalnum():
        errors.append("external_id can only contain letters, numbers, _, -")

    # Validate name
    if not name or not name.strip():
        errors.append("name is required")
    elif len(name) > 255:
        errors.append("name too long (max 255 chars)")

    # Validate email
    if email:
        if "@" not in email or "." not in email.split("@")[-1]:
            errors.append("invalid email format")
        elif len(email) > 255:
            errors.append("email too long (max 255 chars)")

    if errors:
        raise MossValidationError("; ".join(errors))


# Usage
async def create_customer_with_validation(
    moss,
    external_id: str,
    name: str,
    email: str | None = None
):
    """Create customer with pre-validation."""
    # Validate inputs first
    validate_customer_creation(external_id, name, email)

    # Create customer
    return await moss.customers.create(
        external_id=external_id,
        name=name,
        email=email
    )
```

### Pydantic Validation

Use Pydantic for structured validation:

```python
from pydantic import BaseModel, EmailStr, Field, validator

class CustomerCreateInput(BaseModel):
    """Validated input for customer creation."""

    external_id: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None

    @validator("external_id")
    def validate_external_id(cls, v):
        """Validate external_id format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("external_id can only contain letters, numbers, _, -")
        return v


# Usage
async def create_customer_pydantic(moss, input_data: dict):
    """Create customer with Pydantic validation."""
    try:
        # Validate input
        validated = CustomerCreateInput(**input_data)

        # Create customer
        return await moss.customers.create(
            external_id=validated.external_id,
            name=validated.name,
            email=validated.email
        )

    except ValidationError as e:
        # Convert Pydantic error to MossValidationError
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        raise MossValidationError("; ".join(error_messages))
```

## Logging and Monitoring

### Structured Logging

Use structured logging for better observability:

```python
import logging
import json
from moss_partner_sdk.exceptions import MossError, MossAPIError

logger = logging.getLogger(__name__)

async def logged_operation(moss, customer_id: str):
    """Operation with structured logging."""
    logger.info(
        "Starting customer fetch",
        extra={
            "customer_id": customer_id,
            "operation": "get_customer"
        }
    )

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

    except MossAPIError as e:
        logger.error(
            "API error during customer fetch",
            extra={
                "customer_id": customer_id,
                "status_code": e.status_code,
                "error_code": e.code,
                "error_message": e.message,
                "response_body": e.response_body
            }
        )
        raise

    except MossError as e:
        logger.error(
            "SDK error during customer fetch",
            extra={
                "customer_id": customer_id,
                "error_type": type(e).__name__,
                "error_message": e.message
            }
        )
        raise
```

### Error Tracking with Sentry

Integrate with Sentry for error tracking:

```python
import sentry_sdk
from moss_partner_sdk.exceptions import MossError, MossAPIError

# Initialize Sentry
sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production"
)

async def operation_with_sentry(moss, customer_id: str):
    """Operation with Sentry error tracking."""
    with sentry_sdk.configure_scope() as scope:
        scope.set_context("moss_operation", {
            "customer_id": customer_id,
            "operation": "get_customer"
        })

        try:
            customer = await moss.customers.get(customer_id)
            return customer

        except MossAPIError as e:
            # Add extra context to Sentry
            scope.set_context("api_error", {
                "status_code": e.status_code,
                "error_code": e.code,
                "response_body": e.response_body
            })

            # Capture exception in Sentry
            sentry_sdk.capture_exception(e)
            raise

        except MossError as e:
            sentry_sdk.capture_exception(e)
            raise
```

## Common Error Scenarios

### Handle 404 Not Found

```python
async def get_customer_or_none(moss, customer_id: str):
    """Get customer, return None if not found."""
    try:
        return await moss.customers.get(customer_id)
    except MossAPIError as e:
        if e.status_code == 404:
            return None
        raise
```

### Handle Duplicate Resources

```python
async def create_customer_idempotent(moss, external_id: str, name: str):
    """Create customer idempotently using external_id."""
    try:
        return await moss.customers.create(
            external_id=external_id,
            name=name
        )
    except MossAPIError as e:
        if e.code == "duplicate_external_id":
            # Find and return existing customer
            result = await moss.customers.list()
            for customer in result.data:
                if customer.external_id == external_id:
                    return customer
        raise
```

### Handle Rate Limits

```python
import asyncio

async def handle_rate_limit(moss, customer_id: str):
    """Handle rate limit with exponential backoff."""
    max_retries = 5
    base_delay = 60  # Start with 60s for rate limits

    for attempt in range(max_retries):
        try:
            return await moss.customers.get(customer_id)

        except MossAPIError as e:
            if e.status_code == 429:
                if attempt == max_retries - 1:
                    raise

                delay = base_delay * (2 ** attempt)
                print(f"Rate limited. Waiting {delay}s before retry...")
                await asyncio.sleep(delay)
            else:
                raise
```

### Handle Validation Errors

```python
async def create_with_validation_fallback(moss, data: dict):
    """Create customer with validation error handling."""
    try:
        return await moss.customers.create(**data)

    except MossValidationError as e:
        # Log validation error
        print(f"Validation error: {e.message}")

        # Attempt to fix and retry
        fixed_data = fix_validation_errors(data, e.message)
        if fixed_data:
            return await moss.customers.create(**fixed_data)

        raise


def fix_validation_errors(data: dict, error_message: str) -> dict | None:
    """Attempt to fix common validation errors."""
    # Trim whitespace
    data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}

    # Truncate long fields
    if "name" in data and len(data["name"]) > 255:
        data["name"] = data["name"][:255]

    if "external_id" in data and len(data["external_id"]) > 255:
        data["external_id"] = data["external_id"][:255]

    return data
```

## Production-Ready Error Handler

Complete production error handler:

```python
import logging
import sentry_sdk
from moss_partner_sdk.exceptions import (
    MossError,
    MossAPIError,
    MossNetworkError,
    MossValidationError,
    MossParseError
)

logger = logging.getLogger(__name__)

class ProductionErrorHandler:
    """Production-ready error handler for MOSS SDK."""

    def __init__(self, enable_sentry: bool = True):
        self.enable_sentry = enable_sentry

    async def handle_error(
        self,
        error: Exception,
        operation: str,
        context: dict
    ) -> dict:
        """
        Handle error with logging and monitoring.

        Returns error details dictionary.
        """
        error_info = {
            "operation": operation,
            "error_type": type(error).__name__,
            "context": context
        }

        if isinstance(error, MossAPIError):
            return await self._handle_api_error(error, error_info)

        elif isinstance(error, MossNetworkError):
            return await self._handle_network_error(error, error_info)

        elif isinstance(error, MossValidationError):
            return await self._handle_validation_error(error, error_info)

        elif isinstance(error, MossParseError):
            return await self._handle_parse_error(error, error_info)

        else:
            return await self._handle_unknown_error(error, error_info)

    async def _handle_api_error(self, error: MossAPIError, info: dict) -> dict:
        """Handle API errors."""
        info.update({
            "status_code": error.status_code,
            "error_code": error.code,
            "message": error.message
        })

        # Log based on severity
        if error.status_code >= 500:
            logger.error("API server error", extra=info)
        elif error.status_code == 429:
            logger.warning("Rate limit exceeded", extra=info)
        elif error.status_code == 404:
            logger.info("Resource not found", extra=info)
        else:
            logger.warning("API error", extra=info)

        # Track in Sentry
        if self.enable_sentry and error.status_code >= 500:
            sentry_sdk.capture_exception(error)

        return info

    async def _handle_network_error(self, error: MossNetworkError, info: dict) -> dict:
        """Handle network errors."""
        info["message"] = error.message

        logger.error("Network error", extra=info)

        if self.enable_sentry:
            sentry_sdk.capture_exception(error)

        return info

    async def _handle_validation_error(self, error: MossValidationError, info: dict) -> dict:
        """Handle validation errors."""
        info["message"] = error.message

        logger.warning("Validation error", extra=info)

        # Don't send to Sentry (user error)
        return info

    async def _handle_parse_error(self, error: MossParseError, info: dict) -> dict:
        """Handle parse errors."""
        info["message"] = error.message

        logger.error("Parse error", extra=info)

        if self.enable_sentry:
            sentry_sdk.capture_exception(error)

        return info

    async def _handle_unknown_error(self, error: Exception, info: dict) -> dict:
        """Handle unknown errors."""
        info["message"] = str(error)

        logger.error("Unknown error", extra=info, exc_info=True)

        if self.enable_sentry:
            sentry_sdk.capture_exception(error)

        return info


# Usage
handler = ProductionErrorHandler(enable_sentry=True)

async def production_operation(moss, customer_id: str):
    """Production operation with comprehensive error handling."""
    try:
        customer = await moss.customers.get(customer_id)
        return customer

    except MossError as e:
        error_info = await handler.handle_error(
            error=e,
            operation="get_customer",
            context={"customer_id": customer_id}
        )

        # Return error response
        return {
            "error": error_info,
            "success": False
        }
```

## See Also

- [Exceptions API Reference](../api-reference/exceptions.md) - Exception details and examples
- [Customer Lifecycle Guide](customer-lifecycle.md) - Customer operation error handling
- [Production Examples](../examples/production.md) - Production deployment patterns
