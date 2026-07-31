"""HTTP client for MOSS Partner API."""

import asyncio
from typing import Any, Dict, Optional

import httpx

from ._version import VERSION
from .exceptions import MossAPIError, MossNetworkError


class HTTPClient:
    """Async HTTP client with retry logic and error handling."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mosscomputing.com",
        timeout: float = 30.0,
        retries: int = 3,
    ):
        """
        Initialize HTTP client.

        Args:
            api_key: Partner API key (must start with "prt_")
            base_url: Base URL for MOSS API
            timeout: Request timeout in seconds
            retries: Number of retries for failed requests
        """
        if not api_key:
            raise ValueError("api_key is required")
        if not api_key.startswith("prt_"):
            raise ValueError('api_key must start with "prt_"')

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": f"moss-partner-sdk-py/{VERSION}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (e.g., "/v1/partner/customers")
            body: Request body (for POST/PUT/PATCH)
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            MossAPIError: If API returns error response
            MossNetworkError: If network request fails
        """
        client = await self._get_client()

        last_error = None
        for attempt in range(self.retries + 1):
            try:
                response = await client.request(
                    method=method,
                    url=path,
                    json=body,
                    params=params,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                # Don't retry 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    # Try to parse error response
                    try:
                        error_data = e.response.json()
                        error_message = error_data.get("error", e.response.text)
                        error_code = error_data.get("code", "api_error")
                    except Exception:
                        error_message = e.response.text
                        error_code = "api_error"

                    raise MossAPIError(
                        message=error_message,
                        status_code=e.response.status_code,
                        code=error_code,
                        response_body=e.response.text,
                    )

                # Retry 5xx errors
                last_error = e

            except httpx.RequestError as e:
                last_error = e

            # Exponential backoff for retries
            if attempt < self.retries:
                await asyncio.sleep(2**attempt)

        # All retries exhausted
        raise MossNetworkError(f"Request failed after {self.retries} retries: {last_error}")

    async def request_bytes(self, method: str, path: str) -> bytes:
        """
        Request that returns raw bytes (for PDF downloads).

        Args:
            method: HTTP method
            path: Request path

        Returns:
            Raw response bytes

        Raises:
            MossAPIError: If API returns error response
            MossNetworkError: If network request fails
        """
        client = await self._get_client()

        try:
            response = await client.request(method=method, url=path)
            response.raise_for_status()
            return response.content

        except httpx.HTTPStatusError as e:
            # Try to parse error response
            try:
                error_data = e.response.json()
                error_message = error_data.get("error", e.response.text)
                error_code = error_data.get("code", "api_error")
            except Exception:
                error_message = e.response.text
                error_code = "api_error"

            raise MossAPIError(
                message=error_message,
                status_code=e.response.status_code,
                code=error_code,
                response_body=e.response.text,
            )

        except httpx.RequestError as e:
            raise MossNetworkError(f"Request failed: {e}")

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
