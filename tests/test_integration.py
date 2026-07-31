"""
Integration tests against staging API.

These tests verify the SDK works correctly with the M3 backend.
Requires MOSS_PARTNER_KEY environment variable.

Follows LC016 (integration tests for FULL lifecycle) and LC018 (verify actual API behavior).
"""

import pytest

from moss_partner_sdk import MossAPIError, MossPartner


@pytest.mark.integration
class TestHealthCheck:
    """Health check tests."""

    @pytest.mark.asyncio
    async def test_ping(self, skip_if_no_api_key, test_config):
        """Test API connectivity."""
        async with MossPartner(**test_config) as moss:
            is_connected = await moss.ping()
            assert is_connected is True


@pytest.mark.integration
class TestCustomerManagement:
    """Customer CRUD tests - testing FULL lifecycle (LC016)."""

    @pytest.mark.asyncio
    async def test_create_customer(self, skip_if_no_api_key, test_config, unique_id):
        """
        Test customer creation.

        LC018: Customers start as 'pending' status, not 'sandbox_active'.
        """
        async with MossPartner(**test_config) as moss:
            customer = await moss.customers.create(
                external_id=unique_id,
                name="Test Corp",
                email="test@example.com",
                governance={
                    "jurisdictions": ["US"],
                    "frameworks": ["nist_ai_rmf"],
                },
            )

            # Verify customer structure
            assert customer.id is not None
            # API returns UUID format, not cust_ prefix (LC018)
            assert len(customer.id) == 36  # UUID format
            assert customer.external_id == unique_id
            assert customer.name == "Test Corp"

            # LC018: New customers start as 'pending' status
            assert customer.status == "pending"

            # Sandbox token should be present
            assert customer.sandbox_token is not None
            assert len(customer.sandbox_token) > 0

            # Production token should be None (not promoted yet)
            assert customer.production_token is None

    @pytest.mark.asyncio
    async def test_list_customers(self, skip_if_no_api_key, test_config):
        """Test listing customers with pagination."""
        async with MossPartner(**test_config) as moss:
            result = await moss.customers.list(limit=10)

            assert result.data is not None
            assert isinstance(result.data, list)
            assert result.pagination is not None
            assert result.pagination.has_more is not None

    @pytest.mark.asyncio
    async def test_get_customer(self, skip_if_no_api_key, test_config, unique_id):
        """Test getting customer by ID."""
        async with MossPartner(**test_config) as moss:
            # First create a customer
            created = await moss.customers.create(
                external_id=f"{unique_id}_get",
                name="Get Test Corp",
            )

            # Then get it
            fetched = await moss.customers.get(created.id)

            assert fetched.id == created.id
            assert fetched.external_id == created.external_id
            assert fetched.name == created.name

    @pytest.mark.asyncio
    async def test_update_customer(self, skip_if_no_api_key, test_config, unique_id):
        """Test updating customer limits."""
        async with MossPartner(**test_config) as moss:
            # Create customer
            customer = await moss.customers.create(
                external_id=f"{unique_id}_update",
                name="Update Test Corp",
            )

            # Update it
            updated = await moss.customers.update(
                customer.id,
                limits={"agents": 25},
            )

            assert updated.limits.agents == 25

    @pytest.mark.asyncio
    async def test_404_for_nonexistent_customer(self, skip_if_no_api_key, test_config):
        """Test that getting non-existent customer raises 404 error."""
        async with MossPartner(**test_config) as moss:
            with pytest.raises(MossAPIError) as exc_info:
                await moss.customers.get("cust_nonexistent_12345")

            assert exc_info.value.status_code == 404


