"""Webhook management resource for MOSS Partner SDK."""

from __future__ import annotations

from .http import HTTPClient
from .models import Webhook, WebhookListResponse


class WebhooksResource:
    """Methods for managing webhook subscriptions."""

    def __init__(self, http: HTTPClient):
        self.http = http

    async def create(self, url: str, events: list[str]) -> Webhook:
        """
        Create a webhook subscription.

        Args:
            url: Webhook endpoint URL
            events: List of event patterns to subscribe to (e.g., ["customer.*"])

        Returns:
            Created webhook with secret for signature verification

        Example:
            >>> webhook = await moss.webhooks.create(
            ...     url="https://partner.com/webhooks/moss",
            ...     events=["customer.*", "agent.anomaly_detected"],
            ... )
            >>> print(webhook.secret)  # Use this to verify webhook signatures
        """
        body = {
            "url": url,
            "events": events,
        }

        response = await self.http.request("POST", "/v1/partner/webhooks", body=body)
        return Webhook(**response["data"])

    async def list(self) -> WebhookListResponse:
        """
        List all webhook subscriptions.

        Returns:
            List of webhook subscriptions
        """
        response = await self.http.request("GET", "/v1/partner/webhooks")
        return WebhookListResponse(data=[Webhook(**w) for w in response["data"]])

    async def delete(self, webhook_id: str) -> None:
        """
        Delete a webhook subscription.

        Args:
            webhook_id: Webhook UUID
        """
        await self.http.request("DELETE", f"/v1/partner/webhooks/{webhook_id}")


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature.

    Args:
        payload: Raw webhook payload bytes
        signature: X-Moss-Signature header value
        secret: Webhook secret from webhook.secret

    Returns:
        True if signature is valid

    Example:
        >>> from moss_partner_sdk import verify_webhook_signature
        >>>
        >>> is_valid = verify_webhook_signature(
        ...     payload=request.body,
        ...     signature=request.headers["X-Moss-Signature"],
        ...     secret=webhook.secret,
        ... )
        >>> if not is_valid:
        ...     return Response(status=401)
    """
    import hashlib
    import hmac

    expected = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
