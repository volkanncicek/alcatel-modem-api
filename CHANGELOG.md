# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-02

### 🚀 Initial Release - Modern Python API for Alcatel LTE Modems

First official release of the library with a modern, world-class architecture built from the ground up using 2025 Python standards.

### Added

- **Namespace-based API**: Clean, organized API structure
  - `client.sms.send()`, `client.sms.list()`, etc.
  - `client.network.get_info()`, `client.network.connect()`, etc.
  - `client.wlan.get_settings()`, `client.wlan.set_settings()`, etc.
  - `client.device.get_connected_list()`, `client.device.block()`, etc.
  - `client.system.get_status()`, `client.system.poll_basic_status()`, etc.

- **Async Support**: Full async/await support using `httpx.AsyncClient`
  - All endpoints have both sync and async methods
  - Example: `await client.sms.send_async(...)`

- **Pydantic Models**: Type-safe data models with validation
  - `SystemStatus`, `ExtendedStatus`, `NetworkInfo`, `ConnectionState`, `SMSMessage`
  - Automatic validation and type coercion
  - Better IDE autocompletion

- **Modern CLI**: Beautiful CLI built with Typer and Rich
  - Colored output, tables, and formatted JSON
  - Subcommands: `alcatel sms send`, `alcatel system status`, etc.
  - Auto-completion support

- **HTTP Client**: Built on `httpx` for modern HTTP operations
  - Better performance than traditional `requests` library
  - Native async support
  - Modern, type-safe API

- **HTTP Retry Logic**: Built-in retry with exponential backoff
  - Automatic retry on 429, 500, 502, 503, 504 errors
  - Configurable retry strategy

- **Improved Logging**: Proper logging instead of silent failures
  - Uses Python's `logging` module
  - Warning messages for non-critical errors

- **Modular Architecture**: Clean project structure
  - `endpoints/` directory for modular endpoints
  - `utils/` directory for utility functions
  - `client.py` for core HTTP client
  - `exceptions.py` for all exceptions
  - `models.py` with Pydantic models

- **CI/CD Pipeline**: GitHub Actions workflow
  - Test matrix: Python 3.9, 3.10, 3.11, 3.12
  - Ruff linting and formatting checks
  - MyPy strict type checking
  - Auto-publish to PyPI on release

- **Pre-commit Hooks**: Automated code quality checks
  - Ruff formatting and linting
  - Runs before every commit

- **Modern Dependencies**: Built on latest Python ecosystem
  - `httpx>=0.25.0` for HTTP operations
  - `pydantic>=2.0.0` for data validation
  - `typer>=0.9.0` for CLI
  - `rich>=13.0.0` for beautiful terminal output

