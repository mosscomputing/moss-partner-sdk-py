# Session Tokens Guide

Temporary session tokens provide secure, time-limited dashboard access for customers without exposing long-lived credentials.

## Overview

Session tokens enable:

- **One-time login links** for customer support
- **Embedded dashboards** in partner portals
- **Temporary access** for audits or demos
- **Secure delegation** without sharing API keys

## Key Characteristics

| Property | Value | Notes |
|----------|-------|-------|
| **TTL** | 900 seconds (15 minutes) | API enforces this regardless of request (LC018) |
| **Single customer** | Yes | Each token is scoped to one customer |
| **Revocable** | Yes | Can be revoked before expiration |
| **Audit logged** | Yes | Creation and usage are logged |

## Creating Session Tokens

### Basic Creation

```python
import asyncio
from moss_partner_sdk import MossPartner

async def create_session():
    async with MossPartner(api_key="prt_xxx") as moss:
        session = await moss.customers.create_session(
            customer_id="550e8400-e29b-41d4-a716-446655440000",
            purpose="Support dashboard access",
            ttl_seconds=300  # Request 5 mins (API will use 900s)
        )

        print(f"Session Token: {session.session_token}")
        print(f"Expires At: {session.expires_at}")
        print(f"Valid for: 15 minutes")  # API always uses 900s

        return session

if __name__ == "__main__":
    asyncio.run(create_session())
```

### TTL Behavior (Important!)

According to learning LC018, the API **always uses 900 seconds (15 minutes)** regardless of the requested TTL. This is a known limitation:

```python
# Requested: 300 seconds (5 minutes)
# Actual: 900 seconds (15 minutes)
session = await moss.customers.create_session(
    customer_id=customer_id,
    purpose="Quick access",
    ttl_seconds=300  # API ignores this and uses 900s
)

# Check actual expiration
from datetime import datetime
now = datetime.now(session.expires_at.tzinfo)
actual_ttl = (session.expires_at - now).total_seconds()
print(f"Actual TTL: {actual_ttl} seconds")  # Will be ~900
```

**Best Practice**: Always assume 15-minute TTL in your application logic.

## Use Cases

### 1. Support Dashboard Access

Generate a one-time link for customer support agents:

```python
async def generate_support_link(
    customer_id: str,
    support_agent: str,
    ticket_id: str
) -> str:
    """
    Generate one-time dashboard link for support agent.

    Args:
        customer_id: Customer UUID
        support_agent: Support agent identifier
        ticket_id: Support ticket number

    Returns:
        One-time login URL
    """
    async with MossPartner(api_key="prt_xxx") as moss:
        session = await moss.customers.create_session(
            customer_id=customer_id,
            purpose=f"Support access by {support_agent} for ticket {ticket_id}"
        )

        # Generate login URL
        base_url = "https://app.mosscomputing.com"
        login_url = f"{base_url}/login?session={session.session_token}"

        # Log the access for audit
        await log_support_access(
            customer_id=customer_id,
            agent=support_agent,
            ticket_id=ticket_id,
            expires_at=session.expires_at
        )

        return login_url


async def log_support_access(
    customer_id: str,
    agent: str,
    ticket_id: str,
    expires_at
):
    """Log support access for audit trail."""
    # Your logging implementation
    print(f"Support access granted: {agent} → {customer_id} (ticket {ticket_id})")
```

### 2. Embedded Dashboard Widget

Embed MOSS dashboard in your partner portal:

```python
from datetime import datetime, timedelta

async def get_embedded_dashboard_url(customer_id: str) -> dict:
    """
    Generate embedded dashboard URL with session token.

    Returns URL and expiration time for iframe embedding.
    """
    async with MossPartner(api_key="prt_xxx") as moss:
        session = await moss.customers.create_session(
            customer_id=customer_id,
            purpose="Partner portal embedded widget"
        )

        return {
            "iframe_url": (
                f"https://app.mosscomputing.com/embed"
                f"?token={session.session_token}"
            ),
            "expires_at": session.expires_at,
            "valid_for_minutes": 15,  # API default
            "refresh_before": session.expires_at - timedelta(minutes=2)
        }


# Frontend usage (JavaScript)
"""
// Embed in your portal
async function loadMossDashboard(customerId) {
    // Get session URL from your backend
    const response = await fetch(`/api/moss/embed/${customerId}`);
    const { iframe_url, expires_at, refresh_before } = await response.json();

    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.src = iframe_url;
    iframe.width = '100%';
    iframe.height = '600px';
    document.getElementById('moss-widget').appendChild(iframe);

    // Auto-refresh before expiration
    const refreshTime = new Date(refresh_before) - new Date();
    setTimeout(() => {
        console.log('Refreshing session...');
        loadMossDashboard(customerId);
    }, refreshTime);
}
"""
```

