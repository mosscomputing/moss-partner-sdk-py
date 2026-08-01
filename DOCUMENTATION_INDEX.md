# MOSS Partner SDK - Documentation Index

Complete documentation suite for the Python Partner SDK.

**Total**: 12,500+ lines across 22 comprehensive guides

---

## 📚 Documentation Structure

### Getting Started (4 files)

| Document | Description | Lines | Link |
|----------|-------------|-------|------|
| **Index** | Main documentation hub | 200 | [docs/index.md](docs/index.md) |
| **Installation** | Platform-specific install guides | 300 | [docs/installation.md](docs/installation.md) |
| **Authentication** | API key setup and security | 400 | [docs/authentication.md](docs/authentication.md) |
| **Quick Start** | Your first request in 5 minutes | 500 | [docs/getting-started.md](docs/getting-started.md) |

### API Reference (6 files - 3,900+ lines)

| Document | Description | Lines | Link |
|----------|-------------|-------|------|
| **Client** | MossPartner client documentation | 430 | [docs/api-reference/client.md](docs/api-reference/client.md) |
| **Customers** | All customer management methods | 750 | [docs/api-reference/customers.md](docs/api-reference/customers.md) |
| **Webhooks** | Webhook subscription methods | 670 | [docs/api-reference/webhooks.md](docs/api-reference/webhooks.md) |
| **Analytics** | Analytics and metrics | 580 | [docs/api-reference/analytics.md](docs/api-reference/analytics.md) |
| **Models** | All Pydantic data models | 690 | [docs/api-reference/models.md](docs/api-reference/models.md) |
| **Exceptions** | Error handling reference | 590 | [docs/api-reference/exceptions.md](docs/api-reference/exceptions.md) |

### Usage Guides (5 files - 3,600+ lines)

| Document | Description | Lines | Link |
|----------|-------------|-------|------|
| **Customer Lifecycle** | Complete workflow from creation to production | 720 | [docs/guides/customer-lifecycle.md](docs/guides/customer-lifecycle.md) |
| **Session Tokens** | Temporary dashboard access tokens | 730 | [docs/guides/session-tokens.md](docs/guides/session-tokens.md) |
| **Compliance Reports** | ML-DSA-44 signed reports (PDF/JSON) | 730 | [docs/guides/compliance-reports.md](docs/guides/compliance-reports.md) |
| **Webhooks** | Event notifications and verification | 660 | [docs/guides/webhooks.md](docs/guides/webhooks.md) |
| **Error Handling** | Retry patterns and circuit breakers | 790 | [docs/guides/error-handling.md](docs/guides/error-handling.md) |

### Examples (3 files - 1,900+ lines)

| Document | Description | Lines | Link |
|----------|-------------|-------|------|
| **Basic Usage** | 20 common patterns and workflows | 540 | [docs/examples/basic-usage.md](docs/examples/basic-usage.md) |
| **Advanced** | Concurrent operations, testing, caching | 650 | [docs/examples/advanced.md](docs/examples/advanced.md) |
| **Production** | Deployment, monitoring, security | 730 | [docs/examples/production.md](docs/examples/production.md) |

### Help & Reference (4 files)

| Document | Description | Lines | Link |
|----------|-------------|-------|------|
| **Troubleshooting** | Common issues and solutions | 800 | [docs/troubleshooting.md](docs/troubleshooting.md) |
| **FAQ** | 40+ frequently asked questions | 600 | [docs/faq.md](docs/faq.md) |
| **Changelog** | Version history and upgrade guide | 300 | [docs/changelog.md](docs/changelog.md) |
| **Contributing** | Development and contribution guide | 700 | [docs/contributing.md](docs/contributing.md) |

---

## 🎯 Quick Navigation

### By Role

**New Users** - Start here:
1. [Installation](docs/installation.md)
2. [Authentication](docs/authentication.md)
3. [Quick Start](docs/getting-started.md)
4. [Basic Examples](docs/examples/basic-usage.md)

**Developers** - Build with confidence:
1. [API Reference](docs/api-reference/client.md)
2. [Customer Lifecycle](docs/guides/customer-lifecycle.md)
3. [Error Handling](docs/guides/error-handling.md)
4. [Advanced Examples](docs/examples/advanced.md)

