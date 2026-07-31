"""Pydantic models for MOSS Partner SDK."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CustomerStatus(str, Enum):
    """Status of a customer account."""

    PENDING = "pending"
    SANDBOX_ACTIVE = "sandbox_active"
    PRODUCTION_ACTIVE = "production_active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class Governance(BaseModel):
    """Governance configuration for a customer."""

    jurisdictions: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    settings: Optional[Dict[str, Any]] = None


class ResourceLimits(BaseModel):
    """Resource limits for a customer."""

    agents: int
    envelopes_per_month: Optional[int] = None
    policies: Optional[int] = None


class ComplianceIssue(BaseModel):
    """A compliance issue found during assessment."""

    id: str
    severity: str
    description: str
    framework: str
    remediation_url: Optional[str] = None


class ComplianceInfo(BaseModel):
    """Compliance assessment information."""

    score: int
    status: str
    issues: List[ComplianceIssue] = Field(default_factory=list)
    last_assessment: datetime


class BillingInfo(BaseModel):
    """Billing information for a customer."""

    tier: str
    billing_email: str
    stripe_customer_id: Optional[str] = None
    current_mrr: Optional[float] = None


class Customer(BaseModel):
    """A customer in the MOSS Partner system."""

    id: str  # Mapped from API's customerId field
    external_id: str
    name: str
    email: str
    status: CustomerStatus
    sandbox_token: Optional[str] = None  # Mapped from credentials.customerToken.token
    production_token: Optional[str] = None  # Mapped from credentials.productionToken.token
    governance: Governance
    limits: ResourceLimits
    compliance: ComplianceInfo
    billing: Optional[BillingInfo] = None
    created_at: datetime
    updated_at: datetime
    promoted_at: Optional[datetime] = None
    suspended_at: Optional[datetime] = None


class PaginationInfo(BaseModel):
    """Pagination information for list responses."""

    total: int
    limit: int
    offset: int
    has_more: bool


class CustomerListResponse(BaseModel):
    """Response from list customers endpoint."""

    data: List[Customer]
    pagination: PaginationInfo


class SessionResponse(BaseModel):
    """Response from create session endpoint."""

    session_token: str  # Mapped from API's token field
    expires_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class ComplianceReportResponse(BaseModel):
    """Response from compliance report endpoint (parsed from PDF trailer)."""

    report_id: str
    signature: str
    key_id: str
    generated_at: datetime
    download_url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class Webhook(BaseModel):
    """A webhook subscription."""

    id: str
    url: str
    events: List[str]
    secret: str
    active: bool = True
    created_at: datetime
    updated_at: datetime


class WebhookListResponse(BaseModel):
    """Response from list webhooks endpoint."""

    data: List[Webhook]


class AnalyticsCustomers(BaseModel):
    """Customer analytics."""

    total: int
    sandbox: int
    production: int
    suspended: int


class AnalyticsCompliance(BaseModel):
    """Compliance analytics."""

    average_score: float
    at_risk_count: int
    non_compliant_count: int


class AnalyticsBilling(BaseModel):
    """Billing analytics."""

    current_mrr: float
    total_customers_billed: int


class AnalyticsResponse(BaseModel):
    """Response from analytics endpoint."""

    customers: AnalyticsCustomers
    compliance: AnalyticsCompliance
    billing: AnalyticsBilling
    period: str
