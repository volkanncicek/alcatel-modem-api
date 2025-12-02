# Contributing to Alcatel Modem API

Thank you for your interest in contributing to Alcatel Modem API! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/volkanncicek/alcatel-modem-api.git
   cd alcatel-modem-api
   ```

2. **Install the package in development mode:**
   ```bash
   # Using uv (recommended)
   uv pip install -e ".[dev]"
   
   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks (optional but recommended):**
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests with coverage
uv run pytest tests/ --cov=alcatel_modem_api --cov-report=term-missing

# Or using Make
make test
```

### Code Quality Checks

```bash
# Run linter
uv run ruff check .

# Run type checker
uv run mypy alcatel_modem_api

# Format code
uv run ruff format .

# Run all checks
make check
```

## Adding Support for New Modems

If you have a new Alcatel modem model that uses the `/jrd/webapi` endpoint, we'd love to add support for it!

### Capturing Traffic for Analysis

To help us understand how your modem works, you can capture network traffic:

#### Using Wireshark

1. **Install Wireshark:**
   - Download from [wireshark.org](https://www.wireshark.org/download.html)

2. **Capture traffic:**
   - Open Wireshark
   - Select your network interface (usually Ethernet or Wi-Fi)
   - Start capturing
   - Access your modem's web interface and perform the actions you want to replicate
   - Stop capturing

3. **Filter HTTP traffic:**
   - In Wireshark, use filter: `http.host contains "192.168.1.1"` (replace with your modem IP)
   - Look for requests to `/jrd/webapi`

4. **Export relevant requests:**
   - Right-click on a request → Follow → HTTP Stream
   - Save the conversation for analysis

#### Using Browser Developer Tools

1. **Open Developer Tools:**
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I`
   - Firefox: Press `F12` or `Ctrl+Shift+I`

2. **Go to Network tab:**
   - Filter by "webapi" or "jrd"
   - Perform actions in the modem web interface

3. **Inspect requests:**
   - Click on a request to see headers, payload, and response
   - Look for:
     - `_TclRequestVerificationKey` or `_TclRequestVerificationToken` headers
     - Request payload structure
     - Response format

4. **Export for analysis:**
   - Right-click on request → Copy → Copy as cURL
   - Or use "Save all as HAR" to export all network traffic

### Testing Your Modem

1. **Run diagnostics:**
   ```bash
   alcatel doctor -u http://YOUR_MODEM_IP -p YOUR_PASSWORD
   ```

2. **Test basic functionality:**
   ```bash
   # Test connection (no password needed)
   alcatel system status -u http://YOUR_MODEM_IP
   
   # Test authentication
   alcatel system poll-extended -u http://YOUR_MODEM_IP -p YOUR_PASSWORD
   
   # Test SMS (if supported)
   alcatel sms list -u http://YOUR_MODEM_IP -p YOUR_PASSWORD
   ```

3. **Report your findings:**
   - Open an issue with the "New Modem Support" template
   - Include:
     - Modem model name
     - Firmware version
     - Test results from `alcatel doctor`
     - Any captured traffic (anonymized if needed)
     - Any differences you noticed from existing models

## Code Style

- Follow PEP 8 style guidelines
- Use `ruff` for linting and formatting (configuration in `pyproject.toml`)
- Maximum line length: 160 characters
- Use type hints for all functions
- Run `make format` before committing

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `refactor:` for code refactoring
- `test:` for adding or updating tests
- `chore:` for maintenance tasks

Example:
```
feat: add support for MW45V modem model
```

## Pull Request Process

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Run checks:**
   ```bash
   make check
   make test
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: your commit message"
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Questions?

If you have questions or need help, please:
- Open an issue on GitHub
- Check existing issues and discussions
- Review the README.md for usage examples

Thank you for contributing! 🎉