### 3. Audit or Compliance Review

Temporary access for auditors:

```python
async def grant_auditor_access(
    customer_id: str,
    auditor_email: str,
    audit_reference: str
) -> dict:
    """
    Grant temporary access to auditor.

    Returns login credentials and access details.
    """
    async with MossPartner(api_key="prt_xxx") as moss:
        session = await moss.customers.create_session(
            customer_id=customer_id,
            purpose=f"Audit access: {audit_reference} by {auditor_email}"
        )

        # Send credentials to auditor
        await send_auditor_credentials(
            email=auditor_email,
            login_url=f"https://app.mosscomputing.com/login?session={session.session_token}",
            expires_at=session.expires_at,
            audit_reference=audit_reference
        )

        return {
            "auditor": auditor_email,
            "access_granted_at": datetime.now(),
            "expires_at": session.expires_at,
            "audit_reference": audit_reference
        }


async def send_auditor_credentials(
    email: str,
    login_url: str,
    expires_at: datetime,
    audit_reference: str
):
    """Send access credentials to auditor."""
    # Your email implementation
    subject = f"MOSS Audit Access - {audit_reference}"
    body = f"""
    You have been granted temporary access to MOSS for audit purposes.

    Reference: {audit_reference}
    Login URL: {login_url}
    Expires: {expires_at} (15 minutes)

    This link will expire automatically and cannot be reused.
    """
    print(f"Sending to {email}: {subject}")
```

### 4. Demo or Trial Access

Provide temporary demo access to prospects:

```python
async def create_demo_access(
    prospect_email: str,
    demo_customer_id: str
) -> str:
    """
    Create demo access for sales prospect.

    Args:
        prospect_email: Prospect's email
        demo_customer_id: Pre-configured demo customer

    Returns:
        Demo login URL
    """
    async with MossPartner(api_key="prt_xxx") as moss:
        session = await moss.customers.create_session(
            customer_id=demo_customer_id,
            purpose=f"Demo access for {prospect_email}"
        )

        login_url = (
            f"https://app.mosscomputing.com/login"
            f"?session={session.session_token}"
            f"&demo=true"
        )

        # Send demo email
        await send_demo_email(
            email=prospect_email,
            login_url=login_url,
            expires_at=session.expires_at
        )

        return login_url


async def send_demo_email(email: str, login_url: str, expires_at: datetime):
    """Send demo access email to prospect."""
    # Your email implementation
    print(f"Sending demo to {email}, expires {expires_at}")
```

## Session Management

### Auto-Refresh Pattern

Automatically refresh sessions before expiration:

```python
import asyncio
from datetime import datetime, timedelta

class SessionManager:
    """Manage session tokens with auto-refresh."""

    def __init__(self, moss_client, customer_id: str):
        self.moss = moss_client
        self.customer_id = customer_id
        self.current_session = None
        self.refresh_task = None

    async def start(self, purpose: str = "Auto-managed session"):
        """Start session with auto-refresh."""
        # Create initial session
        self.current_session = await self.moss.customers.create_session(
            customer_id=self.customer_id,
            purpose=purpose
        )

        # Schedule refresh before expiration
        await self._schedule_refresh(purpose)

        return self.current_session.session_token

    async def _schedule_refresh(self, purpose: str):
        """Schedule refresh 2 minutes before expiration."""
        if self.current_session is None:
            return

        # Calculate time until refresh (13 minutes, leaving 2min buffer)
        now = datetime.now(self.current_session.expires_at.tzinfo)
        time_until_refresh = (
            self.current_session.expires_at - now - timedelta(minutes=2)
        ).total_seconds()

        # Don't schedule if already expired
        if time_until_refresh <= 0:
            return

        # Schedule refresh
        self.refresh_task = asyncio.create_task(
            self._auto_refresh(purpose, time_until_refresh)
        )

    async def _auto_refresh(self, purpose: str, delay: float):
        """Auto-refresh session after delay."""
        await asyncio.sleep(delay)

        # Refresh session
        self.current_session = await self.moss.customers.create_session(
            customer_id=self.customer_id,
            purpose=purpose
        )

        print(f"Session refreshed, new expiry: {self.current_session.expires_at}")

        # Schedule next refresh
        await self._schedule_refresh(purpose)

    async def stop(self):
        """Stop session and cancel refresh."""
        if self.refresh_task:
            self.refresh_task.cancel()

        if self.current_session:
            # Revoke current session
            await self.moss.customers.revoke_session(
                customer_id=self.customer_id,
                session_token=self.current_session.session_token
            )

    def get_token(self) -> str | None:
        """Get current session token."""
        if self.current_session:
            return self.current_session.session_token
        return None


# Usage
async def use_session_manager():
    async with MossPartner(api_key="prt_xxx") as moss:
        manager = SessionManager(moss, customer_id="customer-uuid")

        # Start auto-managed session
        token = await manager.start(purpose="Long-running widget")
        print(f"Session token: {token}")

        # Use the session for extended period
        # Manager will auto-refresh every 13 minutes
        await asyncio.sleep(3600)  # 1 hour

        # Stop and cleanup
        await manager.stop()
```

