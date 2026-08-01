# MOSS Partner SDK for Python - Documentation

Complete guide to integrating the MOSS Partner API into your Python applications.

## Overview

The MOSS Partner SDK provides a clean, async-first Python interface for managing customers, configuring governance policies, and monitoring compliance through the MOSS Partner API.

**Key Features**:
- 🔐 **Customer Management**: Create, update, promote, suspend, and reactivate customers
- 🎫 **Session Tokens**: Generate temporary dashboard access tokens
- 📊 **Compliance Reports**: ML-DSA-44 signed compliance reports (PDF/JSON)
- 🔔 **Webhooks**: Real-time event notifications with signature verification
- 📈 **Analytics**: Customer, compliance, and billing insights
- ⚡ **Async/Await**: Built on `httpx` for high-performance async operations
- 🔒 **Type Safety**: Comprehensive type hints with Pydantic models
- 🛡️ **Error Handling**: Typed exceptions for API, network, and validation errors

---

## Quick Links

### Getting Started
- [Installation](installation.md) - Install the SDK
- [Authentication](authentication.md) - Set up your API key
- [Quick Start](getting-started.md) - Your first request in 5 minutes

### API Reference
- [MossPartner Client](api-reference/client.md) - Main SDK client
- [Customers](api-reference/customers.md) - Customer management methods
- [Webhooks](api-reference/webhooks.md) - Webhook subscription methods
- [Analytics](api-reference/analytics.md) - Analytics methods
- [Models](api-reference/models.md) - Data models and types
- [Exceptions](api-reference/exceptions.md) - Error handling

### Guides
- [Customer Lifecycle](guides/customer-lifecycle.md) - Complete customer workflow
- [Session Tokens](guides/session-tokens.md) - Temporary dashboard access
- [Compliance Reports](guides/compliance-reports.md) - Generate signed reports
- [Webhooks](guides/webhooks.md) - Event notifications and verification
- [Error Handling](guides/error-handling.md) - Handle errors gracefully

### Examples
- [Basic Usage](examples/basic-usage.md) - Common patterns
- [Advanced](examples/advanced.md) - Advanced techniques
- [Production](examples/production.md) - Production best practices

### Help
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [FAQ](faq.md) - Frequently asked questions
- [Changelog](changelog.md) - Version history
- [Contributing](contributing.md) - Contribution guide

---

## Installation

```bash
pip install moss-partner-sdk
```

Requires Python 3.9+

---

## Quick Example

```python
import asyncio
from moss_partner_sdk import MossPartner

async def main():
    # Initialize with your API key
    async with MossPartner(api_key="prt_xxx") as moss:
        # Create a customer
        customer = await moss.customers.create(
            external_id="acme_123",
            name="Acme Corp",
            email="admin@acme.com",
            governance={
                "jurisdictions": ["EU", "US"],
                "frameworks": ["eu_ai_act", "nist_ai_rmf"],
            },
        )

        print(f"Customer created: {customer.id}")
        print(f"Sandbox token: {customer.sandbox_token}")
        print(f"Status: {customer.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Support

- **Documentation**: https://docs.mosscomputing.com/sdks/python
- **PyPI**: https://pypi.org/project/moss-partner-sdk/
- **GitHub**: https://github.com/mosscomputing/moss-partner-sdk-py
- **Issues**: https://github.com/mosscomputing/moss-partner-sdk-py/issues
- **Email**: support@mosscomputing.com

---

## License

Proprietary - See [LICENSE](../LICENSE) file for details.

---

## Next Steps

1. [Install the SDK](installation.md)
2. [Get your API key](authentication.md)
3. [Follow the quick start guide](getting-started.md)
4. [Explore the API reference](api-reference/client.md)
