"""
MOSS Partner SDK - Python client for MOSS Partner API.

Example:
    >>> from moss_partner_sdk import MossPartner
    >>>
    >>> async with MossPartner(api_key="prt_xxx") as moss:
    ...     customer = await moss.customers.create(
    ...         external_id="acme_123",
    ...         name="Acme Corp",
    ...         email="admin@acme.com",
    ...     )
    ...     print(customer.sandbox_token)
"""

from ._version import VERSION

# Main client
from .client import MossPartner

# Exceptions
from .exceptions import (
    MossAPIError,
    MossError,
    MossNetworkError,
    MossParseError,
    MossValidationError,
)

# Models
from .models import (
    AnalyticsBilling,
    AnalyticsCompliance,
    AnalyticsCustomers,
    AnalyticsResponse,
    BillingInfo,
    ComplianceInfo,
    ComplianceIssue,
    ComplianceReportResponse,
    Customer,
    CustomerListResponse,
    CustomerStatus,
    Governance,
    PaginationInfo,
    ResourceLimits,
    SessionResponse,
    Webhook,
    WebhookListResponse,
)

# Utility functions
from .webhooks import verify_webhook_signature

__version__ = VERSION

__all__ = [
    # Version
    "__version__",
    "VERSION",
    # Main client
    "MossPartner",
    # Exceptions
    "MossError",
    "MossAPIError",
    "MossNetworkError",
    "MossValidationError",
    "MossParseError",
    # Models
    "Customer",
    "CustomerStatus",
    "CustomerListResponse",
    "Governance",
    "ResourceLimits",
    "ComplianceInfo",
    "ComplianceIssue",
    "BillingInfo",
    "PaginationInfo",
    "SessionResponse",
    "ComplianceReportResponse",
    "Webhook",
    "WebhookListResponse",
    "AnalyticsResponse",
    "AnalyticsCustomers",
    "AnalyticsCompliance",
    "AnalyticsBilling",
    # Utility functions
    "verify_webhook_signature",
]
