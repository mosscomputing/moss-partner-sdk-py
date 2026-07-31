"""Main MOSS Partner SDK client."""

from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

from .analytics import AnalyticsResource
from .customers import CustomersResource
from .http import HTTPClient
from .webhooks import WebhooksResource


class MossPartner:
    """
    MOSS Partner SDK client.

    Example:
        >>> from moss_partner_sdk import MossPartner
        >>>
        >>> moss = MossPartner(api_key="prt_xxx")
        >>>
        >>> # Create a customer
        >>> customer = await moss.customers.create(
        ...     external_id="acme_123",
        ...     name="Acme Corp",
        ...     email="admin@acme.com",
        ... )
        >>> print(customer.sandbox_token)
        >>>
        >>> # Close the client when done
        >>> await moss.close()

    Or use as async context manager:
        >>> async with MossPartner(api_key="prt_xxx") as moss:
        ...     customer = await moss.customers.create(...)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mosscomputing.com",
        timeout: float = 30.0,
        retries: int = 3,
    ):
        """
        Initialize MOSS Partner SDK client.

        Args:
            api_key: Partner API key (must start with "prt_")
            base_url: Base URL for MOSS API (default: production)
            timeout: Request timeout in seconds (default: 30)
            retries: Number of retries for failed requests (default: 3)

        Raises:
            ValueError: If api_key is invalid
        """
        self._http = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
        )

        # Initialize resource classes
        self.customers = CustomersResource(self._http)
        self.webhooks = WebhooksResource(self._http)
        self.analytics = AnalyticsResource(self._http)

    async def ping(self) -> bool:
        """
        Health check - verify API connectivity.

        Returns:
            True if API is reachable

        Example:
            >>> is_connected = await moss.ping()
            >>> assert is_connected
        """
        try:
            response = await self._http.request("GET", "/health")
            status = response.get("status")
            return bool(status == "ok")
        except (OSError, ValueError):
            return False

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()
