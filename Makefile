.PHONY: install install-dev test lint format clean

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

# Clean build artifacts
clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache .mypy_cache .ruff_cache 2>/dev/null || true
	@rm -rf *.egg-info dist build 2>/dev/null || true

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
	@echo "  clean        - Clean build artifacts"
	@echo "  help         - Show this help message"

