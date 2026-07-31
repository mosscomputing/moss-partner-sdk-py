"""Customer management resource for MOSS Partner SDK."""

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .exceptions import MossParseError
from .http import HTTPClient
from .models import (
    ComplianceInfo,
    ComplianceReportResponse,
    Customer,
    CustomerListResponse,
    CustomerStatus,
    Governance,
    PaginationInfo,
    ResourceLimits,
    SessionResponse,
)


class CustomersResource:
    """Methods for managing customers (organizations)."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def _map_customer(self, api_response: Dict[str, Any]) -> Customer:
        """
        Map API response to Customer model.

        API field mappings (from TypeScript SDK customers.ts:31-50):
        - API: customerId → SDK: id
        - API: credentials.customerToken.token → SDK: sandbox_token
        - API: credentials.productionToken.token → SDK: production_token
        """
        return Customer(
            id=api_response["customerId"],  # API uses customerId, SDK exposes id
            external_id=api_response["externalId"],
            name=api_response["name"],
            email=api_response.get("email", ""),  # API may return empty string
            status=CustomerStatus(api_response["status"]),
            # Extract nested credential tokens
            sandbox_token=(
                api_response.get("credentials", {})
                .get("customerToken", {})
                .get("token")
            ),
            production_token=(
                api_response.get("credentials", {})
                .get("productionToken", {})
                .get("token")
            ),
            governance=Governance(
                **(api_response.get("governance", {"jurisdictions": [], "frameworks": []}))
            ),
            limits=ResourceLimits(**(api_response.get("limits", {"agents": 0}))),
            compliance=ComplianceInfo(
                **(
                    api_response.get("compliance", {
                        "score": 0,
                        "status": "unknown",
                        "issues": [],
                        "last_assessment": datetime.now(timezone.utc).isoformat(),
                    })
                )
            ),
            billing=api_response.get("billing"),  # Optional, may be None
            created_at=api_response["createdAt"],
            updated_at=api_response["updatedAt"],
            promoted_at=api_response.get("promotedAt"),
            suspended_at=api_response.get("suspendedAt"),
        )

    def _map_session_response(self, api_response: Dict[str, Any]) -> SessionResponse:
        """
        Map API session response to SessionResponse model.

        API field mapping (from TypeScript SDK customers.ts:57-62):
        - API: token → SDK: session_token
        """
        return SessionResponse(
            session_token=api_response.get("token") or api_response.get("sessionToken"),
            expires_at=api_response["expiresAt"],
            metadata=api_response.get("metadata"),
        )

    def _parse_pdf_signature_trailer(self, pdf_bytes: bytes) -> ComplianceReportResponse:
        """
        Extract MOSS signature metadata from PDF trailer.

        Pattern from TypeScript SDK customers.ts:69-114.
        Parses the %%MOSS-SIGNATURE-V1 trailer containing ML-DSA-44 signature.

        Args:
            pdf_bytes: Raw PDF file bytes

        Returns:
            ComplianceReportResponse with signature metadata

        Raises:
            MossParseError: If PDF trailer is invalid or missing
        """
        try:
            # Convert binary to text (ignore decoding errors for binary PDF content)
            pdf_text = pdf_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            raise MossParseError(f"Failed to decode PDF: {e}")

        # Find the signature block
        pattern = r'%%MOSS-SIGNATURE-V1-BEGIN\n(.*?)\n%%MOSS-SIGNATURE-V1-END'
        match = re.search(pattern, pdf_text, re.DOTALL)

        if not match:
            raise MossParseError("PDF does not contain MOSS signature trailer")

        trailer_json = match.group(1).strip()

        try:
            trailer = json.loads(trailer_json)
        except json.JSONDecodeError as e:
            raise MossParseError(f"Invalid MOSS signature trailer JSON: {e}")

        # Parse the signed_payload (it's double-encoded JSON)
        try:
            signed_payload = json.loads(trailer["signed_payload"])
        except (KeyError, json.JSONDecodeError) as e:
            raise MossParseError(f"Invalid signed_payload in trailer: {e}")

        # Map fields from trailer (snake_case from API)
        return ComplianceReportResponse(
            report_id=signed_payload["report_id"],
            signature=trailer["signature_hex"],
            key_id=(
                signed_payload.get("key_id")
                or trailer.get("key_id")
                or "moss_prod_2026_Q1"
            ),
            generated_at=signed_payload["generated_at"],
            download_url=trailer.get("verify_url"),
            data=signed_payload,
        )

    async def create(
        self,
        external_id: str,
        name: str,
        email: Optional[str] = None,
        governance: Optional[Dict[str, Any]] = None,
    ) -> Customer:
        """
        Create a new customer.

        Args:
            external_id: Partner's unique identifier for this customer
            name: Customer organization name
            email: Customer admin email (optional)
            governance: Governance configuration (jurisdictions, frameworks)

        Returns:
            Created customer with sandbox token

        Example:
            >>> customer = await moss.customers.create(
            ...     external_id="acme_123",
            ...     name="Acme Corp",
            ...     email="admin@acme.com",
            ...     governance={
            ...         "jurisdictions": ["EU", "US"],
            ...         "frameworks": ["eu_ai_act", "nist_ai_rmf"],
            ...     },
            ... )
            >>> print(customer.sandbox_token)
        """
        body = {
            "externalId": external_id,
            "name": name,
        }
        if email:
            body["email"] = email
        if governance:
            body["governance"] = governance

        response = await self.http.request("POST", "/v1/partner/customers", body=body)
        return self._map_customer(response["data"])

    async def list(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> CustomerListResponse:
        """
        List customers with optional filtering.

        Args:
            status: Filter by status (pending, sandbox_active, production_active, etc.)
            limit: Maximum number of customers to return (default: 100)
            offset: Pagination offset (default: 0)

        Returns:
            Paginated list of customers
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status

        response = await self.http.request("GET", "/v1/partner/customers", params=params)

        return CustomerListResponse(
            data=[self._map_customer(c) for c in response["data"]],
            pagination=PaginationInfo(**response["pagination"]),
        )

    async def get(self, customer_id: str) -> Customer:
        """
        Get a customer by ID.

        Args:
            customer_id: Customer UUID

        Returns:
            Customer details

        Raises:
            MossAPIError: If customer not found (404)
        """
        response = await self.http.request("GET", f"/v1/partner/customers/{customer_id}")
        return self._map_customer(response["data"])

    async def update(
        self,
        customer_id: str,
        limits: Optional[Dict[str, Any]] = None,
        governance: Optional[Dict[str, Any]] = None,
    ) -> Customer:
        """
        Update a customer's configuration.

        Args:
            customer_id: Customer UUID
            limits: Resource limits to update (e.g., {"agents": 50})
            governance: Governance configuration to update

        Returns:
            Updated customer
        """
        body = {}
        if limits:
            body["limits"] = limits
        if governance:
            body["governance"] = governance

        response = await self.http.request(
            "PATCH", f"/v1/partner/customers/{customer_id}", body=body
        )
        return self._map_customer(response["data"])

    async def promote(
        self,
        customer_id: str,
        attestation: Dict[str, Any],
        billing: Dict[str, Any],
    ) -> Customer:
        """
        Promote customer to production.

        Args:
            customer_id: Customer UUID
            attestation: KYC attestation data
            billing: Billing configuration (tier, billing_email)

        Returns:
            Promoted customer with production token
        """
        body = {
            "attestation": attestation,
            "billing": billing,
        }

        response = await self.http.request(
            "POST", f"/v1/partner/customers/{customer_id}/promote", body=body
        )
        return self._map_customer(response["data"])

    async def suspend(
        self,
        customer_id: str,
        reason: str,
        grace_period_hours: Optional[int] = None,
    ) -> Customer:
        """
        Suspend a customer.

        Args:
            customer_id: Customer UUID
            reason: Suspension reason
            grace_period_hours: Grace period before full suspension

        Returns:
            Suspended customer
        """
        body = {"reason": reason}
        if grace_period_hours is not None:
            body["gracePeriodHours"] = grace_period_hours

        response = await self.http.request(
            "POST", f"/v1/partner/customers/{customer_id}/suspend", body=body
        )
        return self._map_customer(response["data"])

    async def reactivate(
        self,
        customer_id: str,
        resolution: Dict[str, Any],
    ) -> Customer:
        """
        Reactivate a suspended customer.

        Args:
            customer_id: Customer UUID
            resolution: Resolution information

        Returns:
            Reactivated customer
        """
        body = {"resolution": resolution}

        response = await self.http.request(
            "POST", f"/v1/partner/customers/{customer_id}/reactivate", body=body
        )
        return self._map_customer(response["data"])

    async def create_session(
        self,
        customer_id: str,
        purpose: str,
        ttl_seconds: int = 300,
    ) -> SessionResponse:
        """
        Create a temporary session token for customer.

        Note (from LC018): API always uses 900s TTL regardless of requested TTL.

        Args:
            customer_id: Customer UUID
            purpose: Purpose description
            ttl_seconds: Requested TTL (API may ignore and use 900s default)

        Returns:
            Session token and expiration
        """
        body = {
            "customerId": customer_id,
            "purpose": purpose,
            "ttlSeconds": ttl_seconds,
        }

        response = await self.http.request(
            "POST", f"/v1/partner/customers/{customer_id}/sessions", body=body
        )
        return self._map_session_response(response["data"])

    async def revoke_session(self, customer_id: str, session_token: str) -> None:
        """
        Revoke a session token.

        Args:
            customer_id: Customer UUID
            session_token: Session token to revoke
        """
        body = {"sessionToken": session_token}

        await self.http.request(
            "POST", f"/v1/partner/customers/{customer_id}/sessions/revoke", body=body
        )

    async def compliance_report(
        self,
        customer_id: str,
        format: str = "pdf",
        frameworks: Optional[list] = None,
    ) -> ComplianceReportResponse:
        """
        Generate ML-DSA-44 signed compliance report.

        Args:
            customer_id: Customer UUID
            format: Report format ("pdf" or "json")
            frameworks: Frameworks to include (e.g., ["eu_ai_act"])

        Returns:
            Compliance report with ML-DSA-44 signature

        Note:
            For PDF format, signature is extracted from PDF trailer.
            ML-DSA-44 signatures are ~3000-5000 chars (from LC018).
        """
        params: Dict[str, Any] = {"format": format}
        if frameworks:
            params["frameworks"] = ",".join(frameworks)

        # For PDF format, get raw bytes
        if format == "pdf":
            pdf_bytes = await self.http.request_bytes(
                "GET", f"/v1/partner/customers/{customer_id}/compliance-report"
            )
            return self._parse_pdf_signature_trailer(pdf_bytes)

        # For JSON format, get JSON response
        response = await self.http.request(
            "GET",
            f"/v1/partner/customers/{customer_id}/compliance-report",
            params=params,
        )
        # JSON format includes signature in response
        return ComplianceReportResponse(**response["data"])
