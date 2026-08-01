# Installation

## Requirements

- **Python**: 3.9 or higher
- **Dependencies**:
  - `httpx` >= 0.24.0 (async HTTP client)
  - `pydantic` >= 2.0.0 (data validation)
  - `typing-extensions` >= 4.5.0 (Python < 3.10)

---

## Install from PyPI

### Basic Installation

```bash
pip install moss-partner-sdk
```

### With Development Tools

If you're contributing or want to run tests locally:

```bash
pip install moss-partner-sdk[dev]
```

This includes:
- `pytest` - Test runner
- `pytest-asyncio` - Async test support
- `ruff` - Linter
- `mypy` - Type checker

---

## Install from Source

### Clone the Repository

```bash
git clone https://github.com/mosscomputing/moss-partner-sdk-py.git
cd moss-partner-sdk-py
```

### Install in Development Mode

```bash
pip install -e .
```

Or with dev dependencies:

```bash
pip install -e ".[dev]"
```

---

## Verify Installation

```python
import moss_partner_sdk

print(moss_partner_sdk.__version__)  # Should print: 0.1.0
```

Or check available modules:

```python
from moss_partner_sdk import MossPartner, MossAPIError

print("SDK imported successfully!")
```

---

## Virtual Environment (Recommended)

### Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install SDK
pip install moss-partner-sdk
```

### Using conda

```bash
# Create environment
conda create -n moss-sdk python=3.11

# Activate
conda activate moss-sdk

# Install SDK
pip install moss-partner-sdk
```

---

## Upgrading

### To Latest Version

```bash
pip install --upgrade moss-partner-sdk
```

### To Specific Version

```bash
pip install moss-partner-sdk==0.1.0
```

---

## Uninstalling

```bash
pip uninstall moss-partner-sdk
```

---

## Platform-Specific Notes

### macOS

```bash
# If you encounter SSL certificate errors
pip install --upgrade certifi
```

### Windows

```bash
# If you encounter encoding issues, set UTF-8 encoding
set PYTHONIOENCODING=utf-8
pip install moss-partner-sdk
```

### Linux

```bash
# On some distributions, you may need python3-dev
sudo apt-get install python3-dev  # Debian/Ubuntu
sudo yum install python3-devel     # RHEL/CentOS
```

---

## Docker

### Using Official Python Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install SDK
RUN pip install moss-partner-sdk

# Copy your application
COPY . .

CMD ["python", "your_app.py"]
```

### Build and Run

```bash
docker build -t my-moss-app .
docker run -e MOSS_API_KEY=prt_xxx my-moss-app
```

---

## Dependency Compatibility

### Tested Python Versions

- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12

### Required Dependencies

| Package | Minimum Version | Purpose |
|---------|----------------|---------|
| httpx | 0.24.0 | Async HTTP requests |
| pydantic | 2.0.0 | Data validation |
| typing-extensions | 4.5.0 | Type hints (Python < 3.10) |

### Development Dependencies

| Package | Purpose |
|---------|---------|
| pytest | Test runner |
| pytest-asyncio | Async test support |
| ruff | Linting |
| mypy | Type checking |

---

## Troubleshooting Installation

### SSL Certificate Errors

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org moss-partner-sdk
```

Or upgrade certifi:

```bash
pip install --upgrade certifi
```

### Permission Denied

Use `--user` flag to install for current user only:

```bash
pip install --user moss-partner-sdk
```

### Dependency Conflicts

Create a fresh virtual environment:

```bash
python -m venv fresh-env
source fresh-env/bin/activate  # or fresh-env\Scripts\activate on Windows
pip install moss-partner-sdk
```

---

## Next Steps

After installation:

1. [Set up authentication](authentication.md)
2. [Follow the quick start guide](getting-started.md)
3. [Explore the API reference](api-reference/client.md)

---

## Support

If you encounter installation issues:

- Check [Troubleshooting](troubleshooting.md)
- Search [GitHub Issues](https://github.com/mosscomputing/moss-partner-sdk-py/issues)
- Email: support@mosscomputing.com