@pytest.mark.integration
class TestSessionTokens:
    """M3 Backend Feature: Session token tests."""

    @pytest.mark.asyncio
    async def test_create_session(self, skip_if_no_api_key, test_config, unique_id):
        """
        Test session token creation.

        LC018: API uses 900s default TTL regardless of requested TTL.
        """
        async with MossPartner(**test_config) as moss:
            # Create customer first
            customer = await moss.customers.create(
                external_id=f"{unique_id}_session",
                name="Session Test Corp",
            )

            # Create session
            session = await moss.customers.create_session(
                customer.id,
                purpose="SDK integration test",
                ttl_seconds=300,  # Request 5 min, but API may use 900s
            )

            assert session.session_token is not None
            assert session.expires_at is not None

            # Verify session expires in ~15 minutes (API uses 900s default - LC018)
            from datetime import datetime, timezone

            expires_at = session.expires_at
            now = datetime.now(timezone.utc)
            diff_seconds = (expires_at - now).total_seconds()

            # Allow tolerance for network delay
            assert diff_seconds > 800
            assert diff_seconds < 1000


@pytest.mark.integration
class TestComplianceReports:
    """M3 Backend Feature: ML-DSA-44 signed compliance reports."""

    @pytest.mark.asyncio
    async def test_generate_pdf_report(self, skip_if_no_api_key, test_config, unique_id):
        """
        Test compliance report generation with ML-DSA-44 signature.

        LC018: ML-DSA-44 signatures are ~3000-5000 chars.
        """
        async with MossPartner(**test_config) as moss:
            # Create customer first
            customer = await moss.customers.create(
                external_id=f"{unique_id}_report",
                name="Report Test Corp",
            )

            # Generate PDF report
            report = await moss.customers.compliance_report(
                customer.id,
                format="pdf",
                frameworks=["nist_ai_rmf"],
            )

            assert report.report_id is not None
            assert report.signature is not None
            assert report.key_id is not None
            assert report.generated_at is not None

            # Verify ML-DSA-44 signature length (LC018)
            assert len(report.signature) > 3000
            assert len(report.signature) < 5000

            # Verify key ID format
            assert report.key_id.startswith("moss_")

    @pytest.mark.asyncio
    async def test_generate_json_report(self, skip_if_no_api_key, test_config, unique_id):
        """Test JSON format compliance report."""
        async with MossPartner(**test_config) as moss:
            # Create customer first
            customer = await moss.customers.create(
                external_id=f"{unique_id}_json_report",
                name="JSON Report Test Corp",
            )

            # Generate JSON report
            report = await moss.customers.compliance_report(
                customer.id,
                format="json",
            )

            assert report.report_id is not None
            assert report.signature is not None

            # JSON format may include data field
            # (actual API behavior may vary)


class TestErrorHandling:
    """Error handling tests."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_api_error_on_4xx(self, skip_if_no_api_key, test_config):
        """Test that 4xx errors raise MossAPIError."""
        async with MossPartner(**test_config) as moss:
            with pytest.raises(MossAPIError) as exc_info:
                await moss.customers.get("invalid_id")

            error = exc_info.value
            assert error.status_code is not None
            assert error.code is not None
            assert error.message is not None

    def test_validate_api_key_format(self):
        """Test that API key validation happens on construction."""
        with pytest.raises(ValueError, match='api_key must start with "prt_"'):
            MossPartner(api_key="invalid_key_format")

    def test_require_api_key(self):
        """Test that API key is required."""
        with pytest.raises(ValueError, match="api_key is required"):
            MossPartner(api_key="")


@pytest.mark.integration
class TestWebhooks:
    """Webhook management tests."""

    @pytest.mark.asyncio
    async def test_list_webhooks(self, skip_if_no_api_key, test_config):
        """Test listing webhooks."""
        async with MossPartner(**test_config) as moss:
            result = await moss.webhooks.list()

            assert result.data is not None
            assert isinstance(result.data, list)


@pytest.mark.integration
class TestAnalytics:
    """Analytics tests."""

    @pytest.mark.asyncio
    async def test_get_analytics(self, skip_if_no_api_key, test_config):
        """Test getting analytics data."""
        async with MossPartner(**test_config) as moss:
            analytics = await moss.analytics.get(period="30d")

            assert analytics.customers is not None
            assert analytics.compliance is not None
            assert analytics.billing is not None
            assert analytics.period == "30d"
