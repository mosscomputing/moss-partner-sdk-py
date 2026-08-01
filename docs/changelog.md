# Changelog

All notable changes to the MOSS Partner SDK for Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-07-31

### 🎉 Initial Release

First public release of the MOSS Partner SDK for Python.

### Added

#### Core Client
- `MossPartner` client with async/await support
- Async context manager support (`async with`)
- Configurable timeout and retry logic
- Custom base URL support for testing
- Health check via `ping()` method

#### Customer Management
- `customers.create()` - Create new customers
- `customers.list()` - List and filter customers with pagination
- `customers.get()` - Get customer by ID
- `customers.update()` - Update customer configuration
- `customers.promote()` - Promote customer to production
- `customers.suspend()` - Suspend a customer
- `customers.reactivate()` - Reactivate suspended customer

#### Session Tokens
- `customers.create_session()` - Create temporary dashboard access tokens
- `customers.revoke_session()` - Revoke active session tokens
- TTL support (API-capped at 900 seconds per LC018)

#### Compliance Reports
- `customers.compliance_report()` - Generate ML-DSA-44 signed reports
- PDF and JSON format support
- Framework filtering (EU AI Act, NIST AI RMF, ISO 42001, etc.)
- Signature metadata extraction from PDF trailers
- Report ID and generation timestamp

#### Webhooks
- `webhooks.create()` - Create webhook subscriptions
- `webhooks.list()` - List active webhooks
- `webhooks.delete()` - Delete webhook subscriptions
- `verify_webhook_signature()` - HMAC-SHA256 signature verification
- Event pattern matching with wildcards

#### Analytics
- `analytics.get()` - Retrieve partner analytics
- Customer metrics (total, sandbox, production)
- Compliance metrics (average score, issues by severity)
- Billing metrics (MRR, ARR, churn)
- Flexible period selection (7d, 30d, 90d, 365d)

#### Data Models
- `Customer` - Complete customer representation
- `CustomerStatus` - Enum for customer states (pending, active, production, suspended)
- `Governance` - Jurisdictions and frameworks configuration
- `ResourceLimits` - Agent and request quotas
- `ComplianceInfo` - Compliance score and status
- `SessionResponse` - Session token details
- `ComplianceReportResponse` - Report with ML-DSA-44 signature
- `WebhookSubscription` - Webhook configuration
- `AnalyticsResponse` - Partner metrics

#### Error Handling
- `MossError` - Base exception class
- `MossAPIError` - API error responses (4xx, 5xx)
- `MossNetworkError` - Network failures
- `MossValidationError` - Input validation errors
- `MossParseError` - Response parsing errors
- Detailed error messages with status codes

#### Type Safety
- Comprehensive type hints throughout
- Pydantic models for data validation
- Type-safe enum values
- Generic type support for Python < 3.10

#### Testing
- Unit tests for core functionality
- Integration tests for production API
- pytest configuration
- Async test support via pytest-asyncio

#### Documentation
- Complete README with quick start
- API reference documentation
- Usage guides (customer lifecycle, session tokens, compliance, webhooks, error handling)
- Code examples (basic, advanced, production)
- Troubleshooting guide
- FAQ
- Installation instructions
- Authentication guide

#### CI/CD
- GitHub Actions workflow
- Tests across Python 3.9-3.12
- Linting (ruff)
- Type checking (mypy)
- Automated PyPI publishing
- Staging branch support

#### Security
- Pre-publish security audit (0 vulnerabilities)
- No hardcoded secrets
- Secure API key validation
- HMAC-SHA256 webhook signature verification
- Security audit report

### Dependencies

- `httpx` >= 0.24.0 - Async HTTP client
- `pydantic` >= 2.0.0 - Data validation
- `typing-extensions` >= 4.5.0 - Type hints (Python < 3.10)

### Development Dependencies

- `pytest` >= 7.0.0 - Test framework
- `pytest-asyncio` >= 0.21.0 - Async test support
- `ruff` - Linter
- `mypy` - Type checker
- `build` - Build tool

### Notes

- **Python Support**: 3.9, 3.10, 3.11, 3.12
- **License**: Proprietary
- **Pattern**: Matches TypeScript SDK exactly (LC019)
- **Security**: Passed comprehensive pre-publish audit
- **Status**: Production-ready

### Breaking Changes

None - this is the initial release.

### Migration Guide

Not applicable - this is the first version.

### Contributors

- BooCat <38902334+FattyMuffin@users.noreply.github.com>

---

## Unreleased

### Planned Features

Features being considered for future releases:

- [ ] Batch operations for bulk customer management
- [ ] Pagination helper utilities
- [ ] Retry decorator for custom operations
- [ ] Circuit breaker pattern utilities
- [ ] Metrics collection (Prometheus)
- [ ] OpenTelemetry integration
- [ ] Async iterator for pagination
- [ ] Rate limiting utilities
- [ ] Connection pooling optimization
- [ ] gRPC support (if API adds gRPC)

### Future Improvements

- Performance optimizations
- Additional code examples
- More detailed error messages
- Enhanced debugging utilities
- Video tutorials

---

## Version History

| Version | Release Date | Status | Notes |
|---------|--------------|--------|-------|
| 0.1.0 | 2026-07-31 | Current | Initial public release |

---

## Upgrade Guide

### From Development to 0.1.0

If you were using pre-release versions, upgrade to 0.1.0:

```bash
pip install --upgrade moss-partner-sdk
```

No breaking changes - the API is stable.

---

## Deprecation Policy

This project follows semantic versioning:

- **Major version (x.0.0)**: Breaking changes
- **Minor version (0.x.0)**: New features, no breaking changes
- **Patch version (0.0.x)**: Bug fixes, no breaking changes

**Deprecation Timeline**:
1. Feature marked as deprecated in minor release
2. Deprecation warnings added to code and docs
3. Feature removed in next major release (minimum 6 months notice)

---

## Support

For questions about this changelog or specific versions:

- **Documentation**: https://docs.mosscomputing.com/sdks/python
- **GitHub**: https://github.com/mosscomputing/moss-partner-sdk-py
- **Issues**: https://github.com/mosscomputing/moss-partner-sdk-py/issues
- **Email**: support@mosscomputing.com

---

## Links

- [PyPI Package](https://pypi.org/project/moss-partner-sdk/)
- [GitHub Repository](https://github.com/mosscomputing/moss-partner-sdk-py)
- [Documentation](index.md)
- [Security Audit](../SECURITY_AUDIT.md)
