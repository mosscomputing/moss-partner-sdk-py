# Contributing to MOSS Partner SDK

Thank you for your interest in contributing to the MOSS Partner SDK for Python!

---

## Code of Conduct

Be respectful and professional in all interactions. We're here to build great software together.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Good bug reports include**:

1. **Clear title**: Describe the issue in one sentence
2. **SDK version**: `moss_partner_sdk.__version__`
3. **Python version**: `python --version`
4. **Operating system**: Windows, macOS, Linux
5. **Minimal reproducible example**: Smallest code that shows the bug
6. **Expected behavior**: What should happen
7. **Actual behavior**: What actually happens
8. **Error traceback**: Full error message and stack trace

**Example**:

```markdown
## Bug: Session token TTL not respected

**SDK Version**: 0.1.0
**Python Version**: 3.11.4
**OS**: macOS 13.4

**Code**:
\`\`\`python
async with MossPartner(api_key="prt_xxx") as moss:
    session = await moss.customers.create_session(
        "cust_123",
        ttl_seconds=3600
    )
    print(session.expires_at)
\`\`\`

**Expected**: Session expires in 3600 seconds (1 hour)
**Actual**: Session expires in 900 seconds (15 minutes)

**Note**: This may be expected API behavior (LC018).
```

---

### Suggesting Features

Feature requests are welcome! Please include:

1. **Use case**: Why do you need this feature?
2. **Proposed API**: How would you like to use it?
3. **Alternatives**: What workarounds exist today?
4. **Examples**: Show how it would work

**Example**:

```markdown
## Feature Request: Batch customer creation

**Use Case**: I need to onboard 100+ customers at once during migrations.

**Proposed API**:
\`\`\`python
customers = await moss.customers.create_batch([
    {"external_id": "acme_1", "name": "Acme Corp"},
    {"external_id": "acme_2", "name": "Acme Inc"},
])
\`\`\`

**Current Workaround**:
\`\`\`python
tasks = [moss.customers.create(...) for ... in customers]
results = await asyncio.gather(*tasks, return_exceptions=True)
\`\`\`

**Benefit**: Simpler API, better error handling for batch operations.
```

---

### Contributing Code

#### Development Setup

1. **Fork the repository**:
   ```bash
   # On GitHub: Click "Fork"
   ```

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/moss-partner-sdk-py.git
   cd moss-partner-sdk-py
   ```

3. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

5. **Verify setup**:
   ```bash
   pytest tests/ -v
   ruff check src tests
   mypy src
   ```

---

#### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   # or
   git checkout -b fix/my-bug-fix
   ```

2. **Make your changes**:
   - Write code
   - Add tests
   - Update documentation

3. **Run tests locally**:
   ```bash
   # Run unit tests
   pytest tests/ -v -m "not integration"

   # Run linter
   ruff check src tests

   # Run type checker
   mypy src --ignore-missing-imports

   # Format code (if needed)
   ruff format src tests
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add batch customer creation

   - Add customers.create_batch() method
   - Add tests for batch operations
   - Update documentation

   Co-authored-by: YourName <your.email@example.com>"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/my-new-feature
   ```

6. **Create Pull Request**:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill in the template
   - Submit for review

---

#### Commit Message Format

Use conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Build/tooling changes

**Examples**:

```
feat(customers): Add batch customer creation

Add customers.create_batch() method for creating multiple
customers in a single request. Includes error handling for
partial failures.

feat(webhooks): Support custom headers

Allow passing custom headers to webhook subscriptions
for authentication with webhook receivers.

fix(sessions): Handle API TTL cap correctly

Session tokens are capped at 900s by the API (LC018).
Update documentation to reflect this behavior.

docs(guides): Add production deployment guide

Add comprehensive guide for deploying to production,
including Docker, Kubernetes, and monitoring setup.
```

---

#### Pull Request Guidelines

**Before submitting**:

- [ ] Tests pass locally
- [ ] Linter passes (ruff)
- [ ] Type checker passes (mypy)
- [ ] Documentation updated
- [ ] Changelog updated (if applicable)
- [ ] Commit messages follow conventions

**PR Description should include**:

1. **What**: Summary of changes
2. **Why**: Motivation and context
3. **How**: Implementation approach
4. **Testing**: How you tested the changes
5. **Screenshots**: If UI/output changes

**Example**:

```markdown
## Add batch customer creation

### What
Adds `customers.create_batch()` method for creating multiple customers.

### Why
Partners need to onboard many customers during migrations. Individual
calls are slow and error-prone.

### How
- New `create_batch()` method accepts list of customer dicts
- Uses `asyncio.gather()` for parallel creation
- Returns results with success/failure for each customer

### Testing
- Unit tests with mocked API
- Integration test with 10 customers
- Error handling for partial failures

### Breaking Changes
None - this is additive.
```

---

### Code Style

#### Python Style

- Follow PEP 8
- Use type hints
- Use async/await (not callbacks)
- Prefer explicit over implicit
- Keep functions small and focused