### Session Pool for High-Volume Access

Manage multiple sessions for load balancing:

```python
from collections import deque

class SessionPool:
    """Pool of session tokens for high-volume access."""

    def __init__(self, moss_client, customer_id: str, pool_size: int = 5):
        self.moss = moss_client
        self.customer_id = customer_id
        self.pool_size = pool_size
        self.sessions = deque()

    async def initialize(self):
        """Create initial pool of sessions."""
        for i in range(self.pool_size):
            session = await self.moss.customers.create_session(
                customer_id=self.customer_id,
                purpose=f"Pool session {i+1}/{self.pool_size}"
            )
            self.sessions.append(session)

        print(f"Session pool initialized with {self.pool_size} sessions")

    async def get_session(self):
        """Get a session from the pool (round-robin)."""
        if not self.sessions:
            await self.initialize()

        # Rotate pool
        session = self.sessions[0]
        self.sessions.rotate(-1)

        # Check if expired
        now = datetime.now(session.expires_at.tzinfo)
        if now >= session.expires_at:
            # Refresh this session
            session = await self.moss.customers.create_session(
                customer_id=self.customer_id,
                purpose="Pool session refresh"
            )
            self.sessions[0] = session

        return session.session_token

    async def cleanup(self):
        """Revoke all sessions in pool."""
        for session in self.sessions:
            try:
                await self.moss.customers.revoke_session(
                    customer_id=self.customer_id,
                    session_token=session.session_token
                )
            except Exception as e:
                print(f"Failed to revoke session: {e}")

        self.sessions.clear()
```

## Security Considerations

### 1. Purpose Logging

Always provide descriptive purpose for audit trail:

```python
# Good: Descriptive purpose
await moss.customers.create_session(
    customer_id=customer_id,
    purpose="Support ticket #12345 - billing issue investigation by agent@partner.com"
)

# Bad: Generic purpose
await moss.customers.create_session(
    customer_id=customer_id,
    purpose="Dashboard access"
)
```

### 2. Secure Token Transmission

Never log or expose session tokens:

```python
async def safe_create_session(customer_id: str):
    """Create session with secure handling."""
    session = await moss.customers.create_session(
        customer_id=customer_id,
        purpose="Secure access"
    )

    # DON'T: Log the token
    # print(f"Token: {session.session_token}")  # BAD!

    # DO: Log creation without token
    print(f"Session created, expires {session.expires_at}")

    # DO: Transmit over HTTPS only
    return {
        "expires_at": session.expires_at.isoformat(),
        # Token sent separately via secure channel
    }
```

### 3. Revocation After Use

Revoke sessions immediately when no longer needed:

```python
async def one_time_access(customer_id: str):
    """Create session, use it, then immediately revoke."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Create session
        session = await moss.customers.create_session(
            customer_id=customer_id,
            purpose="One-time report generation"
        )

        try:
            # Use the session
            report_url = f"https://app.mosscomputing.com/report?token={session.session_token}"
            await generate_report(report_url)

        finally:
            # Always revoke, even on error
            await moss.customers.revoke_session(
                customer_id=customer_id,
                session_token=session.session_token
            )
            print("Session revoked after use")
```

### 4. IP Restriction (Application-Level)

Track and validate session usage:

