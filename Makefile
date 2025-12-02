.PHONY: install install-dev test lint format docs clean

# Install package in development mode
install:
	uv pip install -e .

# Install package with dev dependencies
install-dev:
	uv pip install -e ".[dev]"

# Run tests
test:
	uv run pytest tests/ --cov=alcatel_modem_api --cov-report=term-missing

# Run linter
lint:
	uv run ruff check .

# Run type checker
type-check:
	uv run mypy alcatel_modem_api

# Format code
format:
	uv run ruff format .

# Check formatting
format-check:
	uv run ruff format --check .

# Run all checks (lint + type-check + format-check)
check: lint type-check format-check

# Build documentation (if using mkdocs)
docs:
	@echo "Documentation is in README.md"
	@echo "To set up MkDocs, run: uv pip install mkdocs mkdocs-material mkdocstrings[python]"

# Clean build artifacts
clean:
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue __pycache__ .pytest_cache .mypy_cache .ruff_cache
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue alcatel_modem_api\__pycache__ alcatel_modem_api\**\__pycache__
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue tests\__pycache__
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue *.egg-info dist build

# Help target
help:
	@echo "Available targets:"
	@echo "  install      - Install package in development mode"
	@echo "  install-dev  - Install package with dev dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run linter"
	@echo "  type-check    - Run type checker"
	@echo "  format       - Format code"
	@echo "  format-check - Check code formatting"
	@echo "  check        - Run all checks (lint + type-check + format-check)"
	@echo "  docs         - Show documentation info"
	@echo "  clean        - Clean build artifacts"
	@echo "  help         - Show this help message"