**Good**:
```python
async def create_customer(
    self,
    external_id: str,
    name: str,
    email: str | None = None
) -> Customer:
    """Create a new customer.

    Args:
        external_id: Unique identifier for the customer
        name: Customer display name
        email: Contact email (optional)

    Returns:
        Created customer with ID and tokens

    Raises:
        MossAPIError: If API returns error
        MossValidationError: If input is invalid
    """
    # Validate input
    if not external_id:
        raise MossValidationError("external_id is required")

    # Make API request
    response = await self.http.request(
        "POST",
        "/v1/partner/customers",
        body={"externalId": external_id, "name": name, "email": email}
    )

    # Map to model
    return self._map_customer(response)
```

**Bad**:
```python
# ❌ No type hints, no docstring, unclear logic
async def create(self, eid, n, e=None):
    r = await self.http.request("POST", "/v1/partner/customers", body={"externalId": eid, "name": n, "email": e})
    return self._map_customer(r)
```

---

#### Type Hints

Always use type hints:

```python
from typing import Any
from collections.abc import Sequence

# ✅ Good
def process_customers(customers: Sequence[Customer]) -> dict[str, Any]:
    ...

# ❌ Bad - no type hints
def process_customers(customers):
    ...
```

For Python 3.9 compatibility, import from `__future__`:

```python
from __future__ import annotations

def example(items: list[str]) -> dict[str, int]:  # ✅ Works in 3.9
    ...
```

---

#### Error Handling

Always raise specific exceptions:

```python
# ✅ Good
if not api_key:
    raise ValueError("api_key is required")

if not api_key.startswith("prt_"):
    raise ValueError('api_key must start with "prt_"')

# ❌ Bad
if not api_key or not api_key.startswith("prt_"):
    raise Exception("Invalid API key")
```

---

#### Testing

Write tests for all new code:

```python
import pytest
from moss_partner_sdk import MossPartner, MossAPIError

@pytest.mark.asyncio
async def test_create_customer_success():
    """Test successful customer creation."""
    moss = MossPartner(api_key="prt_test")

    customer = await moss.customers.create(
        external_id="test_001",
        name="Test Customer"
    )

    assert customer.id.startswith("cust_")
    assert customer.name == "Test Customer"
    assert customer.status == "pending"

@pytest.mark.asyncio
async def test_create_customer_duplicate():
    """Test error when external_id already exists."""
    moss = MossPartner(api_key="prt_test")

    with pytest.raises(MossAPIError) as exc_info:
        await moss.customers.create(
            external_id="existing_id",
            name="Duplicate"
        )

    assert exc_info.value.status_code == 409
```

---

### Documentation

Update documentation for all changes:

#### Docstrings

Use Google-style docstrings:

```python
async def create_session(
    self,
    customer_id: str,
    purpose: str | None = None,
    ttl_seconds: int = 900
) -> SessionResponse:
    """Create temporary session token for customer dashboard access.

    Session tokens provide time-limited access to a customer's MOSS dashboard.
    Useful for support access or embedding dashboards in your application.

    Note:
        The API caps TTL at 900 seconds (15 minutes) regardless of the
        requested value (LC018).

    Args:
        customer_id: Customer ID (must start with "cust_")
        purpose: Optional description of why session is needed
        ttl_seconds: Requested TTL in seconds (capped at 900 by API)

    Returns:
        Session response with token and expiration time

    Raises:
        MossAPIError: If API returns error (e.g., customer not found)
        MossValidationError: If customer_id is invalid

    Example:
        >>> async with MossPartner(api_key="prt_xxx") as moss:
        ...     session = await moss.customers.create_session(
        ...         "cust_123",
        ...         purpose="Support access",
        ...         ttl_seconds=300
        ...     )
        ...     print(session.session_token)
    """
```

#### API Reference

Update `docs/api-reference/*.md` when changing public APIs.

#### Guides

Update `docs/guides/*.md` when adding new features or changing workflows.

#### Examples

Add examples to `docs/examples/*.md` showing real-world usage.

---

### Review Process

1. **Automated checks**: CI runs tests, linting, type checking
2. **Code review**: Maintainers review code quality and design
3. **Documentation review**: Ensure docs are clear and complete
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge to main branch

---

### Release Process

Maintainers handle releases:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `v0.2.0`
4. Push to GitHub: CI auto-publishes to PyPI
5. Create GitHub release with notes

---

## Development Workflow

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/ -v -m "not integration"

# Integration tests (requires MOSS_PARTNER_KEY)
export MOSS_PARTNER_KEY="prt_xxx"
pytest tests/ -v -m integration

# With coverage
pytest tests/ --cov=moss_partner_sdk --cov-report=html
```

---

### Linting

```bash
# Check for issues
ruff check src tests

# Auto-fix issues
ruff check src tests --fix

# Format code
ruff format src tests
```

---

### Type Checking

```bash
# Check types
mypy src --ignore-missing-imports

# Strict mode
mypy src --strict
```

---

### Building

```bash
# Build distribution
python -m build

# Check distribution
twine check dist/*
```

---

## Questions?

- **GitHub Discussions**: For questions about contributing
- **GitHub Issues**: For bug reports and feature requests
- **Email**: partners@mosscomputing.com (for partnership questions)

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (Proprietary).

---

## Thank You!

Your contributions make this SDK better for everyone. Thank you for taking the time to contribute! 🎉