```python
class SecureSessionManager:
    """Session manager with IP restriction."""

    def __init__(self, moss_client):
        self.moss = moss_client
        self.session_ips = {}  # token -> allowed_ip

    async def create_session(
        self,
        customer_id: str,
        allowed_ip: str,
        purpose: str
    ):
        """Create session with IP restriction."""
        session = await self.moss.customers.create_session(
            customer_id=customer_id,
            purpose=f"{purpose} (IP: {allowed_ip})"
        )

        # Store IP restriction
        self.session_ips[session.session_token] = allowed_ip

        return session

    def validate_session_ip(self, session_token: str, request_ip: str) -> bool:
        """Validate session is being used from allowed IP."""
        allowed_ip = self.session_ips.get(session_token)
        if not allowed_ip:
            return False

        return request_ip == allowed_ip

    async def revoke_session(self, customer_id: str, session_token: str):
        """Revoke session and clear IP record."""
        await self.moss.customers.revoke_session(
            customer_id=customer_id,
            session_token=session_token
        )
        self.session_ips.pop(session_token, None)
```

## Revocation

### Manual Revocation

Revoke a session before expiration:

```python
async def revoke_session_example():
    async with MossPartner(api_key="prt_xxx") as moss:
        # Create session
        session = await moss.customers.create_session(
            customer_id="customer-uuid",
            purpose="Temporary access"
        )

        # Use it...
        print(f"Session active: {session.session_token}")

        # Revoke it
        await moss.customers.revoke_session(
            customer_id="customer-uuid",
            session_token=session.session_token
        )

        print("Session revoked - no longer valid")
```

### Revoke All Sessions for Customer

```python
async def revoke_all_customer_sessions(customer_id: str):
    """
    Revoke all active sessions for a customer.

    Note: You need to track sessions yourself - API doesn't list them.
    """
    # Your session tracking implementation
    active_sessions = await get_tracked_sessions(customer_id)

    async with MossPartner(api_key="prt_xxx") as moss:
        for session_token in active_sessions:
            try:
                await moss.customers.revoke_session(
                    customer_id=customer_id,
                    session_token=session_token
                )
                print(f"Revoked session: {session_token[:20]}...")
            except Exception as e:
                print(f"Failed to revoke session: {e}")


async def get_tracked_sessions(customer_id: str) -> list[str]:
    """Get tracked sessions from your database/cache."""
    # Your implementation
    return []
```

### Emergency Revocation

Revoke sessions in emergency scenarios:

```python
async def emergency_revoke(customer_id: str, reason: str):
    """Emergency revocation with logging and alerts."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Get all tracked sessions
        sessions = await get_tracked_sessions(customer_id)

        # Log emergency action
        await log_security_event(
            event_type="emergency_session_revocation",
            customer_id=customer_id,
            reason=reason,
            session_count=len(sessions)
        )

        # Revoke all sessions
        for session_token in sessions:
            await moss.customers.revoke_session(
                customer_id=customer_id,
                session_token=session_token
            )

        # Alert security team
        await alert_security_team(
            f"Emergency: Revoked {len(sessions)} sessions for {customer_id}. "
            f"Reason: {reason}"
        )


async def log_security_event(**kwargs):
    """Log security event."""
    print(f"SECURITY EVENT: {kwargs}")


async def alert_security_team(message: str):
    """Alert security team."""
    print(f"SECURITY ALERT: {message}")
```

## Best Practices

1. **Always set descriptive purposes** for audit trail
2. **Assume 15-minute TTL** - API ignores requested TTL (LC018)
3. **Revoke immediately** when access no longer needed
4. **Never log tokens** - log creation events only
5. **Use HTTPS only** for token transmission
6. **Track sessions** if you need to revoke them later
7. **Refresh proactively** - don't wait until expiration
8. **Validate context** - check IP, user agent, etc. at application level

## Common Patterns

### Pattern: Support Agent Workflow

```python
async def support_agent_workflow(
    ticket_id: str,
    customer_id: str,
    agent_email: str
):
    """Complete support agent access workflow."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # 1. Create session
        session = await moss.customers.create_session(
            customer_id=customer_id,
            purpose=f"Support ticket {ticket_id} by {agent_email}"
        )

        # 2. Generate login URL
        login_url = (
            f"https://app.mosscomputing.com/login"
            f"?session={session.session_token}"
            f"&ticket={ticket_id}"
        )

        # 3. Send to agent
        await send_to_agent(agent_email, login_url, session.expires_at)

        # 4. Return session info
        return {
            "login_url": login_url,
            "expires_at": session.expires_at,
            "valid_for_minutes": 15
        }


async def send_to_agent(email: str, url: str, expires_at: datetime):
    """Send access URL to support agent."""
    print(f"Sending to {email}: {url} (expires {expires_at})")
```

## See Also

- [Customer Lifecycle Guide](customer-lifecycle.md) - Customer management workflow
- [Error Handling Guide](error-handling.md) - Handling session errors
- [Customers API Reference](../api-reference/customers.md) - Session token API details