**DevOps** - Deploy to production:
1. [Production Best Practices](docs/examples/production.md)
2. [Troubleshooting](docs/troubleshooting.md)
3. [FAQ](docs/faq.md)

**Contributors** - Join the project:
1. [Contributing Guide](docs/contributing.md)
2. [Changelog](docs/changelog.md)

---

### By Feature

**Customer Management**:
- [Customer Lifecycle Guide](docs/guides/customer-lifecycle.md)
- [Customers API Reference](docs/api-reference/customers.md)
- [Basic Usage Examples](docs/examples/basic-usage.md)

**Session Tokens**:
- [Session Tokens Guide](docs/guides/session-tokens.md)
- [Customers API Reference](docs/api-reference/customers.md#create_session)

**Compliance Reports**:
- [Compliance Reports Guide](docs/guides/compliance-reports.md)
- [Customers API Reference](docs/api-reference/customers.md#compliance_report)

**Webhooks**:
- [Webhooks Guide](docs/guides/webhooks.md)
- [Webhooks API Reference](docs/api-reference/webhooks.md)

**Analytics**:
- [Analytics API Reference](docs/api-reference/analytics.md)
- [Basic Usage Examples](docs/examples/basic-usage.md#analytics)

**Error Handling**:
- [Error Handling Guide](docs/guides/error-handling.md)
- [Exceptions Reference](docs/api-reference/exceptions.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 📊 Documentation Coverage

### API Methods Documented

**Customer Management (10 methods)**:
- ✅ create() - Create customers
- ✅ list() - List with pagination
- ✅ get() - Get by ID
- ✅ update() - Update configuration
- ✅ promote() - Promote to production
- ✅ suspend() - Suspend customer
- ✅ reactivate() - Reactivate customer
- ✅ create_session() - Session tokens
- ✅ revoke_session() - Revoke tokens
- ✅ compliance_report() - Signed reports

**Webhook Management (3 methods)**:
- ✅ create() - Create subscription
- ✅ list() - List subscriptions
- ✅ delete() - Delete subscription

**Analytics (1 method)**:
- ✅ get() - Retrieve metrics

**Utilities**:
- ✅ verify_webhook_signature() - HMAC verification
- ✅ ping() - Health check

### Data Models Documented (16 models)

- ✅ Customer - Main customer model
- ✅ CustomerStatus - Status enum
- ✅ Governance - Jurisdictions and frameworks
- ✅ ResourceLimits - Quotas
- ✅ ComplianceInfo - Compliance data
- ✅ SessionResponse - Session tokens
- ✅ ComplianceReportResponse - Reports with signatures
- ✅ WebhookSubscription - Webhook config
- ✅ AnalyticsResponse - Metrics
- ✅ CustomerListResponse - Paginated results
- ✅ PaginationInfo - Pagination metadata
- ✅ And 5 more analytics sub-models

### Exceptions Documented (5 types)

- ✅ MossError - Base exception
- ✅ MossAPIError - API errors (4xx/5xx)
- ✅ MossNetworkError - Network failures
- ✅ MossValidationError - Input validation
- ✅ MossParseError - Response parsing

---

## ✨ Documentation Features

### Code Examples

- **50+ runnable examples** across all guides
- **Framework integration**: FastAPI, Flask, Django
- **Real-world scenarios**: Onboarding, monitoring, compliance
- **Production patterns**: Docker, Kubernetes, monitoring

### Best Practices

- ✅ Security best practices throughout
- ✅ Error handling patterns
- ✅ Performance optimization
- ✅ Testing strategies
- ✅ Production deployment

### Developer Experience

- ✅ Clear parameter tables
- ✅ Type information for all APIs
- ✅ Exception documentation
- ✅ Cross-references between docs
- ✅ Searchable content

---

## 🔍 Search Tips

### Find by Keyword

Use GitHub search or your editor's search to find:

- **Error codes**: `401`, `404`, `429`, `500`
- **Methods**: `create`, `list`, `promote`, `suspend`
- **Concepts**: `session`, `webhook`, `compliance`, `analytics`
- **Patterns**: `retry`, `circuit breaker`, `batch`, `concurrent`

### Common Searches

| Looking for... | Search for... | Find in... |
|----------------|---------------|------------|
| How to create customers | "create customer" | getting-started.md, customers.md |
| Error handling | "MossAPIError" | exceptions.md, error-handling.md |
| Session tokens | "create_session" | session-tokens.md, customers.md |
| Webhooks | "verify_webhook" | webhooks.md (guide & API ref) |
| Production deploy | "Docker", "Kubernetes" | production.md |
| Common issues | Error message | troubleshooting.md |

---

## 📖 Reading Order

### For Beginners

1. **Overview** - [Index](docs/index.md) (5 min)
2. **Install** - [Installation](docs/installation.md) (5 min)
3. **Authenticate** - [Authentication](docs/authentication.md) (10 min)
4. **First Request** - [Quick Start](docs/getting-started.md) (15 min)
5. **Common Patterns** - [Basic Examples](docs/examples/basic-usage.md) (30 min)

**Total**: ~1 hour to productive

### For Experienced Developers

1. **API Overview** - [Client Reference](docs/api-reference/client.md) (10 min)
2. **Customer Workflow** - [Customer Lifecycle](docs/guides/customer-lifecycle.md) (20 min)
3. **Error Handling** - [Error Handling Guide](docs/guides/error-handling.md) (15 min)
4. **Advanced Patterns** - [Advanced Examples](docs/examples/advanced.md) (30 min)
5. **Production Deploy** - [Production Guide](docs/examples/production.md) (30 min)

**Total**: ~2 hours to production-ready

---

## 🚀 Getting Started Paths

### Path 1: Quick Integration (1 hour)

Perfect for: Testing the SDK quickly

1. [Installation](docs/installation.md) → Install SDK
2. [Authentication](docs/authentication.md) → Get API key
3. [Quick Start](docs/getting-started.md) → First request
4. [Basic Examples](docs/examples/basic-usage.md) → Copy patterns

### Path 2: Production Integration (1 day)

Perfect for: Building a production integration

Day 1 Morning:
- [Customer Lifecycle](docs/guides/customer-lifecycle.md)
- [Session Tokens](docs/guides/session-tokens.md)

Day 1 Afternoon:
- [Webhooks](docs/guides/webhooks.md)
- [Error Handling](docs/guides/error-handling.md)
- [Production Guide](docs/examples/production.md)

### Path 3: Master the SDK (1 week)

Perfect for: Becoming an expert

Week 1:
- Read all API Reference docs
- Work through all guides
- Study all examples
- Build a complete integration

---

## 💡 Tips for Success

### Use the Index

- Start with [docs/index.md](docs/index.md) - it has links to everything
- Bookmark pages you reference often
- Use your browser's search within page

### Learn by Example

- Copy examples from the guides
- Modify them for your use case
- Refer to API reference for details

### When Stuck

1. Check [Troubleshooting](docs/troubleshooting.md)
2. Search [FAQ](docs/faq.md)
3. Look up error in [Exceptions Reference](docs/api-reference/exceptions.md)
4. Open GitHub issue if still stuck

---

## 📝 Documentation Statistics

- **Total files**: 22 Markdown files
- **Total lines**: 12,500+ lines
- **API methods**: 15 documented
- **Data models**: 16 documented
- **Code examples**: 50+ runnable examples
- **Guides**: 5 comprehensive guides
- **Examples**: 3 example categories (basic, advanced, production)
- **Coverage**: 100% of public API

---

## 🔗 External Resources

- **PyPI Package**: https://pypi.org/project/moss-partner-sdk/
- **GitHub Repository**: https://github.com/mosscomputing/moss-partner-sdk-py
- **Issue Tracker**: https://github.com/mosscomputing/moss-partner-sdk-py/issues
- **MOSS Website**: https://mosscomputing.com
- **Support Email**: support@mosscomputing.com

---

## 📅 Last Updated

**Date**: 2026-07-31
**Version**: 0.1.0
**Commit**: a801438

---

**Happy Coding! 🎉**

For questions or feedback about this documentation, open an issue on GitHub or email support@mosscomputing.com.
