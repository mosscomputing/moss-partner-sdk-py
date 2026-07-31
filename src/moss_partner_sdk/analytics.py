"""Analytics resource for MOSS Partner SDK."""

from .http import HTTPClient
from .models import AnalyticsResponse


class AnalyticsResource:
    """Methods for accessing analytics data."""

    def __init__(self, http: HTTPClient):
        self.http = http

    async def get(self, period: str = "30d") -> AnalyticsResponse:
        """
        Get analytics for the specified period.

        Args:
            period: Time period (e.g., "7d", "30d", "90d")

        Returns:
            Analytics data (customers, compliance, billing)

        Example:
            >>> analytics = await moss.analytics.get(period="30d")
            >>> print(f"Total customers: {analytics.customers.total}")
            >>> print(f"Average compliance score: {analytics.compliance.average_score}")
            >>> print(f"Current MRR: ${analytics.billing.current_mrr}")
        """
        params = {"period": period}

        response = await self.http.request("GET", "/v1/partner/analytics", params=params)
        return AnalyticsResponse(**response["data"])
